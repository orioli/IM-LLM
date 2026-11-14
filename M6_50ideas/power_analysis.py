#!/usr/bin/env python3
"""
power_analysis.py: how much can the runs so far say, and how many calls would a full experiment need?

  cd M6_50ideas
  python power_analysis.py          # no API calls -> results/power_analysis.md

Part 1  The 50-idea runs together. For every model that has been run and scored, the yield ratios
        B/C (slice against no graph), A/C (full graph against no graph), A/B and R/C, each with a 95%
        bootstrap interval, then pooled over models (random effects, DerSimonian-Laird, on the log ratio),
        for all models and for the Claude and the Chinese models apart. Confirmation calls are included
        (20 calls per arm where they exist).

Part 2  Power of the 50-idea design. From the spread between calls: the smallest ratio a 10-call arm can
        detect, and the calls per arm needed to detect a ratio of 1.5 or 1.25 (two-sided 5%, 80% power) or
        to show that two arms are equivalent within 25% or 20% (two one-sided tests at 5%, 80% power).

Part 3  The same for the 5-idea design of Experiment 1, from the paper's own calls (../results/
        ideas_ranked.csv, high effort, 13 needs x 5 calls per arm): what 65 calls per arm can detect, and
        the replicates per need a replication needs.

Part 4  Judge noise: how reliable one judge pass is (from the judge-route check), and what a second pass
        would buy.

Method. Yield = top ideas (score >= 4.0) / tokens. The standard error of a log yield ratio comes from
2,000 bootstrap resamples of calls within arm (within need and arm in Part 3). For n calls per arm it is
scaled by sqrt(calls now / n): calls are independent, so this is the usual square-root law.
"""
from __future__ import annotations

import csv
import math
import random
from collections import defaultdict

import compare_runs_chart as cr
import judge_route_check as jrc
import netcost_table as nt
import replication_report as rr

HERE, ROOT, tc = cr.HERE, cr.ROOT, cr.tc
REPS, TOP = 2000, 4.0
PAIRS = [("B", "C"), ("A", "C"), ("A", "B"), ("R", "C")]
PAIR_NAME = {("B", "C"): "slice / no graph", ("A", "C"): "full graph / no graph",
             ("A", "B"): "full graph / slice", ("R", "C"): "random slice / no graph"}
Z_A2, Z_A1, Z_B = 1.959964, 1.644854, 0.841621          # two-sided 5%, one-sided 5%, 80% power
Z_B2 = 1.281552                                           # equivalence: 80% power needs each one-sided test at 90%


def log_ratio(x: list[dict], y: list[dict]) -> float | None:
    a, b = rr.tot(x), rr.tot(y)
    if not a["top"] or not b["top"]:
        return None
    return math.log((a["top"] / a["tokens"]) / (b["top"] / b["tokens"]))


def boot_se(x: list[dict], y: list[dict], rng: random.Random) -> tuple[float, float, float]:
    """(SE, lo, hi) of the log yield ratio x/y: calls resampled within arm."""
    d = [v for v in (log_ratio([rng.choice(x) for _ in x], [rng.choice(y) for _ in y]) for _ in range(REPS)) if v is not None]
    d.sort()
    m = sum(d) / len(d)
    return (sum((v - m) ** 2 for v in d) / (len(d) - 1)) ** 0.5, d[int(0.025 * len(d))], d[int(0.975 * len(d)) - 1]


def pooled(est: list[tuple[float, float]]) -> dict:
    """Random-effects pooling (DerSimonian-Laird) of (log ratio, SE)."""
    w = [1 / s ** 2 for _, s in est]
    fixed = sum(wi * e for wi, (e, _) in zip(w, est)) / sum(w)
    q = sum(wi * (e - fixed) ** 2 for wi, (e, _) in zip(w, est))
    k = len(est)
    c = sum(w) - sum(wi ** 2 for wi in w) / sum(w)
    tau2 = max(0.0, (q - (k - 1)) / c) if k > 1 and c > 0 else 0.0
    w2 = [1 / (s ** 2 + tau2) for _, s in est]
    mu = sum(wi * e for wi, (e, _) in zip(w2, est)) / sum(w2)
    se = (1 / sum(w2)) ** 0.5
    return {"ratio": math.exp(mu), "lo": math.exp(mu - Z_A2 * se), "hi": math.exp(mu + Z_A2 * se),
            "i2": max(0.0, (q - (k - 1)) / q) if q > 0 else 0.0, "k": k}


def n_detect(se_now: float, n_now: float, ratio: float) -> float:
    return n_now * ((Z_A2 + Z_B) * se_now / math.log(ratio)) ** 2


def n_equiv(se_now: float, n_now: float, margin: float) -> float:
    return n_now * ((Z_A1 + Z_B2) * se_now / math.log(margin)) ** 2


def pct(r: float) -> str:
    return f"{100 * (r - 1):+.0f}%"


def main() -> None:
    names = dict(nt.MODELS)
    keys = [k for k, _ in nt.MODELS if nt.files(k)[0].exists() and nt.files(k)[1].exists()]
    rng = random.Random(tc.SEED)
    data = {}
    for k in keys:
        d = rr.load(k, TOP)
        extra = rr.load(k, TOP, "confirm")
        data[k] = {c: d[c] + (extra.get(c) or []) for c in rr.CONDS}

    L = ["# What the runs can say, and what a full experiment needs", "",
         "No API calls. Yield = top ideas (score ≥ 4.0) per token. Ratios are of yields; 1.00 = no difference. "
         f"Intervals: 95%, {REPS:,} bootstrap resamples of calls within arm.", "",
         "## 1. The six 50-idea runs together (M6)", ""]
    est = defaultdict(dict)
    for p in PAIRS:
        L += [f"**{PAIR_NAME[p].capitalize()}** ({p[0]} / {p[1]})", "",
              "| Model | Calls per arm | Ratio [95% CI] | SE of log ratio |", "| --- | --- | --- | --- |"]
        for k in keys:
            x, y = data[k][p[0]], data[k][p[1]]
            lr = log_ratio(x, y)
            se, lo, hi = boot_se(x, y, rng)
            est[p][k] = (lr, se, (len(x) + len(y)) / 2)
            L.append(f"| {names[k]} | {len(x)}, {len(y)} | {math.exp(lr):.2f} [{math.exp(lo):.2f}–{math.exp(hi):.2f}] | {se:.2f} |")
        for label, group in (("All models", keys), ("Claude models (the paper)", [k for k in keys if k in rr.PAPER]),
                             ("Chinese models", [k for k in keys if k not in rr.PAPER])):
            if len(group) > 1:
                m = pooled([est[p][k][:2] for k in group])
                L.append(f"| **{label}, pooled** | {m['k']} models | **{m['ratio']:.2f} [{m['lo']:.2f}–{m['hi']:.2f}]** | "
                         f"heterogeneity I² = {100 * m['i2']:.0f}% |")
        L.append("")

    L += ["## 2. Power of the 50-idea design (M6)", "",
          "Slice against no graph (B / C), the comparison the paper's \"no better than no graph\" rests on. "
          "\"Smallest detectable ratio\" is what a 10-call arm finds with 80% power; a true difference smaller "
          "than that will usually come out as \"indistinguishable\".", "",
          "| Model | SE of log ratio at 10 calls per arm | Smallest detectable ratio at 10 calls | Calls per arm to "
          "detect 1.5× | to detect 1.25× | to show equivalence within ±25% | within ±20% |", "|" + " --- |" * 7]
    ses = []
    for k in keys:
        lr, se, n = est[("B", "C")][k]
        se10 = se * (n / 10) ** 0.5
        ses.append(se10)
        L.append(f"| {names[k]} | {se10:.2f} | {math.exp((Z_A2 + Z_B) * se10):.2f}× | {n_detect(se10, 10, 1.5):.0f} | "
                 f"{n_detect(se10, 10, 1.25):.0f} | {n_equiv(se10, 10, 1.25):.0f} | {n_equiv(se10, 10, 1.20):.0f} |")
    med = sorted(ses)[len(ses) // 2]
    L += [f"| **Typical (median SE {med:.2f})** | {med:.2f} | **{math.exp((Z_A2 + Z_B) * med):.2f}×** | "
          f"**{n_detect(med, 10, 1.5):.0f}** | **{n_detect(med, 10, 1.25):.0f}** | **{n_equiv(med, 10, 1.25):.0f}** | "
          f"**{n_equiv(med, 10, 1.20):.0f}** |", "",
          "Calls needed fall in proportion when several needs or models are pooled: with *m* needs (or models) "
          "analysed together, divide by *m*, provided the effect is the same in each.", ""]

    # ── Part 3: Experiment 1 (5 ideas per call), the paper's calls at high effort ──
    calls = {}
    with (ROOT / "results" / "ideas_ranked.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["effort"] != "high" or r.get("persona", "engineer") not in ("", "engineer"):
                continue
            c = calls.setdefault(r["run_id"], {"cond": r["condition"], "need": r["target_need"], "top": 0, "ideas": 0,
                                               "tokens": float(r["run_input_tokens"]) + float(r["run_output_tokens"])})
            c["ideas"] += 1
            c["top"] += float(r["score"]) >= TOP
    cells = defaultdict(lambda: defaultdict(list))          # cond -> need -> calls
    for c in calls.values():
        cells[c["cond"]][c["need"]].append(c)

    def resample(cond):                                      # calls resampled within need
        return [rng.choice(cs) for cs in cells[cond].values() for _ in cs]

    def lr1(x, y):
        a, b = sum(c["top"] for c in x) / sum(c["tokens"] for c in x), sum(c["top"] for c in y) / sum(c["tokens"] for c in y)
        return math.log(a / b) if a > 0 and b > 0 else None

    L += ["## 3. Power of the 5-idea design (Experiment 1, the paper's calls, high effort)", "",
          "| Comparison | Calls per arm | Ratio [95% CI] | Smallest detectable ratio now | Replicates per need (13 needs) to "
          "detect 1.5× | 1.25× | equivalence within ±25% |", "|" + " --- |" * 7]
    for p in PAIRS:
        x = [c for cs in cells[p[0]].values() for c in cs]
        y = [c for cs in cells[p[1]].values() for c in cs]
        d = sorted(v for v in (lr1(resample(p[0]), resample(p[1])) for _ in range(REPS)) if v is not None)
        m = sum(d) / len(d)
        se = (sum((v - m) ** 2 for v in d) / (len(d) - 1)) ** 0.5
        n = (len(x) + len(y)) / 2
        per_need = lambda calls_needed: math.ceil(calls_needed / 13)
        L.append(f"| {PAIR_NAME[p]} ({p[0]} / {p[1]}) | {len(x)}, {len(y)} | {math.exp(lr1(x, y)):.2f} "
                 f"[{math.exp(d[int(0.025 * len(d))]):.2f}–{math.exp(d[int(0.975 * len(d)) - 1]):.2f}] | "
                 f"{math.exp((Z_A2 + Z_B) * se):.2f}× | {per_need(n_detect(se, n, 1.5))} | {per_need(n_detect(se, n, 1.25))} | "
                 f"{per_need(n_equiv(se, n, 1.25))} |")
    L += ["", "The paper ran 5 replicates per need. Replicates above are per need and arm, with all 13 needs.", ""]

    # ── Part 4: judge noise ──
    reqs = [r for _, folder in jrc.RUNS for r in jrc.pairs(folder)]
    flat = [(jrc.score(a), jrc.score(b)) for r in reqs for a, b in r]
    if flat:
        n = len(flat)
        mo, mn = sum(a for a, _ in flat) / n, sum(b for _, b in flat) / n
        so = (sum((a - mo) ** 2 for a, _ in flat) / n) ** 0.5
        sn = (sum((b - mn) ** 2 for _, b in flat) / n) ** 0.5
        r = sum((a - mo) * (b - mn) for a, b in flat) / n / (so * sn)
        top_old = [a >= TOP for a, _ in flat]
        again = sum(a >= TOP and b >= TOP for a, b in flat) / sum(top_old)
        near = sum(3.75 <= a <= 4.0 for a, _ in flat) / n
        L += ["## 4. Judge noise", "",
              f"From {n} ideas scored twice by the same judge (`results/judge_route_check.md`): the two scores "
              f"correlate at r = {r:.2f}, so one pass has a reliability of about {r:.2f}; the mean of two passes "
              f"would have {2 * r / (1 + r):.2f}, of three {3 * r / (1 + 2 * r):.2f}. An idea scored top once is top "
              f"again {100 * again:.0f}% of the time. {100 * near:.0f}% of ideas score 3.75 or 4.0, one step from the "
              "cut-off on either side, which is where a single pass flips. The intervals in Parts 1 to 3 already "
              "contain this noise (it is part of the spread between calls), but they do not show how much of the "
              "spread a second judge pass would remove.", ""]
    out = HERE / "results" / "power_analysis.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"-> {out.relative_to(HERE)}")


if __name__ == "__main__":
    main()
