#!/usr/bin/env python3
"""
threshold_sweep.py: how much the yield comparison depends on the top-idea threshold (Experiment 1).

  python threshold_sweep.py      # reads results/ideas_ranked.csv -> results/threshold_sweep.csv  (no API calls)

The paper's top-idea threshold (score >= 4.0) was fixed after seeing the scores. This script repeats the
yield computation of tail_charts.py at 3.5, 3.75, 4.0 and 4.25 with the same functions: yield = all top ideas
of an arm / all its tokens, per 100k tokens; 95% CI from 2,000 bootstrap resamples of calls within market
need, seed 0. Calls that returned no parseable ideas (one: B_M7_high_r03) have no rows in ideas_ranked.csv
and are therefore not counted, neither their ideas nor their tokens; this matches the yields in the paper.
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

import tail_charts as tc

THRESHOLDS = [3.5, 3.75, 4.0, 4.25]
OUT = tc.RESULTS / "threshold_sweep.csv"


def main() -> None:
    calls = tc.load(Path(tc.RESULTS / "ideas_ranked.csv"))
    groups = tc.by_arm_need(calls)
    scores = [s for c in calls.values() for s in c["scores"]]
    arms = [(c, e) for c in tc.COND_ORDER for e in tc.EFFORTS if (c, e) in groups]
    rows = []
    for th in THRESHOLDS:
        rng = random.Random(tc.SEED)                      # same seed for every threshold, as in tail_charts.py
        share = sum(s >= th for s in scores) / len(scores)
        for arm in arms:
            pn = groups[arm]
            lo, hi, _ = tc.bootstrap_yield(pn, th, rng)
            rows.append({"threshold": th, "share_of_ideas": round(share, 4), "condition": arm[0], "effort": arm[1],
                         "needs": len(pn), "yield_per_100k": round(tc.yield_per_100k(pn, th), 2),
                         "ci_lo": round(lo, 2), "ci_hi": round(hi, 2)})
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for th in THRESHOLDS:
        rs = sorted((r for r in rows if r["threshold"] == th), key=lambda r: -r["yield_per_100k"])
        print(f">= {th:<4} ({rs[0]['share_of_ideas']:.1%} of ideas): " +
              "  ".join(f"{r['condition']}{r['effort'][0]} {r['yield_per_100k']} [{r['ci_lo']}-{r['ci_hi']}]" for r in rs))
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
