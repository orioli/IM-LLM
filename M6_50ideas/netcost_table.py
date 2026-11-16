#!/usr/bin/env python3
"""
netcost_table.py: the paper's net-cost table (tab:netcost), for every model that has been run and scored.

  cd M6_50ideas
  python netcost_table.py                                  # all models with a run log and scores; no API calls
  python netcost_table.py --models haiku opus fable        # the paper's three rows only
  python netcost_table.py --screen 0 judge 0.5 5           # other screening costs per idea (USD)

What it answers: which model is cheapest per top idea once the ideas also have to be screened?

  net cost per top idea = (generation cost + s x ideas generated) / top ideas

pooled over the four representations of the 50-idea runs (M6, 10 calls each), for a screening cost s per
idea. Default columns: s = 0 (generation only), s = the automated judge (measured: the Sonnet judge's
tokens at list price / ideas scored, about $0.0012), and s = $0.50 (a person reading an idea for about 30
seconds at $60 an hour). Generation cost is each call's tokens at the model's list price (PRICES in
compare_runs_chart.py), as in the per-dollar charts. A top idea scores >= 4.0.

Intervals: 2,000 bootstrap resamples of calls within representation (percentile 95%), each model with its
own fixed seed, so adding a model never changes another model's interval. Bold: the cheapest model of a
column, and any model that is cheaper than it in at least 2.5% of resamples (indistinguishable).

Also printed: for each model, the screening cost at which it becomes cheaper per top idea than --reference
(default haiku), with a 95% interval. This is the paper's "Opus becomes cheaper than Haiku once screening
costs more than about $0.005 per idea".

Writes results/netcost_table.csv, .md and .tex (the rows in the paper's LaTeX format).
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys

import compare_runs_chart as cr

HERE, tc = cr.HERE, cr.tc
# GEN_MODEL key -> row name, in the order of the table
MODELS = [("haiku", "Haiku 5.5"), ("opus", "Opus 5.5"), ("sonnet", "Sonnet 5.5"), ("fable", "Fable 5.1"),
          ("deepseek", "DeepSeek V4.1 Flash"), ("deepseekpro", "DeepSeek V4 Pro"), ("qwen", "Qwen3.8 Flash"),
          ("glm", "GLM-5.3 Flash")]
JUDGE_MODEL = "claude-sonnet-5-5"
CONDS = cr.ORDER
REPS = 2000
HUMAN = 0.50


def files(key: str):
    """(run log, scored ideas, judge log) of a model's 50-idea run; Haiku keeps the first run's names."""
    if key == "haiku":
        return (HERE / "runs" / "m6_50ideas.jsonl", HERE / "results" / "ideas_scored.csv",
                HERE / "results" / "idea_scores.jsonl")
    return (HERE / "runs" / f"m6_50ideas_{key}.jsonl", HERE / "results" / key / "ideas_scored.csv",
            HERE / "results" / key / "idea_scores.jsonl")


def load(key: str, th: float) -> dict[str, list[tuple[int, int, float]]]:
    """condition -> [(ideas, top ideas, generation cost in USD)], one tuple per call."""
    runs, scores, _ = files(key)
    by_cond = {c: [] for c in CONDS}
    for x in cr.from_study(runs, scores).values():
        if x["model"] not in cr.PRICES:
            sys.exit(f"no price for model {x['model']!r}: add it to PRICES in compare_runs_chart.py")
        pin, pout = cr.PRICES[x["model"]]
        by_cond[x["condition"]].append((len(x["scores"]), sum(s >= th for s in x["scores"]),
                                        (x["in"] * pin + x["out"] * pout) / 1e6))
    return by_cond


def judge_cost_per_idea(key: str) -> tuple[float, int]:
    """(USD, ideas): the judge's tokens for this run at list price, and the ideas it scored."""
    _, scores, log = files(key)
    latest = {}
    for line in log.open(encoding="utf-8"):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("ok"):
            latest[(r["run_id"], r["start"])] = r          # a re-scored request counts once
    pin, pout = cr.PRICES[JUDGE_MODEL]
    usd = sum((r.get("input_tokens") or 0) * pin + (r.get("output_tokens") or 0) * pout for r in latest.values()) / 1e6
    with scores.open(encoding="utf-8") as fh:
        return usd, sum(1 for _ in csv.DictReader(fh))


def totals(by_cond) -> tuple[int, int, float]:
    calls = [c for cs in by_cond.values() for c in cs]
    return sum(c[0] for c in calls), sum(c[1] for c in calls), sum(c[2] for c in calls)


def draws(key: str, by_cond) -> list[tuple[int, int, float]]:
    """REPS pooled (ideas, top ideas, cost) totals, calls resampled within representation."""
    rng = random.Random(f"{tc.SEED}-netcost-{key}")
    return [totals({c: [rng.choice(cs) for _ in cs] for c, cs in by_cond.items() if cs}) for _ in range(REPS)]


def net(t: tuple[int, int, float], s: float) -> float:
    ideas, top, usd = t
    return (usd + s * ideas) / top if top else float("inf")


def ci(vals: list[float]) -> tuple[float, float]:
    v = sorted(vals)
    return v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]


def break_even(x, ref) -> float | None:
    """Screening cost per idea above which x is cheaper per top idea than ref (None if there is no such cost)."""
    (ix, tx, ux), (ir, tr, ur) = x, ref
    if not tx or not tr:
        return None
    extra_gen, fewer_ideas = ux / tx - ur / tr, ir / tr - ix / tx     # x costs more to generate, sifts fewer ideas
    return extra_gen / fewer_ideas if extra_gen > 0 and fewer_ideas > 0 else None


def money(v: float) -> str:
    return f"{v:.2f}" if v >= 1 else f"{v:.3f}"


def cell(v: float, lo: float, hi: float) -> str:
    return f"{money(v)} [{money(lo)}--{money(hi)}]"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    keys = [k for k, _ in MODELS]
    ap.add_argument("--models", nargs="+", choices=keys, default=None,
                    help="rows, in this order (default: every model that has been run and scored)")
    ap.add_argument("--screen", nargs="+", default=["0", "judge", str(HUMAN)],
                    help="screening costs per idea in USD; 'judge' = the measured cost of the Sonnet judge")
    ap.add_argument("--judge-cost", type=float, default=None,
                    help="USD per idea for 'judge' (default: measured over the models shown, rounded to 4 decimals)")
    ap.add_argument("--reference", choices=keys, default="haiku", help="model the break-even costs are against")
    ap.add_argument("--threshold", type=float, default=4.0)
    args = ap.parse_args()

    names = dict(MODELS)
    have = [k for k in (args.models or keys) if files(k)[0].exists() and files(k)[1].exists()]
    missing = [k for k in (args.models or []) if k not in have]
    if missing:
        print(f"not run or not scored yet, left out: {', '.join(missing)}")
    if not have:
        sys.exit("no model has both a run log and scores")

    # the judge's cost per idea, measured
    measured = {k: judge_cost_per_idea(k) for k in have if files(k)[2].exists()}
    for k, (usd, n) in measured.items():
        print(f"judge cost, {names[k]:<20} ${usd:.2f} for {n:,} ideas = ${usd / n:.5f} per idea")
    judge = args.judge_cost
    if judge is None:
        if not measured:
            sys.exit("no judge log found: pass --judge-cost")
        judge = round(sum(u for u, _ in measured.values()) / sum(n for _, n in measured.values()), 4)
    usd_label = lambda v: f"\\${v:.2f}" if v >= 0.01 else f"\\${v:g}"          # $0, $0.0012, $0.50
    screens = [(usd_label(judge) + " (AI judge)", judge) if s == "judge" else
               (usd_label(float(s)) + (" (human)" if float(s) == HUMAN else ""), float(s)) for s in args.screen]

    data = {k: load(k, args.threshold) for k in have}
    for k, by_cond in data.items():
        short = {c: len(cs) for c, cs in by_cond.items() if len(cs) != 10}
        if short:
            print(f"note: {names[k]} has calls per representation other than 10: {short}")
    point = {k: totals(d) for k, d in data.items()}
    boot = {k: draws(k, d) for k, d in data.items()}

    # bold: the cheapest of each column, and any model cheaper than it in >= 2.5% of resamples
    bold = {}
    for label, s in screens:
        best = min(have, key=lambda k: net(point[k], s))
        for k in have:
            wins = sum(net(a, s) < net(b, s) for a, b in zip(boot[k], boot[best])) / REPS
            bold[(k, label)] = k == best or wins >= 0.025

    rows = []
    for k in have:
        ideas, top, usd = point[k]
        lo, hi = ci([i / t for i, t, _ in boot[k] if t])
        row = {"model": names[k], "calls": sum(len(cs) for cs in data[k].values()), "ideas": ideas, "top_ideas": top,
               "generation_usd": usd, "ideas_per_top": ideas / top, "ideas_per_top_lo": lo, "ideas_per_top_hi": hi}
        for label, s in screens:
            lo, hi = ci([net(t, s) for t in boot[k]])
            tag = f"net_{s:g}"
            row.update({tag: net(point[k], s), tag + "_lo": lo, tag + "_hi": hi, tag + "_bold": bold[(k, label)]})
        be = break_even(point[k], point[args.reference]) if args.reference in have and k != args.reference else None
        if be is not None:
            pairs = [break_even(a, b) for a, b in zip(boot[k], boot[args.reference])]
            vals = [p for p in pairs if p is not None]
            lo, hi = ci(vals)
            row.update(break_even_vs_ref=be, break_even_lo=lo, break_even_hi=hi,
                       break_even_defined_share=len(vals) / REPS)
        else:
            row.update(break_even_vs_ref="", break_even_lo="", break_even_hi="", break_even_defined_share="")
        rows.append(row)

    out = HERE / "results" / "netcost_table"
    with out.with_suffix(".csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()} for r in rows)

    def fmt(row, label, s, b0, b1):
        tag = f"net_{s:g}"
        text = cell(row[tag], row[tag + "_lo"], row[tag + "_hi"])
        if row[tag + "_bold"]:                         # bold the value, not the interval, as in the paper
            value, rest = text.split(" ", 1)
            text = f"{b0}{value}{b1} {rest}"
        return text

    head = ["Model", "Ideas per top idea"] + [label for label, _ in screens]
    md = ["| " + " | ".join(h.replace("\\$", "$") for h in head) + " |", "|" + " --- |" * len(head)]
    tex = [" & ".join(head) + " \\\\"]
    for row in rows:
        per_top = f"{row['ideas_per_top']:.1f} [{row['ideas_per_top_lo']:.1f}--{row['ideas_per_top_hi']:.1f}]"
        md.append("| " + " | ".join([row["model"], per_top.replace("--", "–")]
                                    + [fmt(row, l, s, "**", "**").replace("--", "–") for l, s in screens]) + " |")
        tex.append(" & ".join([row["model"], per_top] + [fmt(row, l, s, "\\textbf{", "}") for l, s in screens]) + " \\\\")
    notes = [f"Net cost per top idea (USD) = (generation cost + screening cost x ideas) / top ideas, pooled over "
             f"the four representations (M6, 50 ideas per call). 95% intervals: {REPS:,} bootstrap resamples of calls "
             f"within representation. Generation at list price; ${judge:g} is the measured cost of the automated "
             f"judge per idea; ${HUMAN:.2f} is about 30 seconds of human reading at $60 an hour. Bold: cheapest, or "
             f"indistinguishable from the cheapest."]
    for row in rows:
        if row["break_even_vs_ref"] != "":
            notes.append(f"{row['model']} becomes cheaper than {names[args.reference]} once screening costs more than "
                         f"${row['break_even_vs_ref']:.4f} per idea (95% CI ${row['break_even_lo']:.4f}–"
                         f"${row['break_even_hi']:.4f}).")
        elif row["model"] != names[args.reference] and args.reference in have:
            ideas, top, usd = point[next(k for k in have if names[k] == row["model"])]
            ri, rt, ru = point[args.reference]
            how = ("cheaper at every screening cost" if usd / top <= ru / rt and ideas / top <= ri / rt else
                   "dearer at every screening cost" if usd / top >= ru / rt and ideas / top >= ri / rt else
                   f"cheaper only while screening costs less than "
                   f"${(ru / rt - usd / top) / (ideas / top - ri / rt):.4f} per idea")
            notes.append(f"{row['model']} against {names[args.reference]}: {how}.")
    out.with_suffix(".md").write_text("\n".join(md) + "\n\n" + "\n\n".join(notes) + "\n", encoding="utf-8")
    out.with_suffix(".tex").write_text("\n".join(tex) + "\n", encoding="utf-8")

    print()
    print("\n".join(md))
    print()
    print("\n".join(notes[1:]))
    print(f"-> results/{out.name}.csv, .md, .tex")


if __name__ == "__main__":
    main()
