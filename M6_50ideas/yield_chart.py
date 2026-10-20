#!/usr/bin/env python3
"""
yield_chart.py: the main study's Figure 8 (top ideas found against tokens spent) for the 50-idea run.

  cd M6_50ideas
  python yield_chart.py            # after score_ideas.py table; no API calls, no codebook needed
  GEN_MODEL=opus python yield_chart.py   # the same for the Opus run (results/opus/charts/)

Same definitions and drawing code as ../tail_charts.py (chart 8): a top idea scores >= 4.0 (mean of the
four blind criteria), the yield of an arm is all its top ideas / all its tokens (top ideas per 100k
tokens, the slope of a line through the origin), and the 95% CI comes from 2,000 bootstrap resamples
of calls. Here every arm is one need (M6) at medium effort, asked for 50 ideas per call; all ideas of
a call and all its tokens are counted.

Also draws a three-pane version: pane 1 the same running count and fitted lines, pane 2 a box plot of
each arm's slopes, pane 3 the ranked key and the prompt thumbnails. By default the boxes show the slope of
every single call (its top ideas / its tokens, 10 per arm, all drawn as dots); --box bootstrap shows the
2,000 bootstrap slopes behind the 95% CI instead (as the main study's chart 8b). The triangle is the arm's
pooled slope, the slope of its line in pane 1.

Writes results/charts/8_top_ideas_vs_tokens_m6_50ideas.png (and ..._box.png) and results/yield_m6_50ideas.csv, and prints
the main study's M6 yields (5 ideas per call) for reference. The two are not directly comparable: asked
for 50, the model writes shorter ideas (about 40 words, against about 100), which the judge scores lower.
"""
from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from common import CONDITIONS, GEN_MODEL, GEN_SUFFIX, NEED, RESULTS, ROOT, RUNS, load_calls

sys.path.insert(0, str(ROOT))
import m6_thumb  # noqa: E402
import tail_charts as tc  # noqa: E402  (the main study's chart code, reused unchanged)

EFFORT = "medium"
FIG_SIZE = (15, 6.4)
PANES = {"curve": (0.05, 0.47), "box": (0.535, 0.665), "key": 0.70}   # left/right edges, figure fractions
PLOT_BOTTOM, PLOT_TOP = 0.12, 0.76
THUMB_WIDTH = 0.22                 # figure fraction; keeps the thumbnail above the bottom edge


def call_slope(call: dict, th: float) -> float:
    return 1e5 * sum(s >= th for s in call["scores"]) / call["tokens"] if call["tokens"] else float("nan")


def chart_yield_box(rows, groups, th, box_kind, draws, sub_note, tag):
    """Pane 1: running count + fitted lines (as chart 8). Pane 2: box plot of slopes. Pane 3: key + thumbnail."""
    fig = plt.figure(figsize=FIG_SIZE)
    ax = fig.add_axes([PANES["curve"][0], PLOT_BOTTOM, PANES["curve"][1] - PANES["curve"][0], PLOT_TOP - PLOT_BOTTOM])
    bx = fig.add_axes([PANES["box"][0], PLOT_BOTTOM, PANES["box"][1] - PANES["box"][0], PLOT_TOP - PLOT_BOTTOM])
    ranked = sorted(rows, key=lambda r: -r["yield_per_100k"])
    x_max = y_max = 0
    for r in rows:
        c = r["condition"]
        pn, col = groups[(c, EFFORT)], tc.COND.get(c, tc.MUTED)
        xs, ys, tx, ty = [0.0], [0], 0.0, 0
        for call in tc.interleaved(pn):
            tx += call["tokens"]
            ty += sum(s >= th for s in call["scores"])
            xs.append(tx / 1e6)
            ys.append(ty)
        ax.step(xs, ys, where="post", color=col, linewidth=0.9, alpha=0.35, zorder=1)
        end = r["yield_per_100k"] * xs[-1] * 10
        ax.plot([0, xs[-1]], [0, end], color=col, linewidth=2.0, linestyle=tc.CURVE_STYLE[EFFORT], zorder=2)
        ax.scatter([xs[-1]], [end], s=42, zorder=3, **tc.mark_style(EFFORT, col, 1.5, fill=tc.SURFACE))
        x_max, y_max = max(x_max, xs[-1]), max(y_max, ys[-1], end)
    ax.set_xlim(0, x_max * 1.04)
    ax.set_ylim(0, y_max * 1.08)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}M"))
    ax.set_xlabel("tokens spent (input + output, summed over the arm's calls), millions")
    ax.set_ylabel(f"top ideas found (score ≥ {th:g})")
    ax.grid(color=tc.GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title("Top ideas found per token spent", loc="left", fontsize=11, color=tc.INK, pad=8)

    # pane 2: one box per arm, steepest first, same colours
    data = [[call_slope(x, th) for cs in groups[(r["condition"], EFFORT)].values() for x in cs]
            if box_kind == "calls" else draws[r["condition"]] for r in ranked]
    pos = list(range(1, len(ranked) + 1))
    bp = bx.boxplot(data, positions=pos, widths=0.55, whis=(2.5, 97.5) if box_kind == "bootstrap" else 1.5,
                    showfliers=False, patch_artist=True, medianprops={"linewidth": 1.6})
    rng = random.Random(1)
    for i, (r, d) in enumerate(zip(ranked, data)):
        col = tc.COND.get(r["condition"], tc.MUTED)
        bp["boxes"][i].set(facecolor=col + "22", edgecolor=col, linewidth=1.3)
        bp["medians"][i].set(color=col)
        for k in ("whiskers", "caps"):
            for line in bp[k][2 * i:2 * i + 2]:
                line.set(color=col, linewidth=1.1)
        if box_kind == "calls":
            bx.scatter([pos[i] + rng.uniform(-0.16, 0.16) for _ in d], d, s=14, color=col, alpha=0.75,
                       linewidths=0, zorder=3)
        bx.scatter([pos[i]], [r["yield_per_100k"]], s=60, zorder=4, **tc.mark_style(EFFORT, col, 1.6, fill=tc.SURFACE))
    bx.set_xticks(pos, [tc.SPREAD_NAMES.get(r["condition"], r["condition"]).replace(" ", "\n") for r in ranked],
                  fontsize=8.5)
    for lab, r in zip(bx.get_xticklabels(), ranked):
        lab.set_color(tc.COND.get(r["condition"], tc.MUTED))
        lab.set_fontweight("bold")
    bx.set_ylim(bottom=0)
    bx.set_ylabel("top ideas per 100k tokens")
    bx.grid(axis="y", color=tc.GRID, linewidth=0.8)
    bx.set_axisbelow(True)
    bx.set_title("Spread of the slopes", loc="left", fontsize=11, color=tc.INK, pad=8)
    what = ("box = one dot per call: that call's top ideas ÷ its tokens (whiskers 1.5 × IQR)"
            if box_kind == "calls" else "box = 2,000 bootstrap slopes: box middle 50%, whiskers 95% CI")

    # pane 3: ranked key, then the thumbnail of what each prompt contains
    x0, y = PANES["key"], PLOT_TOP + 0.005
    fig.text(x0, y, "Top ideas per 100k tokens  [95% CI]", fontsize=8.5, color=tc.INK, fontweight="bold", va="top")
    for i, r in enumerate(ranked, 1):
        col = tc.COND.get(r["condition"], tc.MUTED)
        yy = y - 0.045 * i
        fig.text(x0, yy, f"{r['yield_per_100k']:4.1f}  [{r['yield_lo']:.1f}–{r['yield_hi']:.1f}]", fontsize=8.5,
                 color=tc.INK, va="top", family="monospace")
        fig.text(x0 + 0.105, yy, f"{tc.SPREAD_NAMES.get(r['condition'], r['condition'])} · {EFFORT}", fontsize=8.5,
                 color=col, fontweight="bold", va="top")
    tc.add_slices_thumbnail(fig, (x0, 0, THUMB_WIDTH), top=y - 0.045 * len(ranked) - 0.06)

    fig.text(PANES["curve"][0], 0.98, "Top ideas found per token spent, and how much the slope varies",
             fontsize=13, fontweight="bold", color=tc.INK, va="top")
    fig.text(PANES["curve"][0], 0.935,
             "Left: faint steps = observed running count · dashed line = fit through the origin, "
             "slope = all top ideas ÷ all tokens\nMiddle: " + what + " · triangle = the pooled slope "
             "(the line on the left)" + sub_note, fontsize=9, color=tc.INK2, va="top", linespacing=1.4)
    fig.patch.set_facecolor(tc.SURFACE)
    for a in (ax, bx):
        a.set_facecolor(tc.SURFACE)
    name = f"8_top_ideas_vs_tokens{tag}_box{'' if box_kind == 'calls' else '_bootstrap'}.png"
    fig.savefig(tc.OUT / name, dpi=200, facecolor=tc.SURFACE)
    plt.close(fig)
    print(f"  {tc.OUT / name}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--threshold", type=float, default=4.0)
    ap.add_argument("--scores", default=str(RESULTS / "ideas_scored.csv"))
    ap.add_argument("--box", choices=["calls", "bootstrap"], default="calls",
                    help="what the box plot shows: each call's slope (default) or the bootstrap slopes")
    args = ap.parse_args()

    runs = {k: c for k, c in load_calls([RUNS]).items() if c.get("target_need") == NEED}
    gen = ", ".join(sorted({str(c.get("model", "?")) for c in runs.values()}))   # the model that wrote the ideas
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
    rows, draws = [], {}
    for c in CONDITIONS:
        pn = groups.get((c, EFFORT))
        if not pn:
            continue
        lo, hi, draws[c] = tc.bootstrap_yield(pn, args.threshold, rng)
        n_ideas = sum(len(x["scores"]) for cs in pn.values() for x in cs)
        n_top = sum(s >= args.threshold for cs in pn.values() for x in cs for s in x["scores"])
        toks = sum(x["tokens"] for cs in pn.values() for x in cs)
        rows.append({"condition": c, "effort": EFFORT, "calls": sum(len(cs) for cs in pn.values()), "ideas": n_ideas,
                     "top_ideas": n_top, "top_idea_rate": round(n_top / n_ideas, 3), "tokens": toks,
                     "yield_per_100k": tc.yield_per_100k(pn, args.threshold), "yield_lo": lo, "yield_hi": hi})

    # the main study's drawing code, pointed at this study's folder and arms
    tc.OUT = RESULTS / "charts"
    tc.OUT.mkdir(parents=True, exist_ok=True)
    tc.THUMB = m6_thumb.path()                        # the four M6 prompts this study sent (m6_thumb.py)
    tc.CURVE_ARMS = [(c, EFFORT) for c in CONDITIONS]
    tag = "_m6_50ideas" + GEN_SUFFIX + ("" if args.threshold == 4.0 else f"_ge{args.threshold:g}")
    tc.chart_yield(rows, groups, args.threshold,
                   f"\n{NEED} only · ideas by {gen} · 50 asked per call · {EFFORT} effort · "
                   f"{rows[0]['calls']} calls per arm", tag=tag)
    chart_yield_box(rows, groups, args.threshold, args.box, draws,
                    f"\n{NEED} only · ideas by {gen} · 50 asked per call · {EFFORT} effort · {rows[0]['calls']} calls per arm",
                    tag)

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
    print(f"-> {tc.OUT.relative_to(ROOT)}/8_top_ideas_vs_tokens{tag}*.png, "
          f"{(RESULTS / f'yield{tag}.csv').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
