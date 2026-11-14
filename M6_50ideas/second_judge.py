#!/usr/bin/env python3
"""
second_judge.py: does the ranking of the representations depend on the paper's Claude judge?

  cd M6_50ideas
  GEN_MODEL=haiku python second_judge.py score  --judge deepseek/deepseek-v4.1-flash --host deepinfra/fp8
  GEN_MODEL=haiku python second_judge.py report --judge deepseek/deepseek-v4.1-flash
  GEN_MODEL=opus  python second_judge.py score  --judge deepseek/deepseek-v4.1-flash --host deepinfra/fp8 \
                  --sample-per-arm 25          # a random 25 requests per representation (judge_family_check.py)

`score` sends the ideas of one run (GEN_MODEL picks it) to a second judge from another model family, through
OpenRouter. Everything the judge sees is the paper's: the same system and user prompts, built by
score_ideas.py's functions, 5 consecutive ideas per request, effort medium, blind to model, condition and
position. Scores go to results[/<model>]/second_judge/<judge>/idea_scores.jsonl; the first judge's files are
not touched. Resumable; needs OPENROUTER_API_KEY.

`report` (no API calls) reads both judges' scores of the same ideas:

  agreement   correlation of the two scores, mean of each, agreement on "top idea" and Cohen's kappa
  yield       top ideas per 100k tokens per representation under each judge, with 95% bootstrap intervals,
              and the contrasts A - B, A - C, B - C. Judges differ in how generous they are, so the second
              judge's top ideas are counted twice: at the paper's cut-off (score >= 4.0) and at the cut-off
              that gives the number of top ideas closest to the first judge's ("matched")
  verdict     CHINESE_REPLICATION.md, Section 7: the ranking is judge-dependent if, under the second judge,
              the full graph is not below both the slice and no graph, or the interval of B - C is above 0

Writes results[/<model>]/second_judge/<judge>/report.md.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import score_ideas as si
from common import GEN_MODEL, RESULTS, RUNS, load_calls, parse_json

sys.path.insert(0, str(si.ROOT))
from top_ideas import IDEA_CRITERIA  # noqa: E402

CONDS = ["A", "B", "R", "C"]
REPS, TOP = 2000, 4.0


def folder(judge: str) -> Path:
    return RESULTS / "second_judge" / judge.replace("/", "_")


def latest(path: Path) -> dict:
    out = {}
    if path.exists():
        for line in path.open(encoding="utf-8"):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("ok"):
                out[(r["run_id"], r["start"])] = r
    return out


def score_of(rating) -> float | None:
    if not isinstance(rating, dict):
        return None
    vals = [rating.get(c) for c in IDEA_CRITERIA if isinstance(rating.get(c), (int, float))]
    return sum(vals) / len(vals) if len(vals) == len(IDEA_CRITERIA) else None


# ── score ───────────────────────────────────────────────────────────
def score_chunk(client, ch: dict, args) -> dict:
    rec = {"run_id": ch["run_id"], "start": ch["start"], "n": len(ch["ideas"]), "judge_model": args.judge,
           "host_pin": args.host, "ts": datetime.now(timezone.utc).isoformat()}
    body = {"reasoning": {"effort": args.effort}, "usage": {"include": True}}
    if args.host:
        body["provider"] = {"only": [args.host], "allow_fallbacks": False}
    t0 = time.perf_counter()
    try:
        resp = client.chat.completions.create(
            model=args.judge, max_tokens=args.max_tokens, extra_body=body,
            messages=[{"role": "system", "content": si.JUDGE_SYSTEM}, {"role": "user", "content": si.judge_prompt(ch)}])
        text = resp.choices[0].message.content or ""
        out = parse_json(text)
        ratings = out.get("ratings") if isinstance(out, dict) else None
        if not isinstance(ratings, list) or len(ratings) != len(ch["ideas"]) or any(score_of(r) is None for r in ratings):
            raise ValueError(f"expected {len(ch['ideas'])} complete ratings, got: {text[:200]}")
        u = resp.usage
        extra = getattr(u, "model_extra", None) or {}
        rec.update(ok=True, ratings=ratings, input_tokens=u.prompt_tokens, output_tokens=u.completion_tokens,
                   cost_usd_billed=extra.get("cost"), latency_s=round(time.perf_counter() - t0, 2),
                   stop_reason=resp.choices[0].finish_reason,
                   served_by=(getattr(resp, "model_extra", None) or {}).get("provider"))
    except Exception as exc:
        rec.update(ok=False, error=f"{type(exc).__name__}: {exc}")
    return rec


def sample(chunks: list[dict], calls: dict, n: int, seed: str) -> list[dict]:
    """n requests per representation, in a fixed random order: a larger n always contains a smaller one,
    so a second wave (e.g. 25, then 40) only adds requests. Only requests the first judge scored are drawn."""
    first = latest(RESULTS / "idea_scores.jsonl")
    by_arm = {}
    for ch in chunks:
        if (ch["run_id"], ch["start"]) in first:
            by_arm.setdefault(calls[ch["run_id"]]["condition"], []).append(ch)
    out = []
    for cond in sorted(by_arm):
        lst = sorted(by_arm[cond], key=lambda ch: (ch["run_id"], ch["start"]))
        random.Random(f"{seed}-{GEN_MODEL}-{cond}").shuffle(lst)
        out += lst[:n]
    return out


def cmd_score(args) -> None:
    calls = load_calls([RUNS])
    out = folder(args.judge) / "idea_scores.jsonl"
    done = set(latest(out))
    pool = si.chunks(calls)
    if args.sample_per_arm:
        pool = sample(pool, calls, args.sample_per_arm, args.seed)
    todo = [c for c in pool if (c["run_id"], c["start"]) not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(calls)} calls of the {GEN_MODEL} run; {len(todo)} requests to score with {args.judge}")
    if not todo:
        return
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("OPENROUTER_API_KEY is not set")
    import openai
    client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key, max_retries=3, timeout=600)
    out.parent.mkdir(parents=True, exist_ok=True)
    lock, n_ok, cost = threading.Lock(), 0, 0.0
    with out.open("a", encoding="utf-8") as fh, ThreadPoolExecutor(max_workers=args.workers) as pool:
        for i, f in enumerate(as_completed([pool.submit(score_chunk, client, c, args) for c in todo]), 1):
            rec = f.result()
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
            n_ok += bool(rec.get("ok"))
            cost += rec.get("cost_usd_billed") or 0
            if i % 25 == 0 or i == len(todo) or not rec.get("ok"):
                print(f"[{i}/{len(todo)}] ok {n_ok}, ${cost:.3f} so far" + ("" if rec.get("ok") else f"  {rec['error'][:110]}"))
    print("re-run the same command to retry any failures; then `report`")


# ── report ──────────────────────────────────────────────────────────
def ci(vals):
    v = sorted(vals)
    return v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]


def cmd_report(args) -> None:
    calls = load_calls([RUNS])
    first, second = latest(RESULTS / "idea_scores.jsonl"), latest(folder(args.judge) / "idea_scores.jsonl")
    if not second:
        sys.exit("no second-judge scores yet: run `score` first")
    ideas = []                                   # one row per idea rated by both judges
    for (run_id, start), rec in second.items():
        if (run_id, start) not in first or run_id not in calls:
            continue
        for k, (a, b) in enumerate(zip(first[(run_id, start)]["ratings"], rec["ratings"])):
            if score_of(a) is not None and score_of(b) is not None:
                ideas.append({"run_id": run_id, "cond": calls[run_id]["condition"], "s1": score_of(a), "s2": score_of(b),
                              "c1": a, "c2": b})
    n = len(ideas)
    total = sum(len(c.get("ideas") or []) for c in calls.values())
    n1 = sum(i["s1"] >= TOP for i in ideas)
    cuts = sorted({i["s2"] for i in ideas})
    matched = min(cuts, key=lambda c: abs(sum(i["s2"] >= c for i in ideas) - n1))
    by_run = {}
    for i in ideas:
        by_run.setdefault(i["run_id"], []).append(i)
    arms = {c: [{"tokens": (calls[r].get("input_tokens") or 0) + (calls[r].get("output_tokens") or 0), "ideas": v}
                for r, v in by_run.items() if calls[r]["condition"] == c] for c in CONDS}

    def yields(top) -> tuple[dict, dict]:
        point, boot = {}, {}
        for c in CONDS:
            y = lambda cs: 1e5 * sum(top(i) for x in cs for i in x["ideas"]) / sum(x["tokens"] for x in cs)
            rng = random.Random(f"second-{GEN_MODEL}-{c}")       # the same resamples for every definition of "top"
            point[c], boot[c] = y(arms[c]), [y([rng.choice(arms[c]) for _ in arms[c]]) for _ in range(REPS)]
        return point, boot

    views = [("First judge (Sonnet 5.5), score ≥ 4.0", lambda i: i["s1"] >= TOP),
             (f"Second judge, score ≥ 4.0", lambda i: i["s2"] >= TOP),
             (f"Second judge, matched cut-off (score ≥ {matched:g})", lambda i: i["s2"] >= matched)]
    m1, m2 = sum(i["s1"] for i in ideas) / n, sum(i["s2"] for i in ideas) / n
    sd = lambda k, m: (sum((i[k] - m) ** 2 for i in ideas) / n) ** 0.5
    r = sum((i["s1"] - m1) * (i["s2"] - m2) for i in ideas) / n / (sd("s1", m1) * sd("s2", m2))
    L = [f"# Second judge: {args.judge} on the {GEN_MODEL} run", "",
         f"{n:,} of the run's {total:,} ideas rated by both judges, with the same prompt. First judge: "
         f"`claude-sonnet-5-5` (the paper's scores). Second judge: `{args.judge}`.", "", "## Agreement", "",
         f"- Mean score: first judge {m1:.2f}, second judge {m2:.2f}. Correlation of the two scores: r = {r:.2f}.",
         "- Mean per criterion (first / second): " + ", ".join(
             f"{c} {sum(i['c1'][c] for i in ideas) / n:.2f} / {sum(i['c2'][c] for i in ideas) / n:.2f}" for c in IDEA_CRITERIA) + "."]
    for label, top in views[1:]:
        a = sum((i["s1"] >= TOP) == top(i) for i in ideas) / n
        p1, p2 = n1 / n, sum(top(i) for i in ideas) / n
        ch = p1 * p2 + (1 - p1) * (1 - p2)
        both = sum(i["s1"] >= TOP and top(i) for i in ideas)
        L.append(f"- {label}: {sum(top(i) for i in ideas)} top ideas ({100 * p2:.1f}%; first judge {n1}, {100 * p1:.1f}%); "
                 f"{both} are top for both; agreement {100 * a:.1f}%, kappa {(a - ch) / (1 - ch):.2f}.")
    L += ["", "## Yield per representation under each judge", "",
          "Top ideas per 100k tokens [95% CI], and contrasts (difference [95% CI]; ✱ = interval excludes 0).", "",
          "| Top ideas counted by | A full graph | B slice | R random | C no graph | A − B | A − C | B − C |",
          "|" + " --- |" * 8]
    verdicts = []
    for label, top in views:
        point, boot = yields(top)
        cells = [f"{point[c]:.1f} [{ci(boot[c])[0]:.1f}–{ci(boot[c])[1]:.1f}] (n={sum(top(i) for x in arms[c] for i in x['ideas'])})"
                 for c in CONDS]
        cons = {}
        for x, y in (("A", "B"), ("A", "C"), ("B", "C")):
            lo, hi = ci([a - b for a, b in zip(boot[x], boot[y])])
            cons[(x, y)] = (point[x] - point[y], lo, hi)
            cells.append(f"{point[x] - point[y]:+.1f} [{lo:+.1f}, {hi:+.1f}]" + (" ✱" if lo > 0 or hi < 0 else ""))
        L.append(f"| {label} | " + " | ".join(cells) + " |")
        if not label.startswith("First"):
            dependent = not (point["A"] < point["B"] and point["A"] < point["C"]) or cons[("B", "C")][1] > 0
            verdicts.append((label, dependent))
    L += ["", "## Verdict", ""]
    for label, dependent in verdicts:
        L.append(f"- {label}: the ranking is **{'JUDGE-DEPENDENT' if dependent else 'the same as under the first judge'}** "
                 f"({'the full graph is not below both the slice and no graph, or the slice beats no graph' if dependent else 'the full graph is below both the slice and no graph, and the slice does not beat no graph'}).")
    out = folder(args.judge) / "report.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"-> {out.relative_to(si.ROOT / 'M6_50ideas')}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["score", "report"])
    ap.add_argument("--judge", required=True, help="OpenRouter model id of the second judge")
    ap.add_argument("--host", default=None, help="pin the judge to this OpenRouter host endpoint (no fallback)")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--max-tokens", type=int, default=8000)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="score: at most this many requests (to measure the cost first)")
    ap.add_argument("--sample-per-arm", type=int, default=0,
                    help="score: only this many requests per representation, drawn at random (default: all)")
    ap.add_argument("--seed", default="family-check", help="seed of the random draw for --sample-per-arm")
    args = ap.parse_args()
    {"score": cmd_score, "report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    main()
