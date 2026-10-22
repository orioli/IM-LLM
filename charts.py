#!/usr/bin/env python3
"""
charts.py — key charts for the RQ1 pilot, drawn with matplotlib from analyze.py's outputs.

  python charts.py            # reads results/*.csv and results/judgments.jsonl, writes results/charts/*.png

Charts
  1_tokens_per_call.png      input + output tokens per call, by condition and effort
  2_win_rates.png            every pairwise comparison: win rate with 95% CI
  3_score_diff_A_minus_B.png how A and B differ on each judging criterion, by effort
  4_cost_vs_quality.png      total tokens vs mean blind idea score per arm, A and B (needs top_ideas.py report)
  5_context_ladder.png       C → R → B → A at one effort: input tokens vs idea score, with head-to-head win rates
"""
from __future__ import annotations

import csv
import re
import json
import random
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS = Path("results")
OUT = RESULTS / "charts"
EFFORTS = ["low", "medium", "high", "xhigh", "max"]       # charts only draw the levels present in the data
CRITERIA = ["relevance", "novelty", "feasibility", "specificity", "diversity"]

# ── Palette (validated: categorical adjacent pairs and ordinal ramp pass all checks) ──
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
# Condition colours, used in every chart. Pick a preset, or add your own pair.
# R and C sit close to each other for colour-blind readers, so every chart that shows them also labels them.
COND_PALETTES = {
    "ggplot":  {"A": "#00BFC4", "B": "#C77CFF", "R": "#7CAE00", "C": "#F8766D"},  # turquoise, magenta, green, salmon
    "default": {"A": "#2a78d6", "B": "#eb6834", "R": "#1baf7a", "C": "#eda100"},  # blue, orange, green, amber
}
COND_PALETTE = "ggplot"
COND = COND_PALETTES[COND_PALETTE]
TOKENS = {"input": "#1baf7a", "output": "#eda100"}             # slots 3, 4: kept apart from A/B colours
EFFORT_RAMP = {"low": "#86b6ef", "medium": "#3987e5", "high": "#1c5cab", "xhigh": "#0d366b",
               "max": "#0b0b0b"}                         # ordinal blue ramp
COND_NAME = {"A": "A · full graph", "B": "B · need slice", "R": "R · random slice", "C": "C · no graph"}
SHORT_NAME = {"A": "Full graph", "B": "Slice", "R": "Random graph", "C": "No graph"}   # axis labels
CONDITIONS = ["A", "B", "R", "C"]          # display order in charts 1–2
# ── Chart 4 settings ────────────────────────────────────────────────
# Symbol per effort level (matplotlib marker codes): "x" cross, "+" plus, "o" circle (drawn open),
# "^" triangle, "s" square, "D" diamond, "v" triangle down, "*" star
EFFORT_MARKER = {"low": "1", "medium": "^", "high": ".", "xhigh": "*", "max": "D"}

# cost axis: log scale shows cost ratios as equal distances (B at half of A, each effort step a multiple)
LOG_X = True
LOG_X_TICKS = [2500, 5000, 10000, 20000, 40000, 80000]   # only the ticks inside the data range are shown

# axis limits as (min, max); None on either side = automatic. X is in tokens, Y in score points.
# Ideas outside the limits are cut off, not moved, so check none of interest fall outside.
X_LIM = (None, None)
Y_LIM = (2.5, None)

# legend position: "below" = under the plot (never covers data), or any matplotlib location such as
# "lower right", "upper left", "best"
LEGEND_LOC = "below"

# arm means (large marks): area in points²; the halo around them scales with it
MEAN_MARK_SIZE = 75

# individual ideas: tweak if the cloud looks too heavy or too faint
IDEA_MARK_SIZE = 7        # marker area in points²
IDEA_ALPHA = 0.45         # 0 = invisible, 1 = solid
IDEA_LINE_WIDTH = 0.7     # stroke width of the marks
IDEA_JITTER_Y = 0.04      # max vertical nudge in score points (scores come in 0.25 steps); 0 = none
IDEA_JITTER_X = 0.0       # max horizontal nudge as a share of the token cost (0.015 = ±1.5%); 0 = none

# frontier: upper convex hull of individual ideas
SHOW_FRONTIER = True
# "condition" = one frontier per condition, in its colour (A blue, B orange)
# "all"       = one grey frontier over all ideas, whatever the arm
# "both"      = the per-condition frontiers plus the grey overall one
FRONTIER_MODE = "condition"
# right of the best idea: "flat" = carry the best score to the right edge (paying more buys nothing better),
# "hull" = follow the convex hull down to the most expensive ideas, "stop" = end at the best idea
FRONTIER_RIGHT = "hull"
FRONTIER_WIDTH = 1.0
FRONTIER_LINESTYLE = (0, (4, 2.5))   # dashed, so it reads apart from the solid mean lines; "-" = solid
FRONTIER_COLOR = "#52514e"           # used for the overall ("all") frontier
FRONTIER_ALPHA = 1.0                 # transparency of the convex hull lines: 0 = invisible, 1 = solid

# Pareto frontier: staircase through the ideas no other idea beats on both cost and score.
# Drawn for the same groups as FRONTIER_MODE, solid, shifted up so it doesn't sit on the hull.
SHOW_PARETO = True
PARETO_OFFSET_Y = 0.1                # vertical shift in score points; 0 = drawn at the true scores
PARETO_OFFSET_X = -0.1                # horizontal shift in thousands of tokens, as the axis reads (0.1 = 100 tokens)
PARETO_RIGHT = "stop"                # "stop" = end at the best idea, "flat" = carry it to the right edge
PARETO_WIDTH = 1.0
PARETO_ALPHA = 1.0                   # transparency of the Pareto staircase: 0 = invisible, 1 = solid
# label boxed at the middle of each condition's staircase (white background, border in its colour)
PARETO_LABELS = {"A": "Wide context", "B": "Narrow context"}    # {} or None = no labels
PARETO_LABEL_SIZE = 8.5
# conditions drawn in chart 4 (R and C get their own chart, 5)
CHART4_CONDITIONS = ("A", "B")

# ── Chart 5 settings (context ladder) ───────────────────────────────
LADDER_EFFORT = "high"                    # the effort level R and C were run at
LADDER_ORDER = ["C", "R", "B", "A"]       # left to right: least to most context
LADDER_X_TICKS = [1000, 2000, 4000, 8000, 16000, 32000]
LADDER_Y_LIM = (None, None)               # (min, max) in score points; None = automatic
# head-to-head comparisons to print, as (winner-side, other); only those judged at LADDER_EFFORT appear
LADDER_PAIRS = [("R", "C"), ("B", "R"), ("A", "B"), ("B", "C"), ("A", "C"), ("A", "R")]


LINE_MARKERS = {"x", "+", "1", "2", "3", "4", "|", "_", "."}


def mark_style(effort: str, color: str, lw: float, fill: str = "none") -> dict:
    """Scatter kwargs for an effort mark: stroke marks as lines, closed shapes as open outlines."""
    m = EFFORT_MARKER.get(effort, "o")
    if m in LINE_MARKERS:                          # strokes only: × + tri-crosses ticks dot
        return {"marker": m, "color": color, "linewidths": lw}
    # every closed shape (circle, triangle, square, diamond, star…) is drawn as an outline
    return {"marker": m, "facecolors": fill, "edgecolors": color, "linewidths": lw}

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.size": 10, "text.color": INK, "axes.labelcolor": INK2, "axes.edgecolor": AXIS,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "legend.fontsize": 9,
})


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def finish(fig, ax, name: str, subtitle: str = "", after_layout=None) -> None:
    if subtitle:
        ax.set_title(ax.get_title(loc="left"), loc="left", pad=24 + 13 * subtitle.count("\n"))
        ax.text(0, 1.015, subtitle, transform=ax.transAxes, color=INK2, fontsize=9, va="bottom")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    if after_layout:            # e.g. an inset placed relative to the final layout
        after_layout(fig, ax)
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)
    print(f"  {OUT / name}")


# Thumbnail of the 4 x 4 grid of what each prompt contains (figure_slices_grid.py); charts that have
# room draw it next to their key, so the arm names are tied to a picture of what the model saw.
THUMB = OUT / "0b_slices_grid_thumb.png"
LADDER_WIDTH = 10.5 if THUMB.exists() else 8     # chart 5: wider when the thumbnail column is added
COSTQ_EXAMPLES = {"B": OUT / "0b_panel_slice_M8.png", "A": OUT / "0b_panel_full.png"}  # chart 4: next to labels
COSTQ_EXAMPLE_WIDTH = 0.10                      # chart 4: picture width, as a fraction of the plot width
COSTQ_EXAMPLE_ALPHA = 1.0                       # chart 4: opacity of the pictures
SCOREDIFF_EXAMPLE_ALPHA = 0.5                   # chart 3: opacity of the example pictures
SCOREDIFF_EXAMPLES = {                           # chart 3: an example picture on each side, under its arrow
    "left":  (OUT / "0b_panel_slice_M8_gray.png", "B", "Example: slice for M8 (25 nodes)"),
    "right": (OUT / "0b_panel_full_gray.png", "A", "Full graph (123 nodes)"),
}
LADDER_THUMB_RIGHT = 0.72                        # chart 5: right edge of the plot with the thumbnail


def add_slices_thumbnail(fig, box, top=None):
    """A thumbnail of the 4 x 4 grid of what each prompt contains, so the reader sees what 'full graph',
    'slice', 'random graph' and 'no graph' mean next to the arms. box = (left, bottom, width) in figure
    fractions; or give top instead of bottom (box[1] ignored) to hang the label and thumbnail from there."""
    if not THUMB.exists():
        return
    img = plt.imread(THUMB)
    left, bottom, width = box
    fw, fh = fig.get_size_inches()
    height = width * fw / fh * img.shape[0] / img.shape[1]
    # label on one line if it fits the column, else on two
    label = "What each prompt contains (coloured = what the model sees):"
    probe = fig.text(0, 0, label, fontsize=7.5)
    fig.canvas.draw()
    if probe.get_window_extent(fig.canvas.get_renderer()).width / (fw * fig.dpi) > width:
        label = "What each prompt contains\n(coloured = what the model sees):"
    probe.remove()
    gap = (0.022 + 0.022 * label.count("\n")) * 5.6 / fh          # room for the label, in figure fractions
    if top is not None:
        bottom = top - gap - height
    iax = fig.add_axes([left, bottom, width, height])
    iax.imshow(img, interpolation="lanczos")
    iax.set_axis_off()
    fig.text(left, bottom + height + 0.012 * 5.6 / fh, label, fontsize=7.5, color=INK2, va="bottom",
             linespacing=1.3)


# ── 1. Tokens per call ──────────────────────────────────────────────
def chart_tokens(rows: list[dict]) -> None:
    cells = {(r["condition"], r["effort"]): r for r in rows}
    n_bars = sum(1 for k in cells if k[0] in CONDITIONS)
    fig, ax = plt.subplots(figsize=(max(8, 0.75 * n_bars + 2), 4.8))
    x, labels, pos = 0.0, [], []
    for e in [e for e in EFFORTS if any((c, e) in cells for c in CONDITIONS)]:
        for c in CONDITIONS:
            r = cells.get((c, e))
            if r:
                i, o = num(r["input_tokens"]), num(r["output_tokens"])
                # 2px surface gap between stacked segments
                ax.bar(x, i, width=0.7, color=TOKENS["input"], edgecolor=SURFACE, linewidth=2)
                ax.bar(x, o, bottom=i, width=0.7, color=TOKENS["output"], edgecolor=SURFACE, linewidth=2)
                ax.text(x, i + o + 300, f"{(i + o) / 1000:.1f}k", ha="center", va="bottom", color=INK, fontsize=9)
                w = COND_NAME.get(c, c).split()           # "A · full graph", as in chart 5
                labels.append(" ".join(w[:3]) + ("\n" + " ".join(w[3:]) if w[3:] else "") + f"\n{e}")
                pos.append(x)
                x += 0.9
        x += 0.6
    ax.set_xticks(pos, labels)
    ax.tick_params(axis="x", colors=INK2, length=0, labelsize=9)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:g}k"))
    ax.set_ylabel("tokens per call")
    a_in = [num(r["input_tokens"]) for r in rows if r["condition"] == "A"]
    b_in = [num(r["input_tokens"]) for r in rows if r["condition"] == "B"]
    cut = 1 - (sum(b_in) / len(b_in)) / (sum(a_in) / len(a_in)) if a_in and b_in else None
    ax.set_title("Tokens per call" + (f" · slice cuts input by {cut:.0%}" if cut is not None else ""))
    handles = [plt.Rectangle((0, 0), 1, 1, color=TOKENS[k]) for k in ("input", "output")]
    ax.legend(handles, ["input tokens", "output tokens (incl. thinking)"], loc="upper left")
    present = [c for c in CONDITIONS if any(k[0] == c for k in cells)]
    finish(fig, ax, "1_tokens_per_call.png",
           "Mean tokens per call, by representation and thinking effort")


# ── 2. Win rates for every comparison ───────────────────────────────
def chart_win_rates(rows: list[dict]) -> None:
    items = []   # (label, rate, lo, hi, n)
    for r in rows:
        if r["target_need"] != "ALL":
            continue
        comp, n = r["comparison"], int(r.get("n_pairs") or r["n"])
        # each row's win rate is in the column named after its first arm: "condition: B vs R" -> B_win_rate
        first = comp.split(":", 1)[1].split(" vs ")[0].strip()
        rate = num(r.get(f"{first}_win_rate"))
        if rate is None:   # fallback: the only filled *_win_rate column
            rate = next(num(v) for k, v in r.items() if k.endswith("_win_rate") and num(v) is not None)
        lo, hi = num(r["ci95_low"]), num(r["ci95_high"])
        if comp.startswith("condition"):
            x, y = [t.strip() for t in comp.split(":", 1)[1].split(" vs ")]
            items.append((f"{x} over {y} · {r['effort']} effort", rate, lo, hi, n))
        elif comp.startswith("effort"):           # stored as the first level's win rate: flip to the second's
            lo_lvl, hi_lvl = [t.strip() for t in comp.split(":", 1)[1].split(" vs ")]
            items.append((f"{hi_lvl} over {lo_lvl} effort · {r['condition']}", 1 - rate, 1 - hi, 1 - lo, n))
        elif comp.startswith("arms"):             # stored as first arm's win rate: flip to second's
            x, y = comp.split(":", 1)[1].split(" vs ")
            arm = lambda a: a.strip().replace(":", " ") + " effort"
            items.append((f"{arm(y)} over {arm(x)}", 1 - rate, 1 - hi, 1 - lo, n))
    # condition comparisons first (A vs B, then the R/C controls), then effort steps, then arms
    order = {"A over B": 0, "B over R": 1, "B over C": 2, "A over C": 3, "A over R": 4, "R over C": 5,
             "high over low": 6, "xhigh over high": 7}
    items.sort(key=lambda t: (next((v for k, v in order.items() if t[0].startswith(k)), 8), t[0]))
    # sorted on the letter codes above; shown with readable names
    items = [(re.sub(r"\b[ABRC]\b", lambda m: COND_NAME[m.group(0)], lab), *rest) for lab, *rest in items]

    fig, ax = plt.subplots(figsize=(8, 0.55 * len(items) + 1.6))
    ys = list(range(len(items)))[::-1]
    ax.axvline(0.5, color=AXIS, linewidth=1.2, linestyle=(0, (4, 3)))
    ax.text(0.505, -0.75, "no difference", ha="left", color=MUTED, fontsize=8)
    for y, (label, rate, lo, hi, n) in zip(ys, items):
        ax.plot([lo, hi], [y, y], color=INK2, linewidth=2, solid_capstyle="round")
        ax.plot(rate, y, "o", color=INK, markersize=8, markeredgecolor=SURFACE, markeredgewidth=2)
        ax.text(1.04, y, f"{rate:.0%}  ({n} pairs)", va="center", color=INK, fontsize=9)
    ax.set_yticks(ys, [t[0] for t in items])
    ax.tick_params(axis="y", colors=INK, length=0)
    ax.set_xlim(0, 1.3)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_xlabel("win rate of the first-named arm (ties count half) · bar = 95% CI")
    ax.set_title("Blind pairwise judging: win rate per comparison", pad=10)
    ax.set_ylim(-1.0, len(items) - 0.5)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(OUT / "2_win_rates.png", dpi=200)
    plt.close(fig)
    print(f"  {OUT / '2_win_rates.png'}")


# ── 3. Criterion differences A − B ──────────────────────────────────
def chart_score_diff(rows: list[dict]) -> None:
    sel = {r["effort"]: r for r in rows if r["comparison"] == "condition: A vs B" and r["target_need"] == "ALL"}
    if not sel:
        return
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ys = list(range(len(CRITERIA)))[::-1]
    present = [e for e in EFFORTS if e in sel]
    step = 0.6 / max(len(present), 1)
    offsets = {e: 0.3 - step * (k + 0.5) for k, e in enumerate(present)}
    ax.axvline(0, color=AXIS, linewidth=1.2)
    for e in EFFORTS:
        r = sel.get(e)
        if not r:
            continue
        vals = [num(r.get(f"{c}_diff_A_minus_B")) for c in CRITERIA]
        for y, v in zip(ys, vals):
            if v is None:
                continue
            ax.plot([0, v], [y + offsets[e]] * 2, color=EFFORT_RAMP[e], linewidth=2, solid_capstyle="round")
            ax.plot(v, y + offsets[e], "o", color=EFFORT_RAMP[e], markersize=8, markeredgecolor=SURFACE,
                    markeredgewidth=2, label=f"{e} effort" if y == ys[0] else None)
    ax.set_yticks(ys, CRITERIA)
    ax.tick_params(axis="y", colors=INK, length=0)
    lim = 1.2
    ax.set_xlim(-lim, lim)
    ax.text(lim, ys[0] + 0.45, "Full graph better →", ha="right", color=INK2, fontsize=9)
    ax.text(-lim, ys[0] + 0.45, "← Slice better", ha="left", color=INK2, fontsize=9)
    ax.set_ylim(ys[-1] - 0.5, ys[0] + 0.7)
    ax.set_xlabel("mean judge score difference, Full graph minus Slice (1–5 scale)")
    ax.set_title("Judge scores, full graph minus slice, by criterion", pad=10)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    # example pictures in the empty space on each side: what "slice" and "full graph" look like
    lo_v = min(v for r in sel.values() for v in (num(r.get(f"{c}_diff_A_minus_B")) for c in CRITERIA) if v is not None)
    hi_v = max(v for r in sel.values() for v in (num(r.get(f"{c}_diff_A_minus_B")) for c in CRITERIA) if v is not None)
    right = (max(hi_v, 0) + 0.1, lim - 0.04)                 # space right of the longest bar
    w = right[1] - right[0]                                   # both pictures the same size
    boxes = {"left": (-lim + 0.04, -lim + 0.04 + w), "right": right}   # left one against the left edge
    for side, (path, cond, label) in SCOREDIFF_EXAMPLES.items():
        if not path.exists():
            continue
        x0, x1 = boxes[side]
        iax = ax.inset_axes([x0, ys[-1] - 0.4, x1 - x0, ys[0] - ys[-1] + 0.25], transform=ax.transData)
        iax.imshow(plt.imread(path), interpolation="lanczos", aspect="equal", alpha=SCOREDIFF_EXAMPLE_ALPHA)
        iax.set_anchor("C")
        iax.set_axis_off()
        iax.set_title(label, fontsize=8.5, color=INK2, fontweight="bold", pad=4, alpha=SCOREDIFF_EXAMPLE_ALPHA)
    fig.tight_layout()
    fig.savefig(OUT / "3_score_diff_A_minus_B.png", dpi=200)
    plt.close(fig)
    print(f"  {OUT / '3_score_diff_A_minus_B.png'}")


# ── 4. Cost vs quality ──────────────────────────────────────────────
def arm_quality_from_ideas(ideas_csv: Path):
    """Arm -> (mean, ci95 half-width, n_runs), from blind individual idea scores (top_ideas.py).

    Ideas from the same call are not independent, so each call's ideas are averaged first;
    the mean and its 95% CI are then taken over calls.
    """
    per_run = defaultdict(list)
    arm_of = {}
    points = []                                   # (tokens of the generating call, idea score)
    for r in read_csv(ideas_csv):
        sc = num(r.get("score"))
        if sc is None:
            continue
        per_run[r["run_id"]].append(sc)
        arm_of[r["run_id"]] = (r["condition"], r["effort"])
        tok = (num(r.get("run_input_tokens")) or 0) + (num(r.get("run_output_tokens")) or 0)
        points.append((tok, sc, r["condition"], r["effort"]))
    by_arm, ideas_by_arm = defaultdict(list), defaultdict(list)
    for run, vals in per_run.items():
        by_arm[arm_of[run]].append(sum(vals) / len(vals))
        ideas_by_arm[arm_of[run]].extend(vals)
    out = {}
    for arm, xs in by_arm.items():
        m = sum(xs) / len(xs)
        sd = (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5 if len(xs) > 1 else 0.0
        q1, q3 = quartiles(ideas_by_arm[arm])
        out[arm] = (m, 1.96 * sd / len(xs) ** 0.5, len(xs), q1, q3)
    return out, points


def quartiles(xs: list[float]) -> tuple[float, float]:
    """25th and 75th percentiles (linear interpolation)."""
    v = sorted(xs)
    def q(p):
        k = (len(v) - 1) * p
        lo, hi = int(k), min(int(k) + 1, len(v) - 1)
        return v[lo] + (v[hi] - v[lo]) * (k - lo)
    return q(0.25), q(0.75)


def upper_frontier(pts: list[tuple[float, float]], right: str = "flat") -> list[tuple[float, float]]:
    """Upper convex hull of (tokens, score) points, left to right (Andrew's monotone chain).

    Uses the real scores, not the jittered positions. Ideas from one call share its cost, so only
    the best score at each cost can be on the frontier; the rest are dropped first (otherwise the
    line would start at the cheapest call's worst idea and climb straight up).
    right: "flat" extends the best score to the right edge, "hull" keeps the descending hull,
    "stop" ends at the best idea.
    """
    best_at = {}
    for x, y in pts:
        best_at[x] = max(y, best_at.get(x, y))
    # convex in the axis's own scale: on a log axis the hull is built on log(cost), so it looks convex
    cross = lambda o, a, b: ((xs(a[0]) - xs(o[0])) * (b[1] - o[1]) - (a[1] - o[1]) * (xs(b[0]) - xs(o[0])))
    hull = []
    for p in sorted(best_at.items()):
        while len(hull) >= 2 and cross(hull[-2], hull[-1], p) >= 0:   # drop points below the chord
            hull.pop()
        hull.append(p)
    if right in ("flat", "stop") and hull:
        top = max(h[1] for h in hull)
        hull = hull[: next(i for i, h in enumerate(hull) if h[1] == top) + 1]
        if right == "flat":
            hull.append((max(best_at), top))
    return hull


def pareto_steps(pts: list[tuple[float, float]], right: str = "stop") -> list[tuple[float, float]]:
    """Pareto-optimal (tokens, score) points, cheapest first: each is better than every cheaper idea.

    Ideas from one call share its cost, so only the best score at each cost counts. The list ends at
    the best idea ("stop"), or carries its score on to the most expensive call ("flat").
    """
    best_at = {}
    for x, y in pts:
        best_at[x] = max(y, best_at.get(x, y))
    steps, top = [], float("-inf")
    for x, y in sorted(best_at.items()):
        if y > top:
            steps.append((x, y))
            top = y
    if right == "flat" and steps and max(best_at) > steps[-1][0]:
        steps.append((max(best_at), top))
    return steps


def frontier_at(hull: list[tuple[float, float]], x: float) -> float:
    """Height of the frontier line at cost x (linear between hull points); +inf where there is no line."""
    if not hull or x < hull[0][0] or x > hull[-1][0]:
        return float("inf")
    for (x0, y0), (x1, y1) in zip(hull, hull[1:]):
        if x0 <= x <= x1:   # interpolate in the axis's own scale, so it matches the straight line drawn
            return y0 if x1 == x0 else y0 + (y1 - y0) * (xs(x) - xs(x0)) / (xs(x1) - xs(x0))
    return hull[-1][1]


def xs(x: float) -> float:
    """Cost as the x axis lays it out: log when LOG_X, linear otherwise."""
    import math
    return math.log(x) if LOG_X and x > 0 else x


def group_points(points):
    """(condition, effort) -> list of (tokens, score) points."""
    out = defaultdict(list)
    for tok, sc, c, e in points:
        out[(c, e)].append((tok, sc))
    return out


def arm_quality_from_judgments(judgments: Path, runs_index: dict):
    """Fallback: pairwise judge scores pooled per arm (depends on which arms were compared)."""
    scores = defaultdict(list)
    for line in judgments.open(encoding="utf-8"):
        j = json.loads(line)
        if not j.get("ok") or j.get("auto"):
            continue
        for side in ("x", "y"):
            arm = runs_index.get(j[f"run_{side}"])
            s = j.get(f"scores_{side}") or {}
            vals = [s.get(c) for c in CRITERIA if isinstance(s.get(c), (int, float))]
            if arm and vals:
                scores[arm].append(sum(vals) / len(vals))
    return {a: (sum(v) / len(v), None, len(v), None, None) for a, v in scores.items()}, []


def chart_cost_quality(summary: list[dict], ideas_csv: Path, judgments: Path, runs_index: dict) -> None:
    if ideas_csv.exists():
        quality, points = arm_quality_from_ideas(ideas_csv)
        ylabel = "idea score (1–5, blind individual scoring)"
        sub = ("Large marks = arm means · thick bar = 95% CI of the mean · thin bracket = middle 50% of ideas\n"
               "Small marks = individual ideas · dashed = upper convex hull · solid steps = Pareto frontier"
               + (" (shifted)" if SHOW_PARETO and (PARETO_OFFSET_Y or PARETO_OFFSET_X) else ""))
    elif judgments.exists():
        quality, points = arm_quality_from_judgments(judgments, runs_index)
        ylabel = "mean judge score (1–5, average of 5 criteria)"
        sub = "Each point is one arm; scores pooled over every pairwise judgment it appeared in"
    else:
        print("  (skipped 4_cost_vs_quality.png: run `python top_ideas.py score` and `report` first)")
        return
    tokens = {(r["condition"], r["effort"]): num(r["total_tokens"]) for r in summary}
    points = [p for p in points if p[2] in CHART4_CONDITIONS]   # R and C ideas belong to chart 5

    fig, ax = plt.subplots(figsize=(8, 6.2 if LEGEND_LOC == "below" else 5))
    pareto_label_art = {}                                   # condition -> its "Narrow/Wide context" label
    # frontiers first, so the ideas they pass through can be drawn exactly on them
    hulls = {}                                              # key: "A", "B" or "all" -> hull points
    if SHOW_FRONTIER and points:
        if FRONTIER_MODE in ("condition", "both"):
            for c in ("A", "B"):
                pc = [(p[0], p[1]) for p in points if p[2] == c]
                if pc:
                    hulls[c] = upper_frontier(pc, FRONTIER_RIGHT)
        if FRONTIER_MODE in ("all", "both"):
            hulls["all"] = upper_frontier([(p[0], p[1]) for p in points], FRONTIER_RIGHT)
    # the line(s) an idea must not be drawn above: its own condition's frontier, and the overall one
    own_hulls = lambda c: [h for k, h in hulls.items() if k in (c, "all")]
    if points:
        # individual ideas: colour = condition, shape = effort, kept faint so the means stay on top;
        # scores come in steps of 0.25, so jitter them slightly, except ideas on the frontier
        rng = random.Random(0)
        for (c, e), grp in group_points(points).items():
            hs = own_hulls(c)
            # an idea is "on the line" if its real score reaches its frontier at that cost (corners and
            # flat stretches alike): those are drawn exactly on the line, everything else is jittered
            on_line = lambda q: any(q[1] >= frontier_at(h, q[0]) - 1e-9 for h in hs)
            ys = [p[1] if on_line(p)
                  else min([p[1] + rng.uniform(-IDEA_JITTER_Y, IDEA_JITTER_Y)]
                           + [frontier_at(h, p[0]) for h in hs])                       # never above its line
                  for p in grp]
            xs = [p[0] if on_line(p)
                  else p[0] * (1 + rng.uniform(-IDEA_JITTER_X, IDEA_JITTER_X)) for p in grp]
            ax.scatter(xs, ys,
                       s=IDEA_MARK_SIZE, alpha=IDEA_ALPHA, zorder=0, rasterized=True,
                       **mark_style(e, COND.get(c, MUTED), IDEA_LINE_WIDTH))
    for c in ("A", "B"):
        arms = [(e, quality[(c, e)]) for e in EFFORTS if (c, e) in tokens and (c, e) in quality]
        if not arms:
            continue
        pts = [(tokens[(c, e)], q[0], q[1], e) for e, q in arms]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        ax.plot(xs, ys, color=COND[c], linewidth=2, zorder=1)
        for x, (e, (m, ci, _, q1, q3)) in zip(xs, arms):
            if q1 is not None:                    # spread: middle 50% of individual ideas
                ax.plot([x, x], [q1, q3], color=COND[c], linewidth=1.2, alpha=0.9, zorder=1,
                        solid_capstyle="butt")
                cap = (x / 1.015, x * 1.015) if LOG_X else (x - 180, x + 180)
                ax.plot(cap, [q1, q1], color=COND[c], linewidth=1.2, zorder=1)
                ax.plot(cap, [q3, q3], color=COND[c], linewidth=1.2, zorder=1)
            if ci is not None:                    # precision of the mean: 95% CI
                ax.plot([x, x], [m - ci, m + ci], color=COND[c], linewidth=2.5, zorder=1,
                        solid_capstyle="round")
        for x, y, _, e in pts:
            # a surface-coloured halo underneath lifts the mean off the cloud of ideas
            ax.scatter([x], [y], s=MEAN_MARK_SIZE * 1.27, zorder=2, **mark_style(e, SURFACE, 3.5, fill=SURFACE))
            ax.scatter([x], [y], s=MEAN_MARK_SIZE, zorder=3, **mark_style(e, COND[c], 1.6, fill=SURFACE))
    for key, h in hulls.items():
        ax.plot([q[0] for q in h], [q[1] for q in h], color=COND.get(key, FRONTIER_COLOR),
                linewidth=FRONTIER_WIDTH, linestyle=FRONTIER_LINESTYLE, alpha=FRONTIER_ALPHA, zorder=4,
                solid_joinstyle="round", dash_joinstyle="round")
    if SHOW_PARETO and points:
        groups = []
        if FRONTIER_MODE in ("condition", "both"):
            groups += [(c, [(p[0], p[1]) for p in points if p[2] == c]) for c in ("A", "B")]
        if FRONTIER_MODE in ("all", "both"):
            groups.append(("all", [(p[0], p[1]) for p in points]))
        for key, pts_k in groups:
            st = pareto_steps(pts_k, PARETO_RIGHT) if pts_k else []
            if st:
                # step "post": each score holds until the next, cheaper-to-better idea
                if PARETO_LABELS and key in PARETO_LABELS and len(st) >= 1:
                    # middle of the staircase along the axis as drawn (log or linear), on the line itself
                    x_lo, x_hi = st[0][0], st[-1][0]
                    xm = (x_lo * x_hi) ** 0.5 if LOG_X else (x_lo + x_hi) / 2
                    ym = max(q[1] for q in st if q[0] <= xm)
                    pareto_label_art[key] = ax.text(xm + PARETO_OFFSET_X * 1000, ym + PARETO_OFFSET_Y, PARETO_LABELS[key],
                            ha="center", va="center", fontsize=PARETO_LABEL_SIZE, color=INK, zorder=6,
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                                      edgecolor=COND.get(key, FRONTIER_COLOR), linewidth=1.0))
                ax.step([q[0] + PARETO_OFFSET_X * 1000 for q in st], [q[1] + PARETO_OFFSET_Y for q in st],
                        where="post",
                        color=COND.get(key, FRONTIER_COLOR), linewidth=PARETO_WIDTH, alpha=PARETO_ALPHA,
                        zorder=4)
    if LOG_X:
        ax.set_xscale("log")
    ax.set_xlim(*X_LIM)       # None leaves that side automatic
    ax.set_ylim(*Y_LIM)
    if LOG_X:
        lo_x, hi_x = ax.get_xlim()
        ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator([t for t in LOG_X_TICKS if lo_x <= t <= hi_x]))
        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:g}k"))
    ax.set_xlabel("total tokens per call (input + output)" + (", log scale" if LOG_X else ""))
    ax.set_ylabel(ylabel)
    ax.set_title("Cost vs quality per arm")
    # two legends' worth of meaning in one box: colour = condition, shape = effort
    from matplotlib.lines import Line2D
    # column 1: conditions (colour), column 2: effort levels (shape); a blank entry keeps them apart
    col1 = [Line2D([], [], color=COND[c], linewidth=2.5, label=COND_NAME[c]) for c in ("A", "B")]
    if any(k in hulls for k in ("A", "B")):
        col1.append(Line2D([], [], color=INK2, linewidth=FRONTIER_WIDTH, linestyle=FRONTIER_LINESTYLE,
                           label="convex hull (per condition)"))
    if "all" in hulls:
        col1.append(Line2D([], [], color=FRONTIER_COLOR, linewidth=FRONTIER_WIDTH, linestyle=FRONTIER_LINESTYLE,
                           label="frontier (all ideas)"))
    if SHOW_PARETO and points:
        shifts = ([f"{PARETO_OFFSET_X:+g}k tokens"] if PARETO_OFFSET_X else []) + \
                 ([f"{PARETO_OFFSET_Y:+g} score"] if PARETO_OFFSET_Y else [])
        off = f" ({', '.join(shifts)})" if shifts else ""
        col1.append(Line2D([], [], color=INK2, linewidth=PARETO_WIDTH, drawstyle="steps-post",
                           label=f"Pareto frontier{off}"))
    col2 = [Line2D([], [], marker=EFFORT_MARKER[e], linestyle="", color=INK2, markersize=8,
                   markerfacecolor="none", markeredgewidth=1.6, label=f"{e} effort")
            for e in EFFORTS if any((c, e) in quality for c in ("A", "B"))]
    # legend fills column by column: pad both columns to the same height so each group stays together
    blank = lambda: Line2D([], [], linestyle="", label=" ")
    rows_n = max(len(col1), len(col2))
    handles = col1 + [blank() for _ in range(rows_n - len(col1))] + col2 + [blank() for _ in range(rows_n - len(col2))]
    if LEGEND_LOC == "below":
        ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2,
                  columnspacing=3.0, frameon=False)
    else:
        ax.legend(handles=handles, loc=LEGEND_LOC, ncol=2, columnspacing=1.6,
                  frameon=True, facecolor=SURFACE, edgecolor="none", framealpha=0.92)
    ax.grid(axis="x", color=GRID, linewidth=0.8)

    def examples_beside_labels(fig, ax):
        """A small picture of what each condition's prompt contains, just right of its context label."""
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        to_ax = ax.transAxes.inverted()
        ax_w, ax_h = ax.get_window_extent(r).width, ax.get_window_extent(r).height
        for key, art in pareto_label_art.items():
            path = COSTQ_EXAMPLES.get(key)
            if not path or not path.exists():
                continue
            bb = art.get_bbox_patch().get_window_extent(r) if art.get_bbox_patch() else art.get_window_extent(r)
            (x0, y0), (x1, y1) = to_ax.transform([[bb.x0, bb.y0], [bb.x1, bb.y1]])
            img = plt.imread(path)
            w = COSTQ_EXAMPLE_WIDTH
            h = w * ax_w / ax_h * img.shape[0] / img.shape[1]
            iax = ax.inset_axes([x1 + 0.012, (y0 + y1) / 2 - h / 2, w, h])
            iax.imshow(img, interpolation="lanczos", alpha=COSTQ_EXAMPLE_ALPHA)
            iax.set_axis_off()
            iax.set_zorder(5)

    finish(fig, ax, "4_cost_vs_quality.png", sub,
           after_layout=examples_beside_labels if pareto_label_art else None)


# ── 5. Context ladder: C → R → B → A at one effort ──────────────────
def chart_context_ladder(summary: list[dict], pairwise: list[dict], ideas_csv: Path) -> None:
    """Does the graph help (C vs the rest), and is it relevance or size (R vs B)?

    x = mean input tokens per call (how much context the prompt carried), y = mean blind idea score
    with 95% CI (thick) and middle 50% of ideas (thin bracket). Neighbours are joined by their
    head-to-head win rate from the pairwise judge; the other comparisons go in the subtitle.
    """
    name = "5_context_ladder.png"
    if not ideas_csv.exists():
        print(f"  (skipped {name}: run `python top_ideas.py score` and `report` first)")
        return
    quality, _ = arm_quality_from_ideas(ideas_csv)
    inp = {r["condition"]: num(r["input_tokens"]) for r in summary if r["effort"] == LADDER_EFFORT}
    conds = [c for c in LADDER_ORDER if c in inp and (c, LADDER_EFFORT) in quality]
    if len(conds) < 2:
        print(f"  (skipped {name}: fewer than two conditions scored at {LADDER_EFFORT} effort)")
        return

    # head-to-head win rates at this effort, oriented as "first over second"
    h2h = {}
    for r in pairwise:
        if r["target_need"] != "ALL" or not r["comparison"].startswith("condition") \
                or r.get("effort") != LADDER_EFFORT:
            continue
        x, y = [t.strip() for t in r["comparison"].split(":", 1)[1].split(" vs ")]
        rate, lo, hi = num(r.get(f"{x}_win_rate")), num(r["ci95_low"]), num(r["ci95_high"])
        if rate is None:
            continue
        n, p = int(r.get("n_pairs") or r["n"]), num(r.get("sign_test_p"))
        h2h[(x, y)] = (rate, lo, hi, n, p)
        h2h[(y, x)] = (1 - rate, 1 - hi, 1 - lo, n, p)

    def fmt(a, b, short=False):
        rate, lo, hi, n, p = h2h[(a, b)]
        ps = "" if p is None else (" p<0.001" if p < 0.001 else f" p={p:.3f}")
        return f"{a} over {b}: {rate:.0%}" + ("" if short else f" [{lo:.0%}–{hi:.0%}], {n} pairs{ps}")

    # rungs evenly spaced, least to most context: R and B are size-matched by design, so on a token
    # axis they would sit on top of each other; the token count goes in each rung's label instead
    fig, ax = plt.subplots(figsize=(LADDER_WIDTH, 5.4))
    pts = [(k, *quality[(c, LADDER_EFFORT)]) for k, c in enumerate(conds)]     # (x, m, ci, n, q1, q3)
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=AXIS, linewidth=1.2, zorder=1)
    for c, (x, m, ci, n, q1, q3) in zip(conds, pts):
        col = COND.get(c, MUTED)
        if q1 is not None:                                   # middle 50% of individual ideas
            ax.plot([x, x], [q1, q3], color=col, linewidth=1.2, zorder=2, solid_capstyle="butt")
            for q in (q1, q3):
                ax.plot([x - 0.06, x + 0.06], [q, q], color=col, linewidth=1.2, zorder=2)
        if ci:                                               # 95% CI of the mean (over calls)
            ax.plot([x, x], [m - ci, m + ci], color=col, linewidth=3, zorder=3, solid_capstyle="round")
        ax.scatter([x], [m], s=MEAN_MARK_SIZE * 1.6, color=col, edgecolors=SURFACE, linewidths=2, zorder=4)
        ax.annotate(f"{m:.2f}", (x, m), xytext=(9, 0), textcoords="offset points", va="center", ha="left",
                    fontsize=9, color=INK, zorder=5)

    # neighbours: win rate of the right-hand rung, boxed above the connecting segment
    top = max(p[5] if p[5] is not None else p[1] for p in pts)
    for (a, pa), (b, pb) in zip(zip(conds, pts), zip(conds[1:], pts[1:])):
        if (b, a) not in h2h:
            continue
        ax.annotate("", xy=(pb[0] - 0.08, top + 0.12), xytext=(pa[0] + 0.08, top + 0.12),
                    arrowprops=dict(arrowstyle="-", color=AXIS, linewidth=1), zorder=5)
        ax.text((pa[0] + pb[0]) / 2, top + 0.12, fmt(b, a, short=True), ha="center", va="center", fontsize=8.5,
                color=INK, zorder=6,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=AXIS, linewidth=0.8))

    # rung labels double as the legend: name in its colour (colour alone can't tell R from C), then size
    ax.set_xticks(range(len(conds)), [f"{COND_NAME.get(c, c)}\n{inp[c] / 1000:.1f}k input tokens" for c in conds])
    for lab, c in zip(ax.get_xticklabels(), conds):
        lab.set_color(INK)
    ax.tick_params(axis="x", length=0, pad=8)
    ax.set_xlim(-0.5, len(conds) - 0.5)
    lo_y, hi_y = ax.get_ylim()
    ax.set_ylim(LADDER_Y_LIM[0] if LADDER_Y_LIM[0] is not None else lo_y,
                LADDER_Y_LIM[1] if LADDER_Y_LIM[1] is not None else max(hi_y, top + 0.25))
    ax.set_xlabel("graph context in the prompt, least to most (mean input tokens per call)")
    ax.set_ylabel("idea score (1–5, blind individual scoring)")
    ax.set_title(f"Context ladder at {LADDER_EFFORT} effort")
    # small colour key under each rung name
    for k, c in enumerate(conds):
        ax.plot([k], [0], transform=matplotlib.transforms.blended_transform_factory(ax.transData, ax.transAxes),
                marker="s", markersize=7, color=COND.get(c, MUTED), clip_on=False, zorder=6)

    # every judged head-to-head, in full, below the plot
    lines = [fmt(a, b) for a, b in LADDER_PAIRS if (a, b) in h2h and a in conds and b in conds]
    note = None
    if lines:
        note = ax.text(0, -0.24, "Blind pairwise judging (win rate, 95% CI, sign test):\n" + "\n".join(lines),
                       transform=ax.transAxes, va="top", ha="left", fontsize=8.5, color=INK2, linespacing=1.4)
        fig.set_size_inches(LADDER_WIDTH, 5.4 + 0.19 * (len(lines) + 1))

    def thumb_right_column(fig, ax):
        """Narrow the plot and put the thumbnail in a column on the right, level with the plot's top."""
        fig.subplots_adjust(right=LADDER_THUMB_RIGHT)
        left = LADDER_THUMB_RIGHT + 0.03
        add_slices_thumbnail(fig, (left, 0, 0.985 - left), top=ax.get_position().y1)

    finish(fig, ax, name, "Mark = mean over calls · thick bar = 95% CI · thin bracket = middle 50% of ideas\n"
                          "Boxes between rungs = blind head-to-head win rate of the right-hand condition",
           after_layout=thumb_right_column if THUMB.exists() else None)


def runs_index_from_calls(calls: Path) -> dict:
    """run_id -> (condition, effort), from results/calls.csv."""
    if not calls.exists():
        return {}
    return {r["run_id"]: (r["condition"], r["effort"]) for r in read_csv(calls)}


def check_markers() -> None:
    """Fail early, with a readable message, if EFFORT_MARKER holds a symbol matplotlib doesn't know."""
    from matplotlib.markers import MarkerStyle
    bad = []
    for effort, m in EFFORT_MARKER.items():
        try:
            MarkerStyle(m)
        except ValueError:
            bad.append(f"{effort}: {m!r}")
    if bad:
        raise SystemExit("Invalid marker symbol in EFFORT_MARKER (" + ", ".join(bad) + ").\n"
                         "Use one of: 'x' '+' 'o' '.' '^' 'v' '<' '>' 's' 'D' 'd' 'p' 'h' '*' "
                         "'1' '2' '3' '4' '|' '_'  (':' and '-' are line styles, not markers)")


def main() -> None:
    check_markers()
    OUT.mkdir(parents=True, exist_ok=True)
    summary = read_csv(RESULTS / "summary_condition_effort.csv")
    print("charts ->")
    chart_tokens(summary)
    pw = RESULTS / "pairwise_summary.csv"
    pairwise = read_csv(pw) if pw.exists() else []
    if pairwise:
        chart_win_rates(pairwise)
        chart_score_diff(pairwise)
    else:
        print("  (skipped charts 2–3: run `python analyze.py summary` first)")
    chart_cost_quality(summary, RESULTS / "ideas_ranked.csv", RESULTS / "judgments.jsonl",
                       runs_index_from_calls(RESULTS / "calls.csv"))
    chart_context_ladder(summary, pairwise, RESULTS / "ideas_ranked.csv")


if __name__ == "__main__":
    main()
