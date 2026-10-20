#!/usr/bin/env python3
"""
m6_thumb.py: the "what each prompt contains" thumbnail for this study, 2 x 2 panels for need M6 only.

  python m6_thumb.py      -> results/charts/m6_prompts_thumb.png   (no API calls)

The main study's thumbnail (../results/charts/0b_slices_grid_thumb.png) shows all 13 need slices, and its
no-graph and random panels are for M8. This study only used M6, so its charts show the four prompts it
actually sent: the full graph, no graph (the M6 need only), the random slice drawn for M6 (R_M6_s1, the
--r-seed 1 slice) and the M6 slice. Same drawing and colours as ../figure_slices_grid.py.
yield_chart.py and compare_runs_chart.py build it on first use.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "results" / "charts" / "m6_prompts_thumb.png"
NEED = "M6"
R_SLICE = f"R_{NEED}_s1"


def build(out: Path = OUT) -> Path:
    sys.path.insert(0, str(ROOT))
    import figure_slices_grid as fsg                       # the main study's layout, colours and slice loader
    from figure_innovation_matrix import ROWS, order_rows

    g = yaml.safe_load(open(ROOT / "microwave_base_graph.yaml", encoding="utf-8"))
    rows, x = order_rows(g["nodes"], g["edges"])
    y = {t: k for k, (t, _) in enumerate(ROWS)}
    pos = {i: (x[i], y[t]) for t, ids in rows.items() for i in ids}
    all_edges = [(e["from"], e["to"]) for e in g["edges"] if e["from"] in pos and e["to"] in pos]
    # load_slice reads from the main study's folder
    rn, re_ = fsg.load_slice(R_SLICE)
    bn, be = fsg.load_slice(f"B_{NEED}")
    panels = [("A", "Full graph", set(pos), set(all_edges)),
              ("C", f"No graph ({NEED} only)", {NEED}, set()),
              ("R", f"Random graph ({NEED})", rn, re_),
              ("B", f"Slice ({NEED})", bn, be)]

    fig, axes = plt.subplots(2, 2, figsize=(4.0, 3.0))
    for ax, (cond, tag, hot_n, hot_e) in zip(axes.flat, panels):
        col = fsg.COND[cond]
        for u, v in all_edges:
            hot = (u, v) in hot_e or (v, u) in hot_e
            ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], lw=0.9 if hot else 0.25,
                    color=col if hot else fsg.FAINT, alpha=0.95 if hot else 0.5, zorder=2 if hot else 1)
        hot_ids = [i for i in pos if i in hot_n]
        if hot_ids:
            ax.scatter([pos[i][0] for i in hot_ids], [pos[i][1] for i in hot_ids], s=6 if cond == "C" else 3,
                       color=col, linewidths=0, zorder=4)
        ax.text(0.03, 0.96, tag, transform=ax.transAxes, fontsize=8, fontweight="bold", color=col, va="top",
                ha="left", zorder=6, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
        for sp in ax.spines.values():
            sp.set_edgecolor(col)
            sp.set_linewidth(1.3)
        ax.set_xticks([]), ax.set_yticks([])
        ax.set_xlim(-0.03, 1.03)
        ax.set_ylim(-0.7, len(ROWS) - 0.3)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0.06, hspace=0.06)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=250, facecolor="white")
    plt.close(fig)
    return out


def path() -> Path:
    """The thumbnail, built if it does not exist yet."""
    return OUT if OUT.exists() else build()


if __name__ == "__main__":
    print(f"-> {build()}")
