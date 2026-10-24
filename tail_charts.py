#!/usr/bin/env python3
"""
tail_charts.py: which arm finds the *great* ideas? Looks at the top tail of the blind idea scores, not the mean.

  python tail_charts.py                 # reads results/ideas_ranked.csv, writes results/charts/6_*.png, 7_*.png
  python tail_charts.py --threshold 4.25

A "top idea" is one whose blind individual score (top_ideas.py, mean of 4 criteria) reaches THRESHOLD.
Scores move in 0.25 steps, so an exact "top 10%" does not exist: the script prints which share of all
ideas the threshold actually keeps (>= 4.0 was the top 12.3% in the full run, >= 4.25 the top 2.4%).

Charts
  6_top_idea_rate.png      share of each arm's ideas that are top ideas, 95% CI (bootstrap over calls within need)
  7_chance_vs_budget.png   chance of at least one top idea for a given token budget, per arm
  8b_yield_spread.png      the spread of each arm's slope: box plot of its 2,000 bootstrap slopes (box = middle
                           50%, whiskers = 95% CI), with the chance that each arm's slope beats the next one's
  8c_yield_spread_annotated.png  the same, with a line at the no-graph slope and two notes (SPREAD_* settings)
  9_slice_size_effect.png  per market need: the need slice's yield divided by the full graph's, against the
                           size of the slice (needs --manifest, default slices/manifest.csv)
  8_top_ideas_vs_tokens.png  cumulative count of top ideas against tokens spent, per arm; the slope of each
                           line (top ideas per 100k tokens) is the arm's yield, and does not saturate
  8d_yield_with_spread.png  chart 8 and 8b in one figure: pane 1 the running counts and fitted lines, pane 2
                           a box plot of each arm's 2,000 bootstrap slopes, pane 3 the ranked key and thumbnail
  8d_yield_with_spread_calls.png  the same, but pane 2 shows each call's own slope (its top ideas / its tokens,
                           one dot per call); with 5 ideas a call, most calls have 0 or 1 top idea

Also writes results/tail_summary.csv with every number in the charts. Runs with another --threshold or
with --match-needs add a tag to every file name (e.g. 6_top_idea_rate_ge4.25_matched.png).

Needs differ a lot in how easy a top idea is, so every rate is the mean of per-need rates (each need
weighs the same), and the bootstrap resamples calls within each need. xhigh was only run on 6 needs;
its rows are marked, and --match-needs restricts every arm to those needs for a like-for-like check.
"""
from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# shared look: same colours, effort symbols, fonts and save routine as charts.py
from charts import (AXIS, COND, COND_NAME, EFFORT_MARKER, EFFORTS, GRID, INK, INK2, MUTED, OUT, RESULTS,
                    SURFACE, finish, mark_style, num, read_csv)
import matplotlib

# ── Settings ────────────────────────────────────────────────────────
THRESHOLD = 4.0               # score a top idea must reach (4.0 ≈ top 12%, 4.25 ≈ top 2.4% in the full run)
COND_ORDER = ["C", "R", "B", "A"]      # chart 6 rows, top to bottom by group
BOOTSTRAP = 2000              # resamples for the 95% CI
SEED = 0
# chart 7: which arms get a curve, and the largest budget shown (tokens)
CURVE_ARMS = [("C", "high"), ("R", "high"), ("B", "medium"), ("B", "high"), ("A", "high"),
              ("B", "xhigh"), ("A", "xhigh")]
BUDGET_MAX = 120_000
# chart 8b: reference line at C's slope, and two arrow-shaped notes (set to None to leave them out)
SPREAD_REFERENCE = ("C", "high")
# each note: (condition, effort of the row it sits on, centre x in slope units, text)
SPREAD_NOTE_WORSE = ("A", "low", 8.0, "Adding the full knowledge graph to the prompt made top-idea generation "
                                      "less efficient than no graph at all")
SPREAD_NOTE_BETTER = ("B", "low", 2.0, "Giving only the relevant slice was more efficient than giving the full graph")
SPREAD_NOTE_WRAP = 30            # characters per line in the notes
# y-axis names in the slope-spread charts (8b, 8c); other charts keep the letter codes
SPREAD_THUMB_RIGHT = 0.73       # chart 8c: right edge of the plot when the thumbnail column is added
SPREAD_NAMES = dict(COND_NAME)   # "A · full graph", ...: the same names as charts 1 and 5
KEY_POS = (1.03, 0.98)        # chart 8: top-left corner of the slope key, in axes fractions (>1 = right of plot)
CURVE_STYLE = {"low": (0, (1, 2)), "medium": (0, (5, 2)), "high": "-", "xhigh": "-", "max": "-"}


def load(path):
    """run_id -> dict(condition, effort, need, tokens, scores)."""
    calls = {}
    for r in read_csv(path):
        sc = num(r.get("score"))
        if sc is None:
            continue
        c = calls.setdefault(r["run_id"], {"run_id": r["run_id"], "condition": r["condition"], "effort": r["effort"],
                                           "need": r["target_need"], "scores": [],
                                           "tokens": (num(r.get("run_input_tokens")) or 0)
                                                     + (num(r.get("run_output_tokens")) or 0)})
        c["scores"].append(sc)
    return calls


def by_arm_need(calls, needs=None):
    out = defaultdict(lambda: defaultdict(list))        # (cond, effort) -> need -> [call]
    for c in calls.values():
        if needs is None or c["need"] in needs:
            out[(c["condition"], c["effort"])][c["need"]].append(c)
    return out


def rates(per_need, th):
    """Need-balanced rates for one arm: idea share, call share (>=1 top idea), mean tokens per call."""
    idea, call, tok = [], [], []
    for cs in per_need.values():
        n_ideas = sum(len(c["scores"]) for c in cs)
        idea.append(sum(s >= th for c in cs for s in c["scores"]) / n_ideas)
        call.append(sum(any(s >= th for s in c["scores"]) for c in cs) / len(cs))
        tok.append(sum(c["tokens"] for c in cs) / len(cs))
    k = len(per_need)
    return sum(idea) / k, sum(call) / k, sum(tok) / k


def bootstrap(per_need, th, rng, reps=BOOTSTRAP):
    """95% CI of the idea share and call share: resample calls within each need."""
    ideas, calls_ = [], []
    for _ in range(reps):
        res = {n: [rng.choice(cs) for _ in cs] for n, cs in per_need.items()}
        i, c, _ = rates(res, th)
        ideas.append(i)
        calls_.append(c)
    q = lambda v: (sorted(v)[int(0.025 * reps)], sorted(v)[int(0.975 * reps) - 1])
    return q(ideas), q(calls_)


def yield_per_100k(per_need, th):
    """Top ideas per 100k tokens: all top ideas / all tokens (the slope of a line through the origin)."""
    hits = sum(s >= th for cs in per_need.values() for c in cs for s in c["scores"])
    toks = sum(c["tokens"] for cs in per_need.values() for c in cs)
    return 1e5 * hits / toks if toks else float("nan")


def bootstrap_yield(per_need, th, rng, reps=BOOTSTRAP):
    """95% CI of the yield: resample calls within each need, keeping each call's ideas and tokens together."""
    draws = [yield_per_100k({n: [rng.choice(cs) for _ in cs] for n, cs in per_need.items()}, th)
             for _ in range(reps)]
    vals = sorted(draws)
    # the raw draws keep their random order, so two arms' draws can be paired as independent samples
    return vals[int(0.025 * reps)], vals[int(0.975 * reps) - 1], draws


def interleaved(per_need):
    """Calls in a need-balanced order: replicate 1 of every need, then replicate 2, and so on."""
    needs = sorted(per_need)
    out = []
    # ideas_ranked.csv lists ideas best first, so sort each need's calls by run id (i.e. replicate)
    ordered = {n: sorted(cs, key=lambda c: c["run_id"]) for n, cs in per_need.items()}
    for k in range(max(len(cs) for cs in ordered.values())):
        out += [ordered[n][k] for n in needs if k < len(ordered[n])]
    return out


def chance_after(per_need, th, k):
    """P(at least one top idea) after k calls of this arm, averaged over needs.

    Within a need, calls are treated as independent draws: k calls succeed with 1 - (1 - p)^k. With only
    5 calls per need, the raw share is often exactly 0 or 1, which would mean "never" or "always", so p
    uses the Jeffreys estimate (hits + 1/2) / (calls + 1) instead.
    """
    vals = []
    for cs in per_need.values():
        hits = sum(any(s >= th for s in c["scores"]) for c in cs)
        p = (hits + 0.5) / (len(cs) + 1)
        vals.append(1 - (1 - p) ** k)
    return sum(vals) / len(vals)


def arm_label(c, e, xhigh_needs):
    return f"{c} · {e}" + (f" ({xhigh_needs} needs)" if xhigh_needs else "")


def legend_marker(effort, color):
    """Line2D marker kwargs matching mark_style: strokes as lines, closed shapes as open outlines."""
    from charts import LINE_MARKERS, SURFACE as _S
    m = EFFORT_MARKER.get(effort, "o")
    if m in LINE_MARKERS:
        return {"marker": m, "markeredgecolor": color, "markeredgewidth": 1.3}
    return {"marker": m, "markerfacecolor": _S, "markeredgecolor": color, "markeredgewidth": 1.3}


# ── 6. Top-idea rate per arm ────────────────────────────────────────
def chart_rate(rows, th, kept, sub_note, tag=""):
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(rows) + 1.9))
    ys = list(range(len(rows)))[::-1]
    base = kept
    ax.axvline(base, color=AXIS, linewidth=1.2, linestyle=(0, (4, 3)), zorder=0)
    ax.text(base, len(rows) - 0.35, f" all ideas: {base:.1%}", color=MUTED, fontsize=8, va="bottom")
    xmax = max(r["idea_hi"] for r in rows) * 1.12
    for y, r in zip(ys, rows):
        col = COND.get(r["condition"], MUTED)
        ax.plot([r["idea_lo"], r["idea_hi"]], [y, y], color=col, linewidth=2.2, solid_capstyle="round", zorder=1)
        ax.scatter([r["idea_rate"]], [y], s=70, zorder=3, **mark_style(r["effort"], col, 1.8, fill=SURFACE))
        ax.text(xmax * 1.01, y, f"{r['idea_rate']:.1%}   {r['hits']}/{r['ideas']}   "
                                f"{r['tokens_per_hit'] / 1000:.0f}k tok/hit",
                va="center", fontsize=8.5, color=INK)
    ax.set_yticks(ys, [r["label"].replace(r["condition"] + " ·", SPREAD_NAMES.get(r["condition"], r["condition"]) + " ·", 1)
                       for r in rows])
    for lab, r in zip(ax.get_yticklabels(), rows):
        lab.set_color(INK)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, xmax)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_ylim(-0.7, len(rows) - 0.2)
    ax.set_xlabel(f"share of the arm's ideas scoring ≥ {th:g} (mean over needs) · bar = 95% CI")
    ax.set_title(f"Top-idea rate per arm (score ≥ {th:g}, the top {kept:.0%} of all ideas)")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    fig.subplots_adjust(right=0.7)
    finish(fig, ax, f"6_top_idea_rate{tag}.png",
           "Colour = condition · symbol = effort · right: rate, top ideas / ideas, tokens spent per top idea"
           + sub_note)


# ── 7. Chance of a top idea vs budget ───────────────────────────────
def chart_budget(groups, th, kept, sub_note, tag=""):
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ends = []
    for c, e in CURVE_ARMS:
        pn = groups.get((c, e))
        if not pn:
            continue
        col = COND.get(c, MUTED)
        tok = rates(pn, th)[2]
        # whole calls only (a budget buys a whole number of calls), starting from nothing spent
        ks = list(range(0, int(BUDGET_MAX // tok) + 1))
        xs = [k * tok / 1000 for k in ks]
        ys = [chance_after(pn, th, k) for k in ks]
        ax.plot(xs, ys, color=col, linewidth=1.8, linestyle=CURVE_STYLE.get(e, "-"), zorder=2)
        ax.scatter(xs[1:], ys[1:], s=28, zorder=3, **mark_style(e, col, 1.3, fill=SURFACE))
        most = max(len(v) for v in groups.values())
        ends.append((ys[-1], f"{SPREAD_NAMES.get(c, c)} · {e}" + (f" ({len(pn)} needs)" if len(pn) < most else ""), col, xs[-1], e))
    # direct labels at the right edge, nudged apart so they don't overlap
    # legend outside the plot, in the order the curves end (highest first), with each curve's
    # colour, line style and effort symbol, so arms of the same colour stay distinguishable
    ends.sort(key=lambda t: -t[0])
    handles = [Line2D([], [], color=col, linewidth=1.8, linestyle=CURVE_STYLE.get(eff, "-"),
                      markersize=6, **legend_marker(eff, col)) for _, _, col, _, eff in ends]
    ax.legend(handles, [lab for _, lab, _, _, _ in ends], loc="upper left", bbox_to_anchor=(1.02, 1.0),
              frameon=False, fontsize=8.5, handlelength=2.6, borderaxespad=0)
    ax.set_xlim(0, BUDGET_MAX / 1000)
    ax.set_ylim(0, 1.0)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}k"))
    ax.set_xlabel("token budget (input + output, summed over calls)")
    ax.set_ylabel(f"chance of at least one idea scoring ≥ {th:g}")
    ax.set_title("Chance of a top idea for a given budget")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    fig.subplots_adjust(right=0.74)
    finish(fig, ax, f"7_chance_vs_budget{tag}.png",
           "Each symbol = one more call · chance = 1 − (1 − p)^calls per need, averaged over needs\n"
           "p = that need's share of calls with ≥ 1 top idea, (hits + ½) / (calls + 1)" + sub_note,
           after_layout=thumbnail_below_legend if THUMB.exists() else None)


# ── 8. Top ideas against tokens spent ───────────────────────────────
THUMB = OUT / "0b_slices_grid_thumb.png"   # from figure_slices_grid.py; drawn under the key of chart 8 if present
THUMB_BOX = (0.69, 0.11, 0.28)     # left, bottom, width of the thumbnail, in figure fractions


def add_slices_thumbnail(fig, box=None, top=None):
    """A thumbnail of the 4 x 4 grid of what each prompt contains, so the reader sees what 'full graph',
    'slice', 'random graph' and 'no graph' mean next to the arms. box = (left, bottom, width) in figure
    fractions; or give top instead of bottom (box[1] ignored) to hang the thumbnail from that height."""
    if not THUMB.exists():
        return
    img = plt.imread(THUMB)
    left, bottom, width = box or THUMB_BOX
    fw, fh = fig.get_size_inches()
    height = width * fw / fh * img.shape[0] / img.shape[1]
    if top is not None:
        bottom = top - (0.035 if width * fw >= 2.6 else 0.06) - height
    iax = fig.add_axes([left, bottom, width, height])
    iax.imshow(img, interpolation="lanczos")
    iax.set_axis_off()
    label = "What each prompt contains (coloured = what the model sees):"
    if width * fw < 2.6:                                # narrow column: two lines
        label = "What each prompt contains\n(coloured = what the model sees):"
    fig.text(left, bottom + height + 0.012, label, fontsize=7.5, color=INK2, va="bottom", linespacing=1.3)


def thumbnail_below_legend(fig, ax):
    """Chart 7: hang the thumbnail under the legend that sits right of the plot."""
    leg = ax.get_legend()
    fig.canvas.draw()
    bb = leg.get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
    left = bb.x0 + 0.005
    add_slices_thumbnail(fig, (left, 0, 0.985 - left), top=bb.y0 - 0.03)


def thumbnail_right_column(fig, ax):
    """Chart 8c: make room right of the plot and put the thumbnail there, level with the plot's top."""
    fig.subplots_adjust(right=SPREAD_THUMB_RIGHT)
    pos = ax.get_position()
    left = SPREAD_THUMB_RIGHT + 0.02
    add_slices_thumbnail(fig, (left, 0, 0.985 - left), top=pos.y1)


def chart_yield(rows, groups, th, sub_note, tag=""):
    """Cumulative top ideas vs cumulative tokens. Unlike a probability, a count does not saturate: the
    slope of each arm's line is its yield, top ideas per 100k tokens, and arms are compared by slope."""
    fig, ax = plt.subplots(figsize=(10, 5.6))
    by_arm = {(r["condition"], r["effort"]): r for r in rows}
    most = max(len(v) for v in groups.values())
    key = []
    x_max = y_max = 0
    for c, e in CURVE_ARMS:
        pn, r = groups.get((c, e)), by_arm.get((c, e))
        if not pn or not r:
            continue
        col = COND.get(c, MUTED)
        # observed path: calls in need-balanced order, cumulative tokens and top ideas
        xs, ys, tx, ty = [0.0], [0], 0.0, 0
        for call in interleaved(pn):
            tx += call["tokens"]
            ty += sum(s >= th for s in call["scores"])
            xs.append(tx / 1e6)
            ys.append(ty)
        ax.step(xs, ys, where="post", color=col, linewidth=0.9, alpha=0.35, zorder=1)
        # fitted line through the origin: slope = yield
        slope = r["yield_per_100k"]
        ax.plot([0, xs[-1]], [0, slope * xs[-1] * 10], color=col, linewidth=2.0,
                linestyle=CURVE_STYLE.get(e, "-"), zorder=2)
        ax.scatter([xs[-1]], [slope * xs[-1] * 10], s=42, zorder=3, **mark_style(e, col, 1.5, fill=SURFACE))
        x_max, y_max = max(x_max, xs[-1]), max(y_max, ys[-1], slope * xs[-1] * 10)
        few = f" ({len(pn)} needs)" if len(pn) < most else ""
        key.append((slope, f"{SPREAD_NAMES.get(c, c)} · {e}{few}", r["yield_lo"], r["yield_hi"], col))

    # ranked key in the empty lower-right corner (below the shallow lines): steepest line first
    key.sort(reverse=True)
    x0, y0, dy = KEY_POS[0], KEY_POS[1], 0.05
    ax.text(x0, y0 + 0.01, f"Top ideas per 100k tokens  [95% CI]", transform=ax.transAxes,
            fontsize=8.5, color=INK, fontweight="bold", va="top", zorder=6)
    for i, (slope, lab, lo, hi, col) in enumerate(key, 1):
        y = y0 + 0.01 - dy * i
        ax.text(x0, y, f"{slope:4.1f}  [{lo:.1f}–{hi:.1f}]", transform=ax.transAxes,
                fontsize=8.5, color=INK, va="top", family="monospace", zorder=6)
        ax.text(x0 + 0.215, y, lab, transform=ax.transAxes, fontsize=8.5, color=col,
                fontweight="bold", va="top", zorder=6)
    ax.set_xlim(0, x_max * 1.04)
    ax.set_ylim(0, y_max * 1.08)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}M"))
    ax.set_xlabel("tokens spent (input + output, summed over the arm's calls), millions")
    ax.set_ylabel(f"top ideas found (score ≥ {th:g})")
    ax.set_title("Top ideas found per token spent")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    # like charts.finish, but the key sits right of the plot, so leave that strip free
    sub = ("Faint steps = observed running count, calls in need-balanced order · line = fit through the origin\n"
           "Slope = all top ideas ÷ all tokens, 95% CI by resampling calls within need" + sub_note)
    ax.set_title(ax.get_title(loc="left"), loc="left", pad=24 + 13 * sub.count("\n"))
    ax.text(0, 1.015, sub, transform=ax.transAxes, color=INK2, fontsize=9, va="bottom")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    fig.subplots_adjust(left=0.07, right=0.66, top=0.83, bottom=0.11)   # fixed: tight_layout would squeeze
                                                                       # the plot to make room for the key
    add_slices_thumbnail(fig)
    name = f"8_top_ideas_vs_tokens{tag}.png"
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)
    print(f"  {OUT / name}")

# ── 8d. Chart 8 with the spread of the slopes ───────────────────────
BOX_FIG = (16, 7.0)
BOX_PANES = {"curve": (0.05, 0.43), "box": (0.49, 0.69), "key": 0.72}   # edges, figure fractions
BOX_PLOT = (0.19, 0.79)                     # bottom, top of both plots
BOX_THUMB_WIDTH = 0.19


def call_slope(call, th):
    return 1e5 * sum(s >= th for s in call["scores"]) / call["tokens"] if call["tokens"] else float("nan")


def chart_yield_box(rows, groups, th, sub_note, tag="", box_kind="bootstrap"):
    """Pane 1: running count + fitted lines (as chart 8). Pane 2: box plot of the slopes, steepest arm first:
    the 2,000 bootstrap slopes (box_kind="bootstrap", as chart 8b) or each call's slope ("calls").
    Pane 3: ranked key and the thumbnail of what each prompt contains."""
    by_arm = {(r["condition"], r["effort"]): r for r in rows}
    arms = [by_arm[a] for a in CURVE_ARMS if a in by_arm and groups.get(a)]
    if not arms:
        return
    ranked = sorted(arms, key=lambda r: -r["yield_per_100k"])
    most = max(len(v) for v in groups.values())
    fig = plt.figure(figsize=BOX_FIG)
    (cl, cr), (bl, br), (pb, pt) = BOX_PANES["curve"], BOX_PANES["box"], BOX_PLOT
    ax = fig.add_axes([cl, pb, cr - cl, pt - pb])
    bx = fig.add_axes([bl, pb, br - bl, pt - pb])
    x_max = y_max = 0
    for r in arms:
        c, e = r["condition"], r["effort"]
        pn, col = groups[(c, e)], COND.get(c, MUTED)
        xs, ys, tx, ty = [0.0], [0], 0.0, 0
        for call in interleaved(pn):
            tx += call["tokens"]
            ty += sum(s >= th for s in call["scores"])
            xs.append(tx / 1e6)
            ys.append(ty)
        ax.step(xs, ys, where="post", color=col, linewidth=0.9, alpha=0.35, zorder=1)
        end = r["yield_per_100k"] * xs[-1] * 10
        ax.plot([0, xs[-1]], [0, end], color=col, linewidth=2.0, linestyle=CURVE_STYLE.get(e, "-"), zorder=2)
        ax.scatter([xs[-1]], [end], s=42, zorder=3, **mark_style(e, col, 1.5, fill=SURFACE))
        x_max, y_max = max(x_max, xs[-1]), max(y_max, ys[-1], end)
    ax.set_xlim(0, x_max * 1.04)
    ax.set_ylim(0, y_max * 1.08)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}M"))
    ax.set_xlabel("tokens spent (input + output, summed over the arm's calls), millions")
    ax.set_ylabel(f"top ideas found (score ≥ {th:g})")
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title("Top ideas found per token spent", loc="left", fontsize=11, color=INK, pad=8)

    data = [[call_slope(x, th) for cs in groups[(r["condition"], r["effort"])].values() for x in cs]
            if box_kind == "calls" else r["yield_boot"] for r in ranked]
    pos = list(range(1, len(ranked) + 1))
    bp = bx.boxplot(data, positions=pos, widths=0.6, whis=(2.5, 97.5) if box_kind == "bootstrap" else 1.5,
                    showfliers=False, patch_artist=True, medianprops={"linewidth": 1.6})
    jitter = random.Random(1)
    for i, (r, d) in enumerate(zip(ranked, data)):
        col = COND.get(r["condition"], MUTED)
        bp["boxes"][i].set(facecolor=col + "22", edgecolor=col, linewidth=1.3)
        bp["medians"][i].set(color=col)
        for k in ("whiskers", "caps"):
            for line in bp[k][2 * i:2 * i + 2]:
                line.set(color=col, linewidth=1.1)
        if box_kind == "calls":
            bx.scatter([pos[i] + jitter.uniform(-0.18, 0.18) for _ in d], d, s=10, color=col, alpha=0.6,
                       linewidths=0, zorder=3)
        bx.scatter([pos[i]], [r["yield_per_100k"]], s=55, zorder=4, **mark_style(r["effort"], col, 1.6, fill=SURFACE))
    bx.set_xticks(pos, [f"{SPREAD_NAMES.get(r['condition'], r['condition'])} · {r['effort']}" for r in ranked],
                  fontsize=8, rotation=45, ha="right", rotation_mode="anchor")
    for lab, r in zip(bx.get_xticklabels(), ranked):
        lab.set_color(COND.get(r["condition"], MUTED))
        lab.set_fontweight("bold")
    bx.set_ylim(bottom=0)
    bx.set_ylabel("top ideas per 100k tokens")
    bx.grid(axis="y", color=GRID, linewidth=0.8)
    bx.set_axisbelow(True)
    bx.set_title("Spread of the slopes", loc="left", fontsize=11, color=INK, pad=8)
    what = ("box = one dot per call: that call's top ideas ÷ its tokens (whiskers 1.5 × IQR)" if box_kind == "calls"
            else "box = 2,000 bootstrap slopes (calls resampled within need): middle 50%, whiskers 95% CI")

    x0, y = BOX_PANES["key"], pt + 0.005
    fig.text(x0, y, "Top ideas per 100k tokens  [95% CI]", fontsize=8.5, color=INK, fontweight="bold", va="top")
    for i, r in enumerate(ranked, 1):
        col, yy = COND.get(r["condition"], MUTED), y - 0.042 * i
        few = f" ({len(groups[(r['condition'], r['effort'])])} needs)" if len(groups[(r["condition"], r["effort"])]) < most else ""
        fig.text(x0, yy, f"{r['yield_per_100k']:4.1f}  [{r['yield_lo']:.1f}–{r['yield_hi']:.1f}]", fontsize=8.5,
                 color=INK, va="top", family="monospace")
        fig.text(x0 + 0.1, yy, f"{SPREAD_NAMES.get(r['condition'], r['condition'])} · {r['effort']}{few}",
                 fontsize=8.5, color=col, fontweight="bold", va="top")
    add_slices_thumbnail(fig, (x0, 0, BOX_THUMB_WIDTH), top=y - 0.042 * len(ranked) - 0.06)

    fig.text(cl, 0.98, "Top ideas found per token spent, and how much the slope varies", fontsize=13,
             fontweight="bold", color=INK, va="top")
    fig.text(cl, 0.935, "Left: faint steps = observed running count, calls in need-balanced order · line = fit through "
             "the origin, slope = all top ideas ÷ all tokens\nMiddle: " + what + " · symbol = the pooled slope "
             "(the line on the left)" + sub_note, fontsize=9, color=INK2, va="top", linespacing=1.4)
    fig.patch.set_facecolor(SURFACE)
    for a in (ax, bx):
        a.set_facecolor(SURFACE)
    name = f"8d_yield_with_spread{tag}{'' if box_kind == 'bootstrap' else '_calls'}.png"
    fig.savefig(OUT / name, dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print(f"  {OUT / name}")


# ── 8b. Spread of each arm's slope ──────────────────────────────────
def chart_yield_spread(rows, th, sub_note, tag="", annotated=False):
    """Box plot of each arm's bootstrap slopes, steepest first, so overlaps between arms are visible.
    Right of each box: the chance that this arm's slope is higher than the next arm's, from pairing the
    two arms' independent bootstrap draws (0.5 = indistinguishable, near 1 = clearly higher)."""
    arms = sorted((r for r in rows if r.get("yield_boot")), key=lambda r: -r["yield_per_100k"])
    if not arms:
        return
    fig, ax = plt.subplots(figsize=(14 if annotated else 9, 0.6 * len(arms) + 1.9))
    ys = list(range(len(arms)))[::-1]
    y_of = {(r["condition"], r["effort"]): y for y, r in zip(ys, arms)}
    ref = next((r["yield_per_100k"] for r in arms if (r["condition"], r["effort"]) == SPREAD_REFERENCE), None)
    if not annotated:
        ref = None
    if ref is not None:                               # the no-graph baseline, through the middle of C
        ax.axvline(ref, color=INK, linewidth=1.2, linestyle=(0, (5, 3)), zorder=4)
    for y, r in zip(ys, arms):
        col = COND.get(r["condition"], MUTED)
        kw = dict(positions=[y], widths=0.55, whis=(2.5, 97.5), showfliers=False, patch_artist=True,
                  manage_ticks=False)
        try:                                        # matplotlib >= 3.10
            bp = ax.boxplot([r["yield_boot"]], orientation="horizontal", **kw)
        except TypeError:                           # older matplotlib
            bp = ax.boxplot([r["yield_boot"]], vert=False, **kw)
        for b in bp["boxes"]:
            b.set(facecolor=col, alpha=0.35, edgecolor=col, linewidth=1.2)
        for k in ("whiskers", "caps"):
            for line in bp[k]:
                line.set(color=col, linewidth=1.2)
        for m in bp["medians"]:
            m.set(color=col, linewidth=2)
        ax.scatter([r["yield_per_100k"]], [y], s=34, zorder=3, **mark_style(r["effort"], col, 1.4, fill=SURFACE))
    x_right = max(r["yield_hi"] for r in arms) * 1.08
    import textwrap
    # worse-than-no-graph note points left (towards fewer top ideas per token), border in the full graph's
    # colour; better note points right, border in the need slice's colour
    for note, style, col in ((SPREAD_NOTE_WORSE, "larrow", COND.get("A", INK)),
                             (SPREAD_NOTE_BETTER, "rarrow", COND.get("B", INK))):
        if not note or ref is None or (note[0], note[1]) not in y_of:
            continue
        ax.text(note[2], y_of[(note[0], note[1])], textwrap.fill(note[3], SPREAD_NOTE_WRAP, break_on_hyphens=False), ha="center",
                va="center", fontsize=8.5, color=INK, zorder=6,
                bbox=dict(boxstyle=f"{style},pad=0.45", facecolor=SURFACE, edgecolor=col, linewidth=1.6))
    for i, (y, r) in enumerate(zip(ys, arms)):
        if i + 1 < len(arms):
            a, b = r["yield_boot"], arms[i + 1]["yield_boot"]
            p = sum(x > z for x, z in zip(a, b)) / len(a)
            ax.text(x_right, y - 0.5, f"{p:.2f}", va="center", ha="left", fontsize=8, color=INK2)
    ax.text(x_right, len(arms) - 0.45, "P(higher\nthan next)", va="bottom", ha="left", fontsize=8, color=INK2)
    ax.set_yticks(ys, [r["label"].replace(r["condition"] + " ·", SPREAD_NAMES.get(r["condition"], r["condition"]) + " ·", 1)
                       for r in arms])
    for lab in ax.get_yticklabels():
        lab.set_color(INK)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, x_right * 1.12)
    ax.set_ylim(-0.8, len(arms) + 0.15)
    ax.set_xlabel(f"top ideas (score ≥ {th:g}) per 100k tokens")
    ax.set_title("How far apart are the slopes?")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    finish(fig, ax, f"{'8c_yield_spread_annotated' if annotated else '8b_yield_spread'}{tag}.png",
           "Bootstrap slopes (2,000 resamples of calls within need) · box = middle 50% · whiskers = 95% CI\n"
           "Symbol = observed slope · right: chance this arm's slope beats the arm below it"
           + (" · dashed line = no graph" if annotated else "")
           + sub_note,
           after_layout=thumbnail_right_column if annotated and THUMB.exists() else None)


# ── 9. Slice size vs the slice's advantage, per market need ─────────
def chart_slice_size(groups, th, manifest, tag=""):
    """Does the need slice beat the full graph by more when the slice is small? One point per need:
    x = nodes in the need's slice (B), y = B's yield ÷ A's yield, at high and at medium effort."""
    if not manifest.exists():
        print(f"  (skipped 9_slice_size_effect.png: {manifest} not found)")
        return
    size = {r["target_need"]: int(r["n_nodes"]) for r in read_csv(manifest) if r["condition"] == "B"}

    def need_yield(arm, need):
        cs = groups.get(arm, {}).get(need, [])
        toks = sum(c["tokens"] for c in cs)
        return 1e5 * sum(s >= th for c in cs for s in c["scores"]) / toks if toks else None

    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.axhline(1, color=AXIS, linewidth=1.2, linestyle=(0, (4, 3)), zorder=0)
    ax.text(5.5, 1.03, "equal yield", color=MUTED, fontsize=8, va="bottom")
    lines, skipped = [], {}
    for effort, filled in (("high", True), ("medium", False)):
        pts = []
        for need in sorted(groups.get(("B", effort), {}), key=lambda n: int(n[1:])):
            yb, ya = need_yield(("B", effort), need), need_yield(("A", effort), need)
            if need in size and yb and ya:      # a ratio needs top ideas on both sides (log scale, no 0 or ∞)
                pts.append((size[need], yb / ya, need))
            elif need in size:
                skipped.setdefault(effort, []).append(need)
        if not pts:
            continue
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        ax.scatter(xs, ys, s=46, zorder=3, **mark_style(effort, COND["B"], 1.6,
                                                        fill=COND["B"] if filled else SURFACE))
        if filled:
            for x, y_, need in pts:
                ax.annotate(need, (x, y_), xytext=(6, 2), textcoords="offset points", fontsize=8, color=INK2)
        # least-squares line of log ratio on size, drawn back on the ratio scale
        import math
        lx = [math.log(v) for v in ys]
        mx, my = sum(xs) / len(xs), sum(lx) / len(lx)
        b = sum((a - mx) * (c - my) for a, c in zip(xs, lx)) / sum((a - mx) ** 2 for a in xs)
        xx = [min(xs), max(xs)]
        ax.plot(xx, [math.exp(my + b * (v - mx)) for v in xx], color=COND["B"], linewidth=1.4,
                linestyle="-" if filled else (0, (4, 2)), zorder=2)
        r = pearson_r(xs, lx)
        miss = skipped.get(effort)
        lines.append(f"{effort}: r = {r:+.2f}, n = {len(pts)}" + (f" ({', '.join(miss)} left out)" if miss else ""))
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator([0.5, 1, 2, 4, 8]))
    ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}×"))
    ax.set_xlim(5, 58)
    ax.set_xlabel("nodes in the need's slice (B), of 123 in the full graph")
    ax.set_ylabel("need slice yield ÷ full graph yield (log scale)")
    ax.set_title("Need slice's efficiency advantage by slice size")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    finish(fig, ax, f"9_slice_size_effect{tag}.png",
           f"One point per need · yield = top ideas (score ≥ {th:g}) per 100k tokens · filled = high effort, open = medium\n"
           "Lines = least-squares fit of log ratio on slice size · correlation with size:\n" + "; ".join(lines))


def pearson_r(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sx = sum((a - mx) ** 2 for a in x) ** 0.5
    sy = sum((b - my) ** 2 for b in y) ** 0.5
    return sxy / (sx * sy) if sx and sy else float("nan")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ideas", default=str(RESULTS / "ideas_ranked.csv"))
    ap.add_argument("--threshold", type=float, default=THRESHOLD)
    ap.add_argument("--manifest", default="slices/manifest.csv", help="slicer manifest, for chart 9")
    ap.add_argument("--match-needs", action="store_true",
                    help="use only the needs every arm was run on (the xhigh needs)")
    args = ap.parse_args()
    th = args.threshold
    OUT.mkdir(parents=True, exist_ok=True)

    calls = load(Path(args.ideas))
    all_scores = [s for c in calls.values() for s in c["scores"]]
    groups = by_arm_need(calls)
    needs_of = {a: set(pn) for a, pn in groups.items()}
    all_needs = set().union(*needs_of.values())
    sub_note = ""
    if args.match_needs:
        common = set.intersection(*needs_of.values())
        groups = by_arm_need(calls, common)
        all_scores = [s for c in calls.values() if c["need"] in common for s in c["scores"]]
        sub_note = f"\nOnly the {len(common)} needs every arm was run on: {', '.join(sorted(common))}"
    kept = sum(s >= th for s in all_scores) / len(all_scores)
    print(f"threshold {th:g}: {sum(s >= th for s in all_scores)} of {len(all_scores)} ideas ({kept:.1%})")

    rng = random.Random(SEED)
    rows = []
    for c in COND_ORDER:
        for e in EFFORTS:
            pn = groups.get((c, e))
            if not pn:
                continue
            idea, call, tok = rates(pn, th)
            (ilo, ihi), (clo, chi) = bootstrap(pn, th, rng)
            hits = sum(s >= th for cs in pn.values() for x in cs for s in x["scores"])
            ideas = sum(len(x["scores"]) for cs in pn.values() for x in cs)
            spent = sum(x["tokens"] for cs in pn.values() for x in cs)
            ylo, yhi, yboot = bootstrap_yield(pn, th, rng)
            few = len(pn) if not args.match_needs and len(pn) < len(all_needs) else 0
            rows.append({"condition": c, "effort": e, "label": arm_label(c, e, few), "needs": len(pn),
                         "calls": sum(len(cs) for cs in pn.values()), "ideas": ideas, "hits": hits,
                         "idea_rate": idea, "idea_lo": ilo, "idea_hi": ihi,
                         "call_rate": call, "call_lo": clo, "call_hi": chi,
                         "tokens_per_call": tok, "tokens_per_hit": spent / hits if hits else float("inf"),
                         "yield_per_100k": yield_per_100k(pn, th), "yield_lo": ylo, "yield_hi": yhi,
                         "yield_boot": yboot})

    out_csv = RESULTS / ("tail_summary" + ("" if th == THRESHOLD else f"_ge{th:g}")
                         + ("_matched" if args.match_needs else "") + ".csv")
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=[k for k in rows[0] if k not in ("label", "yield_boot")] + ["threshold"])
        w.writeheader()
        for r in rows:
            w.writerow({**{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()
                           if k not in ("label", "yield_boot")},
                        "threshold": th})
    print(f"{'arm':22} needs  hits/ideas  idea rate [95% CI]     call rate [95% CI]     tok/call  tok/hit"
          f"  top/100k tok [95% CI]")
    for r in rows:
        print(f"{r['label']:22} {r['needs']:5}  {r['hits']:4}/{r['ideas']:<5}  {r['idea_rate']:6.1%} "
              f"[{r['idea_lo']:5.1%}–{r['idea_hi']:5.1%}]  {r['call_rate']:6.1%} [{r['call_lo']:5.1%}–{r['call_hi']:5.1%}]"
              f"  {r['tokens_per_call']:8.0f} {r['tokens_per_hit']:8.0f}"
              f"  {r['yield_per_100k']:5.2f} [{r['yield_lo']:.2f}–{r['yield_hi']:.2f}]")
    print(f"-> {out_csv}\ncharts ->")
    # non-default runs get their own file names, so they don't overwrite the main charts
    tag = ("" if th == THRESHOLD else f"_ge{th:g}") + ("_matched" if args.match_needs else "")
    chart_rate(rows, th, kept, sub_note, tag)
    chart_budget(groups, th, kept, sub_note, tag)
    chart_yield(rows, groups, th, sub_note, tag)
    chart_yield_box(rows, groups, th, sub_note, tag)
    chart_yield_box(rows, groups, th, sub_note, tag, box_kind="calls")
    chart_yield_spread(rows, th, sub_note, tag)
    chart_yield_spread(rows, th, sub_note, tag, annotated=True)
    chart_slice_size(groups, th, Path(args.manifest), tag)


if __name__ == "__main__":
    main()
