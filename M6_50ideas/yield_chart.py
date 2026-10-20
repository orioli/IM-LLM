#!/usr/bin/env python3
"""
yield_chart.py: the main study's Figure 8 (top ideas found against tokens spent) for the 50-idea run.

  cd M6_50ideas
  python yield_chart.py            # after score_ideas.py table; no API calls, no codebook needed

Same definitions and drawing code as ../tail_charts.py (chart 8): a top idea scores >= 4.0 (mean of the
four blind criteria), the yield of an arm is all its top ideas / all its tokens (top ideas per 100k
tokens, the slope of a line through the origin), and the 95% CI comes from 2,000 bootstrap resamples
of calls. Here every arm is one need (M6) at medium effort, asked for 50 ideas per call; all ideas of
a call and all its tokens are counted.

Writes results/charts/8_top_ideas_vs_tokens_m6_50ideas.png and results/yield_m6_50ideas.csv, and prints
the main study's M6 yields (5 ideas per call) for reference. The two are not directly comparable: asked
for 50, the model writes shorter ideas (about 40 words, against about 100), which the judge scores lower.
"""
from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import defaultdict

from common import CONDITIONS, NEED, RESULTS, ROOT, RUNS, load_calls

sys.path.insert(0, str(ROOT))
import tail_charts as tc  # noqa: E402  (the main study's chart code, reused unchanged)

EFFORT = "medium"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--threshold", type=float, default=4.0)
    ap.add_argument("--scores", default=str(RESULTS / "ideas_scored.csv"))
    args = ap.parse_args()

    runs = {k: c for k, c in load_calls([RUNS]).items() if c.get("target_need") == NEED}
    calls = {}
    with open(args.scores, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            run = runs.get(r["run_id"])
            if run is None:
                continue
            c = calls.setdefault(r["run_id"], {"run_id": r["run_id"], "condition": run["condition"],
                                               "effort": run.get("effort", EFFORT), "need": NEED, "scores": [],
                                               "tokens": (run.get("input_tokens") or 0) + (run.get("output_tokens") or 0)})
            c["scores"].append(float(r["score"]))
    if not calls:
        sys.exit(f"No scored ideas: run `python score_ideas.py score` and `table` first ({args.scores}).")

    groups = tc.by_arm_need(calls)
    rng = random.Random(tc.SEED)
    rows = []
    for c in CONDITIONS:
        pn = groups.get((c, EFFORT))
        if not pn:
            continue
        lo, hi, _ = tc.bootstrap_yield(pn, args.threshold, rng)
        n_ideas = sum(len(x["scores"]) for cs in pn.values() for x in cs)
        n_top = sum(s >= args.threshold for cs in pn.values() for x in cs for s in x["scores"])
        toks = sum(x["tokens"] for cs in pn.values() for x in cs)
        rows.append({"condition": c, "effort": EFFORT, "calls": sum(len(cs) for cs in pn.values()), "ideas": n_ideas,
                     "top_ideas": n_top, "top_idea_rate": round(n_top / n_ideas, 3), "tokens": toks,
                     "yield_per_100k": tc.yield_per_100k(pn, args.threshold), "yield_lo": lo, "yield_hi": hi})

    # the main study's drawing code, pointed at this study's folder and arms
    tc.OUT = RESULTS / "charts"
    tc.OUT.mkdir(parents=True, exist_ok=True)
    tc.THUMB = ROOT / "results" / "charts" / "0b_slices_grid_thumb.png"
    tc.CURVE_ARMS = [(c, EFFORT) for c in CONDITIONS]
    tag = "_m6_50ideas" + ("" if args.threshold == 4.0 else f"_ge{args.threshold:g}")
    tc.chart_yield(rows, groups, args.threshold,
                   f"\n{NEED} only · 50 ideas asked per call · {EFFORT} effort · "
                   f"{rows[0]['calls']} calls per arm", tag=tag)

    with (RESULTS / f"yield{tag}.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()} for r in rows)

    print(f"\n{'arm':<10} {'ideas':>6} {'top':>5} {'rate':>6} {'tokens':>9}  top ideas per 100k tokens [95% CI]")
    for r in sorted(rows, key=lambda r: -r["yield_per_100k"]):
        print(f"{r['condition']} · {EFFORT:<6} {r['ideas']:>6} {r['top_ideas']:>5} {r['top_idea_rate']:>6.1%} "
              f"{r['tokens']:>9,}  {r['yield_per_100k']:.1f} [{r['yield_lo']:.1f}–{r['yield_hi']:.1f}]")

    ref = ROOT / "results" / "ideas_ranked.csv"          # the main study, 5 ideas per call
    if ref.exists():
        agg = defaultdict(lambda: [0, 0, set(), 0])
        with ref.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("target_need") != NEED or (r.get("persona") or "engineer") != "engineer":
                    continue
                a = agg[(r["condition"], r["effort"])]
                a[0] += 1
                a[1] += float(r["score"]) >= args.threshold
                if r["run_id"] not in a[2]:
                    a[2].add(r["run_id"])
                    a[3] += int(float(r["run_input_tokens"]) + float(r["run_output_tokens"]))
        print(f"\nFor reference, the main study on {NEED} (5 ideas per call, 5 calls per arm; shorter lists, "
              "longer ideas, not directly comparable):")
        for (c, e), (n, t, runs_, toks) in sorted(agg.items()):
            print(f"  {c} · {e:<6} {n:>4} ideas {t:>3} top  {1e5 * t / toks:5.1f} per 100k tokens")
    print(f"-> results/charts/8_top_ideas_vs_tokens{tag}.png, results/yield{tag}.csv")


if __name__ == "__main__":
    main()
