#!/usr/bin/env python3
"""
judge_route_check.py: does the judge give the same scores through OpenRouter's batch route as it gave the paper?

  cd M6_50ideas
  for m in haiku opus fable; do GEN_MODEL=$m python judge_batch.py submit --check --run-ids <calls>; done
  for m in haiku opus fable; do GEN_MODEL=$m python judge_batch.py wait --check; done
  python judge_route_check.py                      # no API calls -> results/judge_route_check.md

Calls the paper already scored (Anthropic API, October 2026) are scored a second time through the route
used for the Chinese models (OpenRouter Batch API -> Anthropic, same model, prompt, effort and max_tokens).
Each idea then has two scores from the same judge. Compared, pooled and per generator:

  mean score, old and new, and the mean difference with a 95% interval (bootstrap over requests, since the
  5 ideas of a request are rated together); the share of top ideas (score >= 4.0) old and new; how often
  the two ratings agree on "top idea", with Cohen's kappa; the correlation of the two scores.

Two ratings of one idea by the same judge never agree exactly (the judge samples), so the test is for a
systematic shift. Accepted (CHINESE_REPLICATION.md, Section 6) if the pooled mean differs by at most 0.10
and the pooled share of top ideas by at most 3 percentage points.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from top_ideas import IDEA_CRITERIA  # noqa: E402

RUNS = [("Haiku 5.5", HERE / "results"), ("Opus 5.5", HERE / "results" / "opus"), ("Fable 5.1", HERE / "results" / "fable")]
MAX_MEAN_SHIFT, MAX_TOP_SHIFT, TOP = 0.10, 0.03, 4.0
REPS = 2000


def latest(path: Path) -> dict:
    out = {}
    if path.exists():
        for line in path.open(encoding="utf-8"):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("ok"):
                out[(r["run_id"], r["start"])] = r["ratings"]
    return out


def score(rating) -> float | None:
    vals = [rating.get(c) for c in IDEA_CRITERIA if isinstance(rating.get(c), (int, float))] if isinstance(rating, dict) else []
    return sum(vals) / len(vals) if vals else None


def pairs(folder: Path) -> list[list[tuple[dict, dict]]]:
    """One list per request: (old rating, new rating) for each idea rated both times."""
    old, new = latest(folder / "idea_scores.jsonl"), latest(folder / "judge_route_check" / "idea_scores.jsonl")
    out = []
    for key, ratings in new.items():
        if key not in old:
            continue
        req = [(o, n) for o, n in zip(old[key], ratings) if score(o) is not None and score(n) is not None]
        if req:
            out.append(req)
    return out


def stats(reqs: list[list[tuple[dict, dict]]], rng: random.Random) -> dict:
    flat = [p for r in reqs for p in r]
    o, n = [score(a) for a, _ in flat], [score(b) for _, b in flat]
    k = len(flat)
    mo, mn = sum(o) / k, sum(n) / k
    boot = []
    for _ in range(REPS):
        res = [p for _ in reqs for p in rng.choice(reqs)]
        boot.append(sum(score(b) - score(a) for a, b in res) / len(res))
    boot.sort()
    to, tn = [x >= TOP for x in o], [x >= TOP for x in n]
    agree = sum(a == b for a, b in zip(to, tn)) / k
    po, pn = sum(to) / k, sum(tn) / k
    chance = po * pn + (1 - po) * (1 - pn)
    so = (sum((x - mo) ** 2 for x in o) / k) ** 0.5
    sn = (sum((x - mn) ** 2 for x in n) / k) ** 0.5
    r = sum((a - mo) * (b - mn) for a, b in zip(o, n)) / k / (so * sn) if so and sn else float("nan")
    return {"requests": len(reqs), "ideas": k, "mean_old": mo, "mean_new": mn, "diff": mn - mo,
            "diff_lo": boot[int(0.025 * REPS)], "diff_hi": boot[int(0.975 * REPS) - 1],
            "top_old": po, "top_new": pn, "agree": agree, "kappa": (agree - chance) / (1 - chance) if chance < 1 else float("nan"),
            "r": r, "abs_diff": sum(abs(a - b) for a, b in zip(o, n)) / k,
            "criteria": {c: sum(b[c] - a[c] for a, b in flat if isinstance(a.get(c), (int, float))
                                and isinstance(b.get(c), (int, float))) / k for c in IDEA_CRITERIA}}


def main() -> None:
    rng = random.Random(0)
    per = [(name, pairs(folder)) for name, folder in RUNS]
    per = [(name, reqs) for name, reqs in per if reqs]
    if not per:
        sys.exit("no re-scored calls found: run judge_batch.py submit --check and wait --check first")
    rows = [(name, stats(reqs, rng)) for name, reqs in per]
    rows.append(("All", stats([r for _, reqs in per for r in reqs], rng)))
    pooled = rows[-1][1]
    ok = abs(pooled["diff"]) <= MAX_MEAN_SHIFT and abs(pooled["top_new"] - pooled["top_old"]) <= MAX_TOP_SHIFT
    lines = ["# Judge-route check", "",
             "The same ideas, scored twice by `claude-sonnet-5-5` with the same prompt, effort and `max_tokens`: "
             "*old* = the paper's scores (Anthropic API, October 2026), *new* = OpenRouter Batch API pinned to "
             "Anthropic (the route used for the Chinese models). Replicate 1 of each representation of each run.", "",
             "| Ideas written by | Requests | Ideas | Mean score old | new | Difference [95% CI] | Top ideas old | new | "
             "Agree on top | kappa | r | Mean abs. difference |", "|" + " --- |" * 12]
    for name, s in rows:
        lines.append(f"| {name} | {s['requests']} | {s['ideas']} | {s['mean_old']:.2f} | {s['mean_new']:.2f} | "
                     f"{s['diff']:+.3f} [{s['diff_lo']:+.3f}, {s['diff_hi']:+.3f}] | {100 * s['top_old']:.1f}% | "
                     f"{100 * s['top_new']:.1f}% | {100 * s['agree']:.1f}% | {s['kappa']:.2f} | {s['r']:.2f} | "
                     f"{s['abs_diff']:.2f} |")
    lines += ["", "Mean difference per criterion, new − old, all ideas: "
              + ", ".join(f"{c} {v:+.3f}" for c, v in pooled["criteria"].items()) + ".", "",
              f"**Verdict: route {'accepted' if ok else 'NOT accepted'}.** Pooled mean shift {pooled['diff']:+.3f} "
              f"(limit ±{MAX_MEAN_SHIFT}); pooled top-idea share {100 * pooled['top_old']:.1f}% → "
              f"{100 * pooled['top_new']:.1f}% (limit ±{100 * MAX_TOP_SHIFT:.0f} points). The two ratings of an idea "
              f"differ by {pooled['abs_diff']:.2f} points on average: that is the judge's own run-to-run noise, "
              f"present in the paper's scores as well."]
    out = HERE / "results" / "judge_route_check.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"-> {out.relative_to(HERE)}")


if __name__ == "__main__":
    main()
