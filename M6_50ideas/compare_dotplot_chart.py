#!/usr/bin/env python3
"""
compare_dotplot_chart.py: the yield comparison across runs as dot plots, one row per run on a shared axis.

  cd M6_50ideas
  python compare_dotplot_chart.py                                         # paper's three runs
  python compare_dotplot_chart.py --models opus fable deepseek deepseekpro qwen

Same data, measures and colours as compare_stack_chart.py, drawn so that it stays readable as runs are added:

  fig_yield_dotplot[__<models>].png   A: top ideas per US dollar (log axis), B: top ideas per 100k tokens.
                                      One row per run, the four representations as dots with their 95%
                                      bootstrap interval (2,000 resamples of calls, within need), the dot is
                                      the pooled yield (all top ideas / all tokens or dollars).
  fig_ratio_forest[__<models>].png    Each representation's yield divided by no graph's, per run, on a log
                                      axis with 1 marked, and pooled over runs (random effects on the log
                                      ratio) for the Claude runs, the other runs and all of them.

The 5-idea row is the main study over all 13 needs (A and B at medium effort, R and C at high, the only effort
they were run at), as in panel A of the paper's figure. 50-idea rows: M6, medium effort, first 10 calls.
Representations get a marker shape as well as a colour (R and C are close for colour-blind readers).
Also writes the numbers behind both figures as CSV. No API calls.
"""
from __future__ import annotations

import argparse
import csv
import math
import random

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import compare_runs_chart as cr
import power_analysis as pa

tc = cr.tc
ORDER = ["A", "B", "R", "C"]
NAME = {"A": "Full graph", "B": "Need slice", "R": "Random slice", "C": "No graph"}
MARK = {"A": "o", "B": "s", "R": "^", "C": "D"}
OFFSET = {"A": -0.27, "B": -0.09, "R": 0.09, "C": 0.27}
CLAUDE = {"Haiku", "Opus", "Sonnet", "Fable"}
CHINESE = {"DeepSeek Flash", "DeepSeek Pro", "Qwen Flash", "GLM Flash"}
REPS = 2000


def family(title: str) -> str:
    return "Claude" if title.split(" · ")[0] in CLAUDE else "Other"


def row_label(title: str) -> str:
    model, ideas = title.split(" · ")
    return f"{model} · {ideas.replace('ideas/call', 'ideas')}" + ("  (13 needs)" if ideas.startswith("5 ") else "")


def yields(models, usd: bool):
    """[(title, {cond: (yield, lo, hi)})] in panel order."""
    panels, stats = cr.compute("all", "bootstrap", usd, 4.0, models)
    out = []
    for title, _ in panels:
        out.append((title, {s["condition"]: (s["yield_per_100k"], s["yield_lo"], s["yield_hi"])
                            for s in stats if s["panel"] == title}))
    return out


def ratios(models):
    """[(title, {cond: (ratio, lo, hi, log, se)})] for A, B, R against C, per token; calls resampled within need."""
    panels, _ = cr.compute("all", "bootstrap", False, 4.0, models)
    rng = random.Random(f"{tc.SEED}-ratio")
    out = []
    for title, calls in panels:
        groups = tc.by_arm_need(calls)
        arm = {k[0]: v for k, v in groups.items()}             # cond -> need -> calls

        def y(per_need):
            top = sum(sum(s >= 4.0 for s in c["scores"]) for cs in per_need.values() for c in cs)
            tok = sum(c["tokens"] for cs in per_need.values() for c in cs)
            return top / tok

        res = {}
        for c in ("A", "B", "R"):
            point = math.log(y(arm[c]) / y(arm["C"]))
            draws = []
            for _ in range(REPS):
                a = {n: [rng.choice(cs) for _ in cs] for n, cs in arm[c].items()}
                b = {n: [rng.choice(cs) for _ in cs] for n, cs in arm["C"].items()}
                ya, yb = y(a), y(b)
                if ya > 0 and yb > 0:
                    draws.append(math.log(ya / yb))
            draws.sort()
            m = sum(draws) / len(draws)
            se = (sum((d - m) ** 2 for d in draws) / (len(draws) - 1)) ** 0.5
            lo, hi = draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1]
            res[c] = (math.exp(point), math.exp(lo), math.exp(hi), point, se)
        out.append((title, res))
    return out


def style(ax, n_rows: int, labels: list[str], groups: list[tuple[int, int, str]], show_labels: bool) -> None:
    for i in range(n_rows):                                    # light bands on every other row
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color=tc.GRID, alpha=0.35, lw=0, zorder=0)
    for start, end, _ in groups[1:]:
        ax.axhline(start - 0.5, color=tc.AXIS, lw=0.9, zorder=1)
    ax.set_ylim(n_rows - 0.5, -0.5)
    if show_labels:
        ax.set_yticks(range(n_rows), labels)
    ax.tick_params(axis="y", length=0, labelsize=10, colors=tc.INK, labelleft=show_labels)
    ax.grid(axis="x", color=tc.GRID, lw=0.7, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)


def dot(ax, y, x, lo, hi, cond, size=6.5, hollow=False):
    col = tc.COND[cond]
    ax.plot([lo, hi], [y, y], color=col, lw=1.8, solid_capstyle="round", zorder=3)
    if hollow:                                                  # pooled estimates: outlined, ring of surface around
        ax.plot([x], [y], marker=MARK[cond], ms=size, mfc=tc.SURFACE, mec=col, mew=2.0, zorder=4, ls="none")
    else:
        ax.plot([x], [y], marker=MARK[cond], ms=size, mfc=col, mec=tc.SURFACE, mew=1.2, zorder=4, ls="none")


def legend_handles(conds=ORDER):
    return [Line2D([], [], color=tc.COND[c], marker=MARK[c], ms=7, mec=tc.SURFACE, mew=1.2, lw=1.8,
                   label=NAME[c]) for c in conds]


def group_spans(titles):
    spans, start = [], 0
    keys = [("5-idea" if t.split(" · ")[1].startswith("5 ") else family(t)) for t in titles]
    for i in range(1, len(titles) + 1):
        if i == len(titles) or keys[i] != keys[start]:
            spans.append((start, i - 1, keys[start]))
            start = i
    return spans


def yield_figure(models, suffix: str) -> None:
    per_usd, per_tok = yields(models, True), yields(models, False)
    titles = [t for t, _ in per_tok]
    n = len(titles)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 1.15 + 0.52 * n + 1.3), sharey=True,
                             gridspec_kw={"wspace": 0.06})
    fig.patch.set_facecolor(tc.SURFACE)
    spans = group_spans(titles)
    rows = []
    for k, (ax, data, letter, xlabel) in enumerate((
            (axes[0], per_usd, "A", "top ideas per US dollar (log scale)"),
            (axes[1], per_tok, "B", "top ideas per 100k tokens"))):
        style(ax, n, [row_label(t) for t in titles], spans, show_labels=(k == 0))
        for i, (title, vals) in enumerate(data):
            for c in ORDER:
                if c in vals:
                    v, lo, hi = vals[c]
                    dot(ax, i + OFFSET[c], v, lo, hi, c)
                    rows.append({"panel": letter, "run": title, "condition": c, "yield": round(v, 3),
                                 "lo": round(lo, 3), "hi": round(hi, 3)})
        if letter == "A":
            ax.set_xscale("log")
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}"))
        else:
            ax.set_xlim(left=0)
        ax.set_xlabel(xlabel, color=tc.INK2, fontsize=10)
        ax.set_title(f"{letter}  {'Per dollar' if letter == 'A' else 'Per token'}", loc="left", fontsize=12,
                     fontweight="bold", color=tc.INK, pad=8)
    fig.text(0.012, 0.985, "Top ideas found, by run and representation", fontsize=14, fontweight="bold",
             color=tc.INK, va="top")
    fig.text(0.012, 0.985 - 0.32 / fig.get_size_inches()[1],
             "dot = pooled yield (all top ideas, score ≥ 4, ÷ all dollars or tokens) · line = 95% bootstrap interval · "
             "50-idea runs: M6, medium effort, 10 calls per representation", fontsize=9, color=tc.INK2, va="top")
    fig.legend(handles=legend_handles(), loc="lower center", ncol=4, frameon=False, fontsize=10,
               bbox_to_anchor=(0.55, 0.0))
    h = fig.get_size_inches()[1]
    fig.subplots_adjust(left=0.2, right=0.985, top=1 - 1.0 / h, bottom=0.95 / h)
    out = cr.HERE / "results" / "charts" / f"fig_yield_dotplot{suffix}.png"
    fig.savefig(out, dpi=200, facecolor=tc.SURFACE)
    plt.close(fig)
    write(rows, cr.HERE / "results" / f"fig_yield_dotplot{suffix}.csv")
    print(f"-> {out.relative_to(cr.HERE)}")


def ratio_figure(models, suffix: str) -> None:
    data = ratios(models)
    titles = [t for t, _ in data]
    fifty = [(t, r) for t, r in data if not t.split(" · ")[1].startswith("5 ")]
    pooled_rows = []
    for label, keep in (("Pooled, Claude runs", lambda t: family(t) == "Claude"),
                        ("Pooled, Chinese runs" if all(t.split(" · ")[0] in CHINESE for t, _ in fifty if family(t) != "Claude")
                         else "Pooled, other runs", lambda t: family(t) != "Claude"),
                        ("Pooled, all 50-idea runs", lambda t: True)):
        sel = [r for t, r in fifty if keep(t)]
        if len(sel) < 2 or (len(sel) == len(fifty) and not label.startswith("Pooled, all")):
            continue
        res = {}
        for c in ("A", "B", "R"):
            p = pa.pooled([(r[c][3], r[c][4]) for r in sel])
            res[c] = (p["ratio"], p["lo"], p["hi"])
        pooled_rows.append((f"{label} ({len(sel)})", res))
    labels = [row_label(t) for t in titles] + [p[0] for p in pooled_rows]
    n = len(labels)
    fig, ax = plt.subplots(figsize=(9.5, 1.15 + 0.5 * n + 1.3))
    fig.patch.set_facecolor(tc.SURFACE)
    spans = group_spans(titles) + ([(len(titles), n - 1, "pooled")] if pooled_rows else [])
    style(ax, n, labels, spans, show_labels=True)
    ax.axvline(1, color=tc.INK2, lw=1.1, zorder=2)
    off = {"A": -0.2, "B": 0.0, "R": 0.2}
    rows = []
    for i, (title, res) in enumerate(data):
        for c in ("A", "B", "R"):
            r, lo, hi = res[c][:3]
            dot(ax, i + off[c], r, lo, hi, c)
            rows.append({"row": title, "condition": c, "ratio_to_no_graph": round(r, 3), "lo": round(lo, 3), "hi": round(hi, 3)})
    for j, (label, res) in enumerate(pooled_rows):
        i = len(titles) + j
        for c in ("A", "B", "R"):
            r, lo, hi = res[c]
            dot(ax, i + off[c], r, lo, hi, c, size=8, hollow=True)
            rows.append({"row": label, "condition": c, "ratio_to_no_graph": round(r, 3), "lo": round(lo, 3), "hi": round(hi, 3)})
    for i in range(len(titles), n):
        ax.get_yticklabels()[i].set_fontweight("bold")
    ax.set_xscale("log")
    ticks = [0.25, 0.5, 1, 2]
    ax.set_xticks(ticks, [f"{t:g}×" for t in ticks])
    lows = [x["lo"] for x in rows] + [x["ratio_to_no_graph"] for x in rows]
    highs = [x["hi"] for x in rows] + [x["ratio_to_no_graph"] for x in rows]
    ax.set_xlim(min(lows) / 1.1, max(highs) * 1.1)
    ax.set_xlabel("yield relative to no graph (top ideas per token, log scale)", color=tc.INK2, fontsize=10)
    ax.text(0.96, 1.01, "← worse than no graph", ha="right", va="bottom", fontsize=9, color=tc.INK2,
            transform=ax.get_xaxis_transform())
    ax.text(1.04, 1.01, "better than no graph →", ha="left", va="bottom", fontsize=9, color=tc.INK2,
            transform=ax.get_xaxis_transform())
    fig.text(0.012, 0.985, "How each representation compares with giving no graph", fontsize=14,
             fontweight="bold", color=tc.INK, va="top")
    fig.text(0.012, 0.985 - 0.32 / fig.get_size_inches()[1],
             "dot = yield ÷ no graph's yield · line = 95% bootstrap interval · hollow = pooled over runs "
             "(random effects) · 5-idea row: R and C at high effort, A and B at medium", fontsize=8.5,
             color=tc.INK2, va="top")
    fig.legend(handles=legend_handles(("A", "B", "R")), loc="lower center", ncol=3, frameon=False, fontsize=10,
               bbox_to_anchor=(0.6, 0.0))
    h = fig.get_size_inches()[1]
    fig.subplots_adjust(left=0.31, right=0.97, top=1 - 1.15 / h, bottom=0.95 / h)
    out = cr.HERE / "results" / "charts" / f"fig_ratio_forest{suffix}.png"
    fig.savefig(out, dpi=200, facecolor=tc.SURFACE)
    plt.close(fig)
    write(rows, cr.HERE / "results" / f"fig_ratio_forest{suffix}.csv")
    print(f"-> {out.relative_to(cr.HERE)}")


def write(rows, path) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cr.models_arg(ap)
    args = ap.parse_args()
    models = args.models if args.models is not None else cr.DEFAULT_MODELS
    suffix = cr.models_suffix(args.models)
    yield_figure(models, suffix)
    ratio_figure(models, suffix)


if __name__ == "__main__":
    main()
