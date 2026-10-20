#!/usr/bin/env python3
"""
discovery_analysis.py: when the model is asked for 50 ideas at once, does the graph change how many
different ideas (moves) it finds, how long it stays on the need, and whether it gets past the "main 5"?
(no API calls)

  cd M6_50ideas
  python discovery_analysis.py      # after score_ideas.py table and code_moves.py (both logs coded)

Unit: one call (one list of ideas). Position = the idea's place in the list. The model does not
return exactly 50 ideas (it returned 44-60), so every list is cut to its first K ideas, K = the
shortest list (or --positions), and all per-call measures use those K ideas.
Per condition (A full graph, B need slice, R random slice, C no graph):
  distinct moves per call          how many different moves one 50-idea list contains          [H12, H13]
  distinct moves per 100k tokens   the same, per token (the prompt, plus the output in proportion to the K
                                   ideas kept)
  within-call curve                distinct moves after the first p ideas, p = 1..K
  by position band (1-5, 6-10, 11-20, ..., 41-K): share of ideas that add a move not yet in the list,
                                   mean score, on-need share (judge relevance >= 4)             [H14]
  main-5 share                     ideas whose move is one of the 5 moves most often found by the main
                                   study's 5-idea M6 calls; positions 1-5 vs 6-K                [H15]
  pooled over calls                moves found, Chao2 estimate (± 1.96 bootstrap SE), coverage
  distinct top moves per call      moves with an idea scoring >= 4.0 (the main study's threshold)

95% CIs: 2,000 bootstrap resamples of calls within each condition (percentile intervals; Chao2 uses the
estimate ± 1.96 SE). A hypothesis is supported only if the CI of its pre-registered difference is above 0.
Writes results/discovery_summary.{md,csv}, discovery_by_position.csv, discovery_tests.csv,
move_incidence.csv and results/charts/m6_within_call.png, m6_by_position.png, m6_incidence.png.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from common import (COND_NAME, CONDITIONS, N_IDEAS, NEED, REF_LOGS, RESULTS, ROOT, RUNS, latest_codes, load_calls,
                    load_codebook, need_label)

sys.path.insert(0, str(ROOT))                      # the main study's chart palette
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from charts import AXIS, COND, GRID, INK, INK2, MUTED, SURFACE  # noqa: E402

TOP, ON_NEED = 4.0, 4                 # top idea: mean score >= 4.0; on need: relevance >= 4
MAIN_K = 5
K = N_IDEAS                           # positions analysed per list; set_length() makes it the shortest list
BANDS, LATE, REST = [], (26, N_IDEAS), (6, N_IDEAS)


def set_length(k: int) -> None:
    """Cut every list to its first k ideas: the position bands, H14's second half and H15's 6-k follow."""
    global K, BANDS, LATE, REST
    K = k
    edges = [(1, 5), (6, 10), (11, 20), (21, 30), (31, 40), (41, 50)]
    BANDS = [(lo, min(hi, k)) for lo, hi in edges if lo <= k]
    if k > 50:
        BANDS[-1] = (41, k)
    LATE, REST = (26, k), (6, k)
OUT = RESULTS / "charts"


# ── Loading ─────────────────────────────────────────────────────────
def load_scores(path: Path) -> dict:
    out = {}
    if path.exists():
        with path.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                try:
                    out[r["idea_id"]] = (float(r["score"]), float(r["relevance"]))
                except (KeyError, TypeError, ValueError):
                    pass
    return out


def build_calls(logs, effort, codes, scores, cb, allow_new, problems):
    calls = {k: c for k, c in load_calls(logs).items()
             if c.get("target_need") == NEED and c.get("effort") == effort and c.get("ideas")}
    out = {a: [] for a in CONDITIONS}
    uncoded = unresolved = 0
    for run_id, c in calls.items():
        ideas = []
        for k, _ in enumerate(c["ideas"], 1):
            iid = f"{run_id}#{k}"
            code = codes.get(iid)
            if code is None:
                uncoded += 1
                continue
            p = code["primary"]
            if p == "NEW":
                unresolved += 1
                p = f"NEW:{iid}"
            sc = scores.get(iid)
            ideas.append({"pos": k, "move": p, "score": sc[0] if sc else None, "rel": sc[1] if sc else None})
        out.setdefault(c["condition"], []).append({"input": c.get("input_tokens") or 0, "output": c.get("output_tokens") or 0,
                                                   "ideas": ideas, "listed": len(c["ideas"])})
    if uncoded:
        problems.append(f"{uncoded} ideas in {', '.join(map(str, logs))} have no code")
    if unresolved and not allow_new:
        problems.append(f"{unresolved} ideas are still NEW (review, update the codebook, recode)")
    return {a: v for a, v in out.items() if v}


# ── Per-call measures ───────────────────────────────────────────────
def per_call(call, cat, echo, main5):
    ideas = sorted((i for i in call["ideas"] if i["pos"] <= K), key=lambda i: i["pos"])
    seen, curve, new_flags = set(), [], []
    for it in ideas:
        new_flags.append(it["move"] not in seen)
        seen.add(it["move"])
        curve.append(len(seen))
    curve = (curve + [curve[-1] if curve else 0] * K)[:K]
    top_moves = {i["move"] for i in ideas if i["score"] is not None and i["score"] >= TOP}
    band = {}
    for lo, hi in BANDS + [LATE, (1, 5), REST]:
        sel = [(i, f) for i, f in zip(ideas, new_flags) if lo <= i["pos"] <= hi]
        scored = [i for i, _ in sel if i["score"] is not None]
        band[(lo, hi)] = {"n": len(sel), "new": sum(f for _, f in sel),
                          "main5": sum(i["move"] in main5 for i, _ in sel),
                          "n_scored": len(scored), "score_sum": sum(i["score"] for i in scored),
                          "on_need": sum(i["rel"] >= ON_NEED for i in scored),
                          "top": sum(i["score"] >= TOP for i in scored)}
    # tokens spent on the first K ideas: the whole prompt, plus the output in proportion to the ideas kept
    spent = call["input"] + call["output"] * min(K, call["listed"]) / max(call["listed"], 1)
    return {"tokens": spent, "n": len(ideas), "distinct": len(seen), "top_distinct": len(top_moves),
            "curve": np.array(curve, dtype=float), "moves": seen,
            "nontech": sum(cat.get(i["move"], "unknown") not in ("technology", "unknown") for i in ideas),
            "echo": sum(bool(echo.get(i["move"])) for i in ideas), "band": band}


def chao2(y: np.ndarray, m: int):
    s_obs = int((y > 0).sum())
    q1, q2 = int((y == 1).sum()), int((y == 2).sum())
    q0 = (m - 1) / m * q1 * (q1 - 1) / (2 * (q2 + 1)) if m > 1 else 0.0
    u = int(y.sum())
    cov = float("nan") if u == 0 else (1.0 if q1 == 0 else 1 - q1 / u * ((m - 1) * q1 / ((m - 1) * q1 + 2 * q2)))
    return s_obs, s_obs + q0, cov


def ci(v):
    v = np.asarray([x for x in v if x is not None and x == x], dtype=float)
    return (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) if len(v) else (float("nan"),) * 2


def se_ci(est, v):
    v = np.asarray([x for x in v if x is not None and x == x], dtype=float)
    if len(v) < 2:
        return float("nan"), float("nan")
    se = float(v.std(ddof=1))
    return est - 1.96 * se, est + 1.96 * se


def ratio(num, den):
    return num / den if den else float("nan")


# ── Main ────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--logs", nargs="+", type=Path, default=[RUNS])
    ap.add_argument("--ref-logs", nargs="+", type=Path, default=REF_LOGS,
                    help="the main study's logs: its 5-idea M6 calls define the main 5 moves")
    ap.add_argument("--scores", type=Path, default=RESULTS / "ideas_scored.csv")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--positions", type=int, default=None,
                    help="cut every list to its first N ideas (default: the shortest list)")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--allow-new", action="store_true", help="count unresolved NEW codes as moves of their own")
    ap.add_argument("--allow-stale", action="store_true", help="accept codes from older codebook versions")
    args = ap.parse_args()

    cb = load_codebook()
    codes = latest_codes()
    problems = []
    stale = sum(c["codebook_version"] != cb["version"] for c in codes.values())
    if stale and not args.allow_stale:
        problems.append(f"{stale} codes were made with an older codebook version (code_moves.py code --all)")
    scores = load_scores(args.scores)
    if not scores:
        print(f"note: no scores in {args.scores}; run score_ideas.py score and table (H14 and top moves skipped)")
    arms = build_calls(args.logs, args.effort, codes, scores, cb, args.allow_new, problems)
    # the main study's 5-idea M6 calls (any effort): the reference for the main 5 moves
    ref = {k: c for k, c in load_calls(args.ref_logs).items() if c.get("target_need") == NEED and c.get("ideas")}
    ref_codes = {f"{rid}#{k}": codes.get(f"{rid}#{k}") for rid, c in ref.items() for k in range(1, len(c["ideas"]) + 1)}
    ref_missing = sum(v is None for v in ref_codes.values())
    if problems:
        sys.exit("Not ready for analysis:\n  " + "\n  ".join(problems)
                 + "\n(--allow-new / --allow-stale override, for a preliminary look only)")
    listed = [c["listed"] for a in arms.values() for c in a]
    if not listed:
        sys.exit(f"No {NEED} calls at effort {args.effort} in {args.logs}")
    set_length(args.positions or min(listed))
    args.listed = (min(listed), max(listed))
    print(f"lists of {min(listed)}–{max(listed)} ideas; each cut to its first {K}")
    ref_counts = Counter()
    for rid, c in ref.items():
        ref_counts.update({codes[f"{rid}#{k}"]["primary"] for k in range(1, len(c["ideas"]) + 1)
                           if codes.get(f"{rid}#{k}") and codes[f"{rid}#{k}"]["primary"] != "NEW"})
    main5 = [m for m, _ in sorted(ref_counts.items(), key=lambda x: (-x[1], x[0]))[:MAIN_K]]
    if ref_missing:
        print(f"note: {ref_missing} of the main study's {len(ref_codes)} M6 ideas are not coded; "
              f"code them for the main-5 reference: python code_moves.py code --logs ../runs/rq1_full.jsonl")

    cat = {m["id"]: m["category"] for m in cb["moves"]}
    echo = {m["id"]: bool(m.get("worked_example_echo")) for m in cb["moves"]}
    order = [a for a in CONDITIONS if a in arms]
    pc = {a: [per_call(c, cat, echo, set(main5)) for c in arms[a]] for a in order}
    all_moves = sorted({m for a in order for c in pc[a] for m in c["moves"]})
    col = {m: j for j, m in enumerate(all_moves)}
    inc = {a: np.zeros((len(pc[a]), len(all_moves)), dtype=bool) for a in order}
    for a in order:
        for i, c in enumerate(pc[a]):
            for m in c["moves"]:
                inc[a][i, col[m]] = True

    def stats(a, idx=None):
        cs = pc[a] if idx is None else [pc[a][i] for i in idx]
        y = (inc[a] if idx is None else inc[a][idx]).sum(axis=0)
        s_obs, c2, cov = chao2(y, len(cs))
        b = lambda key, field: sum(c["band"][key][field] for c in cs)
        out = {"distinct": np.mean([c["distinct"] for c in cs]),
               "per100k": np.mean([1e5 * c["distinct"] / c["tokens"] for c in cs]),
               "top_distinct": np.mean([c["top_distinct"] for c in cs]),
               "tokens": np.mean([c["tokens"] for c in cs]), "n": np.mean([c["n"] for c in cs]),
               "curve": np.mean([c["curve"] for c in cs], axis=0),
               "nontech": ratio(sum(c["nontech"] for c in cs), sum(c["n"] for c in cs)),
               "echo": ratio(sum(c["echo"] for c in cs), sum(c["n"] for c in cs)),
               "s_obs": s_obs, "chao2": c2, "coverage": cov, "y": y, "band": {}}
        for key in BANDS + [LATE, (1, 5), REST]:
            out["band"][key] = {"new": ratio(b(key, "new"), b(key, "n")), "main5": ratio(b(key, "main5"), b(key, "n")),
                                "score": ratio(b(key, "score_sum"), b(key, "n_scored")),
                                "on_need": ratio(b(key, "on_need"), b(key, "n_scored")),
                                "top": ratio(b(key, "top"), b(key, "n_scored")),
                                "h": (b(key, "main5"), b(key, "n"))}
        return out

    rng = np.random.default_rng(args.seed)
    obs = {a: stats(a) for a in order}
    boots = {a: [stats(a, rng.integers(0, len(pc[a]), len(pc[a]))) for _ in range(args.boot)] for a in order}
    scored = bool(scores)

    # ── summary rows
    rows = []
    for a in order:
        o, bs = obs[a], boots[a]
        r = {"condition": a, "name": COND_NAME[a], "calls": len(pc[a]), "ideas_per_call": round(o["n"], 1),
             "tokens_per_call": round(o["tokens"])}
        for key, label in (("distinct", "distinct_moves_per_call"), ("per100k", "distinct_moves_per_100k_tokens")):
            lo, hi = ci([x[key] for x in bs])
            r.update({label: round(float(o[key]), 2), f"{label}_ci": f"{lo:.1f}–{hi:.1f}"})
        lo, hi = se_ci(o["chao2"], [x["chao2"] for x in bs])
        r.update(moves_found_all_calls=o["s_obs"], chao2=round(o["chao2"], 1), chao2_ci=f"{lo:.1f}–{hi:.1f}",
                 coverage=round(o["coverage"], 2), nontech_share=round(o["nontech"], 3), echo_share=round(o["echo"], 3))
        if scored:
            lo, hi = ci([x["top_distinct"] for x in bs])
            late = o["band"][LATE]["on_need"]
            llo, lhi = ci([x["band"][LATE]["on_need"] for x in bs])
            r.update(top_moves_per_call=round(float(o["top_distinct"]), 2), top_moves_per_call_ci=f"{lo:.1f}–{hi:.1f}",
                     on_need_share_late=round(late, 3), on_need_share_late_ci=f"{llo:.2f}–{lhi:.2f}")
        if main5:
            r.update(main5_share_1_5=round(o["band"][(1, 5)]["main5"], 3),
                     main5_share_rest=round(o["band"][REST]["main5"], 3))
        rows.append(r)

    pos_rows = []
    for a in order:
        for key in BANDS:
            bnd = obs[a]["band"][key]
            pos_rows.append({"condition": a, "positions": f"{key[0]}-{key[1]}", "new_move_share": round(bnd["new"], 3),
                             "main5_share": round(bnd["main5"], 3) if main5 else "",
                             "mean_score": round(bnd["score"], 2) if scored else "",
                             "on_need_share": round(bnd["on_need"], 3) if scored else "",
                             "top_share": round(bnd["top"], 3) if scored else ""})

    # ── tests
    tests = []

    def add(h, text, f, a, b, counts=False):
        if a not in obs or b not in obs:
            tests.append({"hypothesis": h, "comparison": text, "estimate": "", "ci": "", "result": "not run"})
            return
        est = f(obs[a]) - f(obs[b])
        draws = [f(x) - f(y) for x, y in zip(boots[a], boots[b])]
        lo, hi = se_ci(est, draws) if counts else ci(draws)
        tests.append({"hypothesis": h, "comparison": text, "estimate": round(float(est), 3),
                      "ci": f"{lo:.3f} to {hi:.3f}", "result": "supported" if lo > 0 else "not supported"})

    add("H12", "distinct moves per call: A − B", lambda s: s["distinct"], "A", "B")
    add("H13", "distinct moves per call: B − C", lambda s: s["distinct"], "B", "C")
    if scored:
        add("H14a", f"on-need share, ideas 26–{K}: B − A", lambda s: s["band"][LATE]["on_need"], "B", "A")
        add("H14b", f"on-need share, ideas 26–{K}: B − C", lambda s: s["band"][LATE]["on_need"], "B", "C")
    if main5:
        def pooled(states):
            h1 = sum(s["band"][(1, 5)]["h"][0] for s in states)
            n1 = sum(s["band"][(1, 5)]["h"][1] for s in states)
            h2 = sum(s["band"][REST]["h"][0] for s in states)
            n2 = sum(s["band"][REST]["h"][1] for s in states)
            return ratio(h1, n1) - ratio(h2, n2)
        est = pooled([obs[a] for a in order])
        lo, hi = ci([pooled([boots[a][i] for a in order]) for i in range(args.boot)])
        tests.append({"hypothesis": "H15", "comparison": f"main-5 share: ideas 1–5 − ideas 6–{K} (all conditions)",
                      "estimate": round(est, 3), "ci": f"{lo:.3f} to {hi:.3f}",
                      "result": "supported" if lo > 0 else "not supported"})
    add("descriptive", "distinct moves per call: B − R", lambda s: s["distinct"], "B", "R")
    add("descriptive", "distinct moves per call: A − C", lambda s: s["distinct"], "A", "C")
    add("descriptive", "distinct moves per 100k tokens: B − A", lambda s: s["per100k"], "B", "A")
    add("descriptive", "Chao2 over all calls: A − B", lambda s: s["chao2"], "A", "B", counts=True)

    # ── move × condition incidence (calls containing the move), with the main study for reference
    ref_calls_with = Counter()
    for rid, c in ref.items():
        ref_calls_with.update({codes[f"{rid}#{k}"]["primary"] for k in range(1, len(c["ideas"]) + 1)
                               if codes.get(f"{rid}#{k}")})
    info = lambda m: cb["by_id"].get(m, {"label": "unresolved NEW", "category": "unknown", "prior_art": "unchecked"})
    tot = sum(obs[a]["y"] for a in order)
    inc_rows = []
    for j in np.argsort(-tot, kind="stable"):
        m = all_moves[j]
        r = {"move": m, "label": info(m).get("label", ""), "category": info(m).get("category", ""),
             "prior_art": info(m).get("prior_art", "unchecked"), "main5": m in main5,
             **{f"calls_{a}": int(obs[a]["y"][j]) for a in order}, "calls_main_study_5idea": ref_calls_with.get(m, 0)}
        inc_rows.append(r)

    RESULTS.mkdir(exist_ok=True)
    write_csv(RESULTS / "discovery_summary.csv", rows)
    write_csv(RESULTS / "discovery_by_position.csv", pos_rows)
    write_csv(RESULTS / "discovery_tests.csv", tests)
    write_csv(RESULTS / "move_incidence.csv", inc_rows)
    report(rows, pos_rows, tests, inc_rows, order, cb, main5, len(ref), scored, args)
    OUT.mkdir(parents=True, exist_ok=True)
    chart_within_call(order, obs, boots)
    chart_by_position(order, obs, scored, bool(main5))
    chart_incidence(order, inc_rows, len(ref))
    for t in tests:
        print(f"  {t['hypothesis']:<12} {t['comparison']:<56} {t['estimate']!s:>8}  [{t['ci']}]  {t['result']}")
    print("-> results/discovery_summary.md (+ .csv), discovery_by_position.csv, discovery_tests.csv, "
          "move_incidence.csv, charts/m6_*.png")


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def report(rows, pos_rows, tests, inc_rows, order, cb, main5, n_ref, scored, args):
    md = [f"# {NEED} ({need_label()}): {N_IDEAS} ideas asked for per call", "",
          f"The model returned {args.listed[0]}–{args.listed[1]} ideas per call; every list is cut to its first "
          f"{K} ideas (the shortest list), and all per-call measures use those.", "",
          f"Effort {args.effort}; codebook v{cb['version']} ({len(cb['moves'])} moves). 95% CIs from {args.boot:,} "
          "bootstrap resamples of calls within condition.", "",
          "## Per condition", "",
          f"| Condition | Calls | Tokens per list (first {K} ideas) | Distinct moves per list [95% CI] | per 100k tokens | "
          "Moves over all calls | Chao2 [95% CI] | Coverage |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        md.append(f"| {r['name']} | {r['calls']} | {r['tokens_per_call']:,} | {r['distinct_moves_per_call']} "
                  f"[{r['distinct_moves_per_call_ci']}] | {r['distinct_moves_per_100k_tokens']} | "
                  f"{r['moves_found_all_calls']} | {r['chao2']} [{r['chao2_ci']}] | {r['coverage']} |")
    if scored:
        md += ["", f"| Condition | Top moves per call [95% CI] | On-need share, ideas 26–{K} [95% CI] | "
               "Non-tech share | Echo share |", "| --- | --- | --- | --- | --- |"]
        md += [f"| {r['name']} | {r['top_moves_per_call']} [{r['top_moves_per_call_ci']}] | "
               f"{r['on_need_share_late']:.2f} [{r['on_need_share_late_ci']}] | {r['nontech_share']:.2f} | "
               f"{r['echo_share']:.2f} |" for r in rows]
    md += ["", "## By position in the list", "",
           "Share of ideas that add a move not yet in the same list"
           + (", mean score and on-need share" if scored else "") + ":", "",
           "| Condition | " + " | ".join(f"{lo}–{hi}" for lo, hi in BANDS) + " |", "| --- |" + " --- |" * len(BANDS)]
    for a in order:
        cells = []
        for lo, hi in BANDS:
            p = next(x for x in pos_rows if x["condition"] == a and x["positions"] == f"{lo}-{hi}")
            cells.append(f"{p['new_move_share']:.2f}" + (f" · {p['mean_score']:.2f} · {p['on_need_share']:.2f}"
                                                          if scored else ""))
        md.append(f"| {COND_NAME[a]} | " + " | ".join(cells) + " |")
    if main5:
        md += ["", f"## The main {MAIN_K} moves", "",
               f"The {MAIN_K} moves found in the most of the main study's {n_ref} five-idea {NEED} calls:", ""]
        md += [f"- {m} {cb['by_id'].get(m, {}).get('label', '')}" for m in main5]
        md += ["", f"| Condition | Main-5 share, ideas 1–5 | Main-5 share, ideas 6–{K} |", "| --- | --- | --- |"]
        md += [f"| {r['name']} | {r['main5_share_1_5']:.2f} | {r['main5_share_rest']:.2f} |" for r in rows]
    md += ["", "## Hypotheses (pre-registered in README.md)", "", "| | Comparison | Estimate | 95% CI | Result |",
           "| --- | --- | --- | --- | --- |"]
    md += [f"| {t['hypothesis']} | {t['comparison']} | {t['estimate']} | {t['ci']} | {t['result']} |" for t in tests]
    md += ["", "## Most frequent moves", "",
           "| Move | Category | Prior art | " + " | ".join(order) + " | Main study (5 ideas) |",
           "| --- | --- | --- |" + " --- |" * (len(order) + 1)]
    md += [f"| {r['move']} {r['label']}{' (main 5)' if r['main5'] else ''} | {r['category']} | {r['prior_art']} | "
           + " | ".join(str(r[f'calls_{a}']) for a in order) + f" | {r['calls_main_study_5idea']} |"
           for r in inc_rows[:20]]
    md += ["", "Cells: number of calls whose list contains the move (as a primary move). "
           "Full list: results/move_incidence.csv."]
    (RESULTS / "discovery_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")


# ── Charts ──────────────────────────────────────────────────────────
def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def chart_within_call(order, obs, boots):
    fig, ax = plt.subplots(figsize=(6.4, 4.2), facecolor=SURFACE)
    style(ax)
    x = np.arange(1, K + 1)
    ax.plot(x, x, color=MUTED, linewidth=0.9, linestyle=(0, (3, 2)), label="every idea a new move")
    for a in order:
        curves = np.array([b["curve"] for b in boots[a]])
        lo, hi = np.percentile(curves, 2.5, axis=0), np.percentile(curves, 97.5, axis=0)
        ax.fill_between(x, lo, hi, color=COND[a], alpha=0.15, linewidth=0)
        ax.plot(x, obs[a]["curve"], color=COND[a], linewidth=1.8, label=COND_NAME[a])
    ax.set_ylim(0, max(float(np.max([obs[a]["curve"] for a in order])) * 1.25, 10))
    ax.set_xlim(0, K + 1)
    ax.axvline(5, color=MUTED, linewidth=0.9, linestyle=":")
    ax.text(5.6, 0.97, "the main study\nasked for 5", color=MUTED, fontsize=7, va="top",
            transform=ax.get_xaxis_transform())
    ax.set_xlabel("position in the list of ideas", fontsize=8, color=INK2)
    ax.set_ylabel("distinct moves so far (mean per call)", fontsize=8, color=INK2)
    ax.set_title(f"{NEED}: distinct moves within one list (first {K} ideas)", fontsize=10, color=INK, loc="left")
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    fig.text(0.01, 0.005, "Band: 95% bootstrap interval over calls.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(OUT / "m6_within_call.png", dpi=200)
    plt.close(fig)


def chart_by_position(order, obs, scored, has_main5):
    panels = [("new", "Ideas that add a new move")]
    if scored:
        panels.append(("on_need", "On-need ideas (relevance ≥ 4)"))
    if has_main5:
        panels.append(("main5", f"Ideas whose move is one of the main {MAIN_K}"))
    fig, axes = plt.subplots(1, len(panels), figsize=(4.2 * len(panels), 3.6), facecolor=SURFACE, squeeze=False)
    mids = [(lo + hi) / 2 for lo, hi in BANDS]
    for ax, (key, title) in zip(axes[0], panels):
        style(ax)
        for a in order:
            ax.plot(mids, [obs[a]["band"][b][key] for b in BANDS], color=COND[a], marker="o", ms=3.5, linewidth=1.5,
                    label=COND_NAME[a])
        ax.set_ylim(0, 1.02)
        ax.set_xticks(mids)
        ax.set_xticklabels([f"{lo}–{hi}" for lo, hi in BANDS], fontsize=7)
        ax.set_xlabel("positions in the list", fontsize=8, color=INK2)
        ax.set_title(title, fontsize=9, color=INK, loc="left")
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    axes[0][0].legend(fontsize=7, frameon=False, loc="upper right")
    fig.suptitle(f"{NEED}: what changes further down the list (first {K} ideas)", fontsize=10, color=INK, x=0.01,
                 ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT / "m6_by_position.png", dpi=200)
    plt.close(fig)


def chart_incidence(order, inc_rows, n_ref):
    rows = [r for r in inc_rows if sum(r[f"calls_{a}"] for a in order) > 0]
    n = len(rows)
    cols = order + ["ref"]
    fig, ax = plt.subplots(figsize=(7.0, max(2.6, 0.22 * n + 1.4)), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    n_calls = max(max(r[f"calls_{a}"] for a in order) for r in rows) if rows else 1
    mat = np.array([[r[f"calls_{a}"] / max(n_calls, 1) for a in order] + [r["calls_main_study_5idea"] / max(n_ref, 1)]
                    for r in rows], dtype=float)
    ax.imshow(mat, aspect="auto", cmap="Purples", vmin=0, vmax=1)
    for i, r in enumerate(rows):
        for j, a in enumerate(cols):
            v = r["calls_main_study_5idea"] if a == "ref" else r[f"calls_{a}"]
            if v:
                ax.text(j, i, str(v), ha="center", va="center", fontsize=6.5, color="white" if mat[i, j] > 0.55 else INK)
    mark = {"not_found": "  ★", "unchecked": "  ?"}
    ax.set_yticks(range(n))
    ax.set_yticklabels([f"{'▶ ' if r['main5'] else ''}{r['move']} {str(r['label'])[:34]} · {r['category']}"
                        f"{mark.get(r['prior_art'], '')}" for r in rows], fontsize=6.5, color=INK2)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([COND_NAME[a] for a in order] + [f"main study\n(5 ideas, {n_ref} calls)"], fontsize=7, color=INK2)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.suptitle(f"{NEED}: calls whose list contains each move", fontsize=10, color=INK, x=0.01, ha="left")
    fig.text(0.01, 0.005, f"▶ one of the main {MAIN_K} moves of the main study.  ★ no prior art found, ? prior art "
             "not checked.  Shading: share of the column's calls.", fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.015, 1, 0.97))
    fig.savefig(OUT / "m6_incidence.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
