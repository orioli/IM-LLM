#!/usr/bin/env python3
"""
code_moves.py: code every new M6 idea into the codebook's moves, and check the coding by hand.

  code     the coder model assigns each idea a primary move (or NEW), blind (API calls, resumable)
             python code_moves.py code --dry-run      # plan + one example prompt, no API calls
             python code_moves.py code                # ideas not yet coded, and NEW ideas after a codebook update
             python code_moves.py code --all          # every idea not coded with the current codebook version
             python code_moves.py code --logs ../runs/rq1_full.jsonl   # the main study's 250 M6 ideas (5 per
                                                      # call): the reference that defines the "main 5" moves
  review   ideas coded NEW, with the coder's proposed move -> results/new_move_proposals.csv (no API)
  sample   blind sheet of ideas for human coding -> results/human_coding_sheet.csv (no API)
  agree    human vs coder agreement (Cohen's kappa) -> results/human_agreement.md (no API)

Blind coding. The coder sees each idea's title, new elements and rationale with graph node ids
removed. Ideas from all four conditions are shuffled together and sent in batches of 10, so a batch
never reveals which prompt its ideas came from, and nothing in a batch is shared by one condition.
review and sample show an opaque reference, never the run id (which contains the condition).

Codebook versions. Every code records the codebook version it was made with. Bump `version` in
codebook/codebook.yaml whenever moves or definitions change (adding the NEW proposals you accept,
merging, splitting); filling in prior art does not need a new version. After a bump, `code` recodes
the ideas that were NEW, and `code --all` recodes everything, which is the last step before analysis.

Output: results/moves.jsonl, one line per idea per coding; the last successful line for an idea wins.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from common import (CODER_MODEL, CONDITIONS, MOVES, NEED, RESULTS, RUNS, call_claude, fill, idea_records,
                    latest_codes, load_calls, load_codebook, load_prompt, need_label, parse_json, render_codebook,
                    render_ideas)

SHEET = RESULTS / "human_coding_sheet.csv"
SHEET_KEY = RESULTS / "human_coding_key.csv"


def ref(idea_id: str) -> str:
    """Opaque, stable reference for an idea (the run id would reveal the condition)."""
    return hashlib.sha1(idea_id.encode("utf-8")).hexdigest()[:8]


# ── CODE ────────────────────────────────────────────────────────────
def code_batch(batch: list[dict], batch_id: str, cb: dict, args, system: str, user_t: str) -> list[dict]:
    user = fill(user_t, {"need_id": NEED, "need_label": need_label(), "codebook": render_codebook(cb),
                         "ideas": render_ideas(batch), "n": len(batch)})
    base = {"codebook_version": cb["version"], "codebook_sha256": cb["sha256"], "coder_model": args.model,
            "coder_effort": args.effort, "batch_id": batch_id, "ts": datetime.now(timezone.utc).isoformat()}
    try:
        text, usage = call_claude(system, user, args.model, args.effort, args.max_tokens)
    except Exception as exc:                                 # logged, not raised: the run continues
        return [{"idea_id": it["idea_id"], **base, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
                for it in batch]
    data = parse_json(text)
    codes = data.get("codes") if isinstance(data, dict) else None
    if not isinstance(codes, list) or len(codes) != len(batch):
        return [{"idea_id": it["idea_id"], **base, **usage, "ok": False,
                 "error": f"expected {len(batch)} codes, got: {text[:200]}"} for it in batch]
    nums = [c.get("idea") for c in codes if isinstance(c, dict)]
    if sorted(nums) == list(range(1, len(batch) + 1)):           # trust the numbers over the order
        codes = sorted(codes, key=lambda c: c["idea"])
    out = []
    for it, c in zip(batch, codes):
        rec = {"idea_id": it["idea_id"], **base, **usage}
        if not isinstance(c, dict):
            out.append({**rec, "ok": False, "error": f"not a code: {c!r}"[:200]})
            continue
        primary = str(c.get("primary", "")).strip().upper()
        if primary != "NEW" and primary not in cb["by_id"]:
            out.append({**rec, "ok": False, "error": f"unknown move id {primary!r}"})
            continue
        secondary = []
        for s in (c.get("secondary") or []):
            s = str(s).strip().upper()
            if s in cb["by_id"] and s != primary and s not in secondary:
                secondary.append(s)
        new = c.get("new_move") if primary == "NEW" else None
        if primary == "NEW" and not isinstance(new, dict):
            new = {}
        conf = c.get("confidence")
        out.append({**rec, "ok": True, "primary": primary, "secondary": secondary[:2],
                    "confidence": conf if conf in (1, 2, 3) else None, "new_move": new})
    return out


def cmd_code(args) -> None:
    cb = load_codebook()
    ideas = idea_records(load_calls(args.logs))
    if not ideas:
        sys.exit(f"No {NEED} ideas in {args.logs}")
    codes = latest_codes()

    def todo(i):
        c = codes.get(i["idea_id"])
        if c is None:
            return True
        if c["codebook_version"] == cb["version"]:
            return False
        return args.all or c["primary"] == "NEW"

    pending = [i for i in ideas if todo(i)]
    random.Random(f"{args.seed}-{cb['version']}").shuffle(pending)       # conditions mixed in every batch
    batches = [pending[i:i + args.batch] for i in range(0, len(pending), args.batch)]
    system, user_t = load_prompt("code_moves.txt")
    print(f"{len(ideas)} ideas; codebook v{cb['version']} ({len(cb['moves'])} moves); "
          f"{len(pending)} to code in {len(batches)} batches of up to {args.batch} with {args.model}")
    if args.dry_run:
        if batches:
            ex = fill(user_t, {"need_id": NEED, "need_label": need_label(), "codebook": render_codebook(cb),
                               "ideas": render_ideas(batches[0]), "n": len(batches[0])})
            RESULTS.mkdir(exist_ok=True)
            out = RESULTS / "code_prompt_example.txt"
            out.write_text(f"=== SYSTEM ===\n{system}\n\n=== USER ===\n{ex}\n", encoding="utf-8")
            print(f"example prompt (~{round(len(system + ex) / 3.5):,} tokens) -> {out}")
        return
    if not batches:
        return
    RESULTS.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    lock, n_ok, n_bad = threading.Lock(), 0, 0
    with MOVES.open("a", encoding="utf-8") as fh, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(code_batch, b, f"v{cb['version']}-{stamp}-{n:03d}", cb, args, system, user_t)
                for n, b in enumerate(batches, 1)]
        for n, f in enumerate(as_completed(futs), 1):
            recs = f.result()
            with lock:
                for r in recs:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                fh.flush()
            ok = sum(r["ok"] for r in recs)
            n_ok, n_bad = n_ok + ok, n_bad + len(recs) - ok
            new = sum(r.get("primary") == "NEW" for r in recs)
            print(f"[{n}/{len(batches)}] {ok}/{len(recs)} coded, {new} NEW"
                  + ("" if ok == len(recs) else f"  ({next(r['error'] for r in recs if not r['ok'])[:70]})"))
    print(f"done: {n_ok} coded, {n_bad} failed (re-run the same command to retry failures)")
    status(cb)


def status(cb: dict) -> None:
    codes = latest_codes()
    cur = [c for c in codes.values() if c["codebook_version"] == cb["version"]]
    new = sum(c["primary"] == "NEW" for c in cur)
    print(f"status: {len(codes)} ideas coded, {len(cur)} with v{cb['version']}, {new} of those NEW"
          + (" -> run `review`" if new else ""))


# ── REVIEW ──────────────────────────────────────────────────────────
def norm(label: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", str(label).lower()).strip()


def cmd_review(args) -> None:
    cb = load_codebook()
    ideas = {i["idea_id"]: i for i in idea_records(load_calls(args.logs))}
    codes = latest_codes()
    news = [(iid, c) for iid, c in codes.items() if c["primary"] == "NEW" and iid in ideas]
    news.sort(key=lambda x: norm((x[1].get("new_move") or {}).get("label", "")))
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / "new_move_proposals.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["ref", "codebook_version", "proposed_label", "replaces", "by", "definition",
                    "title", "new_elements", "rationale", "decision (add as MVxx / map to MVxx / leave)"])
        for iid, c in news:
            nm, it = c.get("new_move") or {}, ideas[iid]
            w.writerow([ref(iid), c["codebook_version"], nm.get("label", ""), nm.get("replaces", ""), nm.get("by", ""),
                        nm.get("definition", ""), it["title"], it["elements"], it["rationale"], ""])
    labels = Counter(norm((c.get("new_move") or {}).get("label", "")) for _, c in news)
    print(f"{len(news)} of {len(codes)} coded ideas are NEW -> {out}")
    if news:
        print("  most frequent proposed labels: " + "; ".join(f"{l or '(none)'} ×{n}" for l, n in labels.most_common(8)))
        print("  Add the real new moves to codebook/codebook.yaml (source: new_run), bump `version`, "
              "then run `code` again. Repeat until NEW is rare; then `code --all`.")
    status(cb)


# ── SAMPLE ──────────────────────────────────────────────────────────
def cmd_sample(args) -> None:
    if SHEET.exists() and not args.force:
        sys.exit(f"{SHEET} exists (it may hold your coding); pass --force to overwrite")
    cb = load_codebook()
    calls = load_calls(args.logs)
    codes = latest_codes()
    rng = random.Random(args.seed)
    picked = []
    for cond in CONDITIONS:
        pool = [i for i in idea_records(calls) if i["condition"] == cond and i["idea_id"] in codes]
        rng.shuffle(pool)
        picked += pool[:args.per_condition]
    rng.shuffle(picked)
    RESULTS.mkdir(exist_ok=True)
    with SHEET.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["key", "title", "new_elements", "rationale", "primary_move", "secondary_moves", "notes"])
        for n, it in enumerate(picked, 1):
            w.writerow([f"H{n:03d}", it["title"], it["elements"], it["rationale"], "", "", ""])
    with SHEET_KEY.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["key", "idea_id"])
        w.writerows([f"H{n:03d}", it["idea_id"]] for n, it in enumerate(picked, 1))
    guide = RESULTS / "codebook_for_coders.md"
    guide.write_text(f"# Codebook v{cb['version']}: {NEED}, {need_label()}\n\n"
                     "Fill `primary_move` with one id (or `NEW: short label`), `secondary_moves` with up to two ids "
                     "separated by commas. Do not look at results/moves.jsonl or the key file while coding.\n\n"
                     + "\n".join(f"- **{m['id']} {m['label']}** ({m['category']}): replaces {m.get('replaces') or '-'} "
                                 f"by {m.get('by') or '-'}. {' '.join(str(m['definition']).split())}"
                                 for m in cb["moves"]) + "\n", encoding="utf-8")
    print(f"{len(picked)} ideas ({args.per_condition} per condition, shuffled, blind) -> {SHEET}")
    print(f"codebook for the human coder -> {guide}; hidden key -> {SHEET_KEY}")


# ── AGREE ───────────────────────────────────────────────────────────
def kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    if not n:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb_ = Counter(a), Counter(b)
    pe = sum(ca[k] * cb_[k] for k in set(ca) | set(cb_)) / n / n
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def parse_human(primary: str, secondary: str) -> tuple[str, list[str]]:
    p = (primary or "").strip()
    p = "NEW" if p.upper().startswith("NEW") else p.upper()
    s = [x.strip().upper() for x in re.split(r"[,;\s]+", secondary or "") if x.strip()]
    return p, s


def cmd_agree(args) -> None:
    cb = load_codebook()
    sheet = Path(args.sheet)
    if not sheet.exists() or not SHEET_KEY.exists():
        sys.exit("No coded sheet; run `sample`, code it by hand, then `agree`.")
    with SHEET_KEY.open(encoding="utf-8") as fh:
        key = {r["key"]: r["idea_id"] for r in csv.DictReader(fh)}
    codes = latest_codes()
    with sheet.open(encoding="utf-8-sig") as fh:
        rows = [r for r in csv.DictReader(fh) if (r.get("primary_move") or "").strip()]
    pairs, dis = [], []
    for r in rows:
        iid = key.get(r["key"])
        c = codes.get(iid)
        if not c:
            continue
        hp, hs = parse_human(r["primary_move"], r.get("secondary_moves", ""))
        if hp != "NEW" and hp not in cb["by_id"]:
            print(f"  {r['key']}: unknown move {hp!r} in the sheet, skipped")
            continue
        pairs.append((r["key"], hp, hs, c["primary"], c.get("secondary") or [], r["title"]))
    if not pairs:
        sys.exit("No coded rows matched the key.")
    cat = lambda m: "new" if m == "NEW" else cb["by_id"][m]["category"]
    h, l = [p[1] for p in pairs], [p[3] for p in pairs]
    k_move, k_cat = kappa(h, l), kappa([cat(x) for x in h], [cat(x) for x in l])
    agree = sum(x == y for x, y in zip(h, l)) / len(pairs)
    jac = sum(len(({a} | set(b)) & ({c} | set(d))) / len({a, c} | set(b) | set(d))
              for _, a, b, c, d, _ in pairs) / len(pairs)
    rng = random.Random(1)
    boots = []
    for _ in range(1000):
        idx = [rng.randrange(len(pairs)) for _ in pairs]
        boots.append(kappa([h[i] for i in idx], [l[i] for i in idx]))
    boots.sort()
    lo, hi = boots[25], boots[974]
    verdict = "PASS" if k_move >= args.threshold else "FAIL: revise the definitions that cause disagreements, bump version, recode"
    for _, a, b, c, d, title in pairs:
        if a != c:
            dis.append({"title": title, "human": a, "human_label": cb["by_id"].get(a, {}).get("label", "NEW"),
                        "coder": c, "coder_label": cb["by_id"].get(c, {}).get("label", "NEW")})
    with (RESULTS / "human_disagreements.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["title", "human", "human_label", "coder", "coder_label"])
        w.writeheader()
        w.writerows(dis)
    confused = Counter(tuple(sorted((d["human"], d["coder"]))) for d in dis).most_common(10)
    md = [f"# Human vs coder agreement ({NEED}, codebook v{cb['version']})", "",
          f"- Ideas coded by both: {len(pairs)}",
          f"- Primary move: {agree:.0%} agreement, Cohen's kappa {k_move:.2f} (95% CI {lo:.2f}–{hi:.2f})",
          f"- Category of the primary move: kappa {k_cat:.2f}",
          f"- Overlap of all moves per idea (Jaccard, mean): {jac:.2f}",
          f"- Pre-set threshold: kappa ≥ {args.threshold} → **{verdict}**", "",
          "Most frequent disagreements (move pairs):", ""]
    md += [f"- {a} / {b}: {n}" for (a, b), n in confused] + ["", "All disagreements: results/human_disagreements.csv"]
    (RESULTS / "human_agreement.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("code", "review", "sample", "agree"):
        p = sub.add_parser(name)
        p.add_argument("--logs", nargs="+", type=Path, default=[RUNS])
    c = sub.choices["code"]
    c.add_argument("--all", action="store_true", help="recode every idea not coded with the current version")
    c.add_argument("--model", default=CODER_MODEL)
    c.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    c.add_argument("--max-tokens", type=int, default=16000)
    c.add_argument("--batch", type=int, default=10)
    c.add_argument("--workers", type=int, default=4)
    c.add_argument("--seed", type=int, default=6)
    c.add_argument("--dry-run", action="store_true")
    s = sub.choices["sample"]
    s.add_argument("--per-condition", type=int, default=25)
    s.add_argument("--seed", type=int, default=11)
    s.add_argument("--force", action="store_true")
    a = sub.choices["agree"]
    a.add_argument("--sheet", default=str(SHEET))
    a.add_argument("--threshold", type=float, default=0.6)
    args = ap.parse_args()
    {"code": cmd_code, "review": cmd_review, "sample": cmd_sample, "agree": cmd_agree}[args.cmd](args)


if __name__ == "__main__":
    main()
