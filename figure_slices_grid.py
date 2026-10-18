"""Small multiples of what each prompt contains: 4 x 4 panels of the microwave innovation matrix.

Panel 1 is the full graph (A), panel 2 the no-graph control (C, M8), panel 3 a random slice (R, for M8),
and the other 13 panels the market-need slices (B), ordered by size. In every panel the whole matrix
is drawn faintly and the part given to the model is drawn in colour.

  python figure_slices_grid.py      -> results/charts/0b_slices_grid.png / .pdf
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import yaml

from figure_innovation_matrix import ROWS, order_rows

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "charts"
COND = {"A": "#00BFC4", "B": "#C77CFF", "R": "#7CAE00", "C": "#F8766D"}  # same colours as every chart
INK, INK2, FAINT, GRID = "#1f1f1f", "#5f5f5f", "#d9d9d9", "#efefef"
NEEDS = ["M1", "M3", "M4", "M5", "M6", "M7", "M8", "M11", "M12", "M13", "M14", "M16", "M17"]
R_NEED = "M8"


def load_slice(name):
    s = yaml.safe_load(open(ROOT / "slices" / f"{name}.yaml", encoding="utf-8"))
    return {n["id"] for n in s["nodes"]}, {(e["from"], e["to"]) for e in s.get("edges", [])}


def short(label, n=34):
    label = label.split(" (")[0]
    return label if len(label) <= n else label[: n - 1].rstrip() + "…"


def main():
    g = yaml.safe_load(open(ROOT / "microwave_base_graph.yaml", encoding="utf-8"))
    nodes, edges = g["nodes"], g["edges"]
    label = {n["id"]: n["label"] for n in nodes}
    rows, x = order_rows(nodes, edges)
    y = {t: k for k, (t, _) in enumerate(ROWS)}
    pos = {i: (x[i], y[t]) for t, ids in rows.items() for i in ids}
    all_edges = [(e["from"], e["to"]) for e in edges if e["from"] in pos and e["to"] in pos]
    tokens = {r["slice_id"]: r for r in csv.DictReader(open(ROOT / "slices" / "manifest.csv"))}

    panels = [("A", "Full graph (A)", "every market need", set(pos), set(all_edges))]
    panels.append(("C", f"No graph (C), {R_NEED}", "the market need only", {R_NEED}, set()))
    rn, re_ = load_slice(f"R_{R_NEED}_s1")
    panels.append(("R", f"Random slice (R), {R_NEED}", f"same size as the {R_NEED} slice", rn, re_))
    bs = []
    for m in NEEDS:
        n_, e_ = load_slice(f"B_{m}")
        bs.append((len(n_), m, n_, e_))
    for size, m, n_, e_ in sorted(bs):
        panels.append(("B", f"Slice (B), {m}", short(label[m]), n_, e_))

    fig, axes = plt.subplots(4, 4, figsize=(12, 9.6))
    for ax, (cond, title, sub, hot_n, hot_e) in zip(axes.flat, panels):
        col = COND[cond]
        for t, _ in ROWS:
            ax.axhline(y[t], color=GRID, lw=0.5, zorder=0)
        for u, v in all_edges:
            hot = (u, v) in hot_e or (v, u) in hot_e
            ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], lw=0.7 if hot else 0.25,
                    color=col if hot else FAINT, alpha=0.9 if hot else 0.6, zorder=2 if hot else 1)
        xs = [pos[i][0] for i in pos]
        ys = [pos[i][1] for i in pos]
        hot_ids = [i for i in pos if i in hot_n]
        ax.scatter(xs, ys, s=7, color="white", edgecolors=FAINT, linewidths=0.4, zorder=3)
        if hot_ids:
            ax.scatter([pos[i][0] for i in hot_ids], [pos[i][1] for i in hot_ids], s=11, color=col,
                       edgecolors=INK, linewidths=0.25, zorder=4)
        if cond == "C":
            ax.text(0.5, 0.42, "no graph: the prompt names\nthe product and the market need", transform=ax.transAxes,
                    ha="center", va="center", fontsize=7.5, color=col, style="italic")
        n_count = len([i for i in hot_n if i in pos]) + (1 if "P1" in hot_n else 0)
        sid = {"A": "A_full", "C": f"C_{R_NEED}", "R": f"R_{R_NEED}_s1"}.get(cond, f"B_{title.split(', ')[-1]}")
        nn = int(tokens[sid]["n_nodes"]) if sid in tokens else n_count
        size_txt = f"{nn} node" if nn == 1 else f"{nn} nodes ({nn / 123:.0%})"
        ax.set_title(title, loc="left", fontsize=8.6, fontweight="bold", color=INK, pad=13)
        ax.text(0, 1.015, f"{sub} · {size_txt}", transform=ax.transAxes, fontsize=6.4, color=INK2, va="bottom")
        for s in ax.spines.values():
            s.set_edgecolor(col)
            s.set_linewidth(1.6 if cond != "B" else 0.6)
        ax.set_xticks([]), ax.set_yticks([])
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.6, len(ROWS) - 0.4)

    # row key on the first panel's left edge
    for t, name in ROWS:
        axes[0, 0].text(-0.04, y[t], name.split(" (")[0], ha="right", va="center", fontsize=6, color=INK2,
                        transform=axes[0, 0].get_yaxis_transform())
    fig.suptitle("What each prompt contains", x=0.065, ha="left", fontsize=12, fontweight="bold", y=0.985)
    fig.text(0.065, 0.955, "Each panel is the whole microwave innovation matrix (rows = layers, bottom to top: "
             "constraints, fields, technologies, components, functions, market needs, actors). "
             "Coloured nodes and edges are what the model sees.", fontsize=7.6, color=INK2)
    fig.subplots_adjust(left=0.065, right=0.99, top=0.9, bottom=0.01, wspace=0.08, hspace=0.42)
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"0b_slices_grid.{ext}", dpi=300, facecolor="white")
        print(f"-> {OUT / f'0b_slices_grid.{ext}'}")
    thumbnail(panels, pos, all_edges, y, OUT / "0b_slices_grid_thumb.png")
    single_panel("A", set(pos), set(all_edges), pos, all_edges, OUT / "0b_panel_full.png")
    n8, e8 = load_slice(f"B_{R_NEED}")
    single_panel("B", n8, e8, pos, all_edges, OUT / f"0b_panel_slice_{R_NEED}.png")
    single_panel("A", set(pos), set(all_edges), pos, all_edges, OUT / "0b_panel_full_gray.png", gray=True)
    single_panel("B", n8, e8, pos, all_edges, OUT / f"0b_panel_slice_{R_NEED}_gray.png", gray=True)


def single_panel(cond, hot_n, hot_e, pos, all_edges, out, gray=False):
    """One panel on its own (no title), for use as an example picture inside another chart.
    gray=True draws it in grey tones, so it stays in the background of a coloured chart."""
    col = "#4d4d4d" if gray else COND[cond]
    fig, ax = plt.subplots(figsize=(2.4, 1.8))
    for u, v in all_edges:
        hot = (u, v) in hot_e or (v, u) in hot_e
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], lw=0.8 if hot else 0.25,
                color=col if hot else FAINT, alpha=0.95 if hot else 0.6, zorder=2 if hot else 1)
    ax.scatter([pos[i][0] for i in pos], [pos[i][1] for i in pos], s=4, color="white", edgecolors=FAINT,
               linewidths=0.3, zorder=3)
    hot_ids = [i for i in pos if i in hot_n]
    ax.scatter([pos[i][0] for i in hot_ids], [pos[i][1] for i in hot_ids], s=7, color=col,
               edgecolors=INK, linewidths=0.2, zorder=4)
    for sp in ax.spines.values():
        sp.set_edgecolor(col)
        sp.set_linewidth(1.4)
    ax.set_xticks([]), ax.set_yticks([])
    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(-0.7, len(ROWS) - 0.3)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    fig.savefig(out, dpi=300, facecolor="white")
    plt.close(fig)
    print(f"-> {out}")


def thumbnail(panels, pos, all_edges, y, out):
    """Small version without titles, for the corner of the yield chart: borders and short tags only."""
    tags = {"A": "Full graph", "C": "No graph", "R": "Random graph"}
    fig, axes = plt.subplots(4, 4, figsize=(4.0, 3.0))
    for k, (ax, (cond, title, sub, hot_n, hot_e)) in enumerate(zip(axes.flat, panels)):
        col = COND[cond]
        for u, v in all_edges:
            hot = (u, v) in hot_e or (v, u) in hot_e
            ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], lw=0.75 if hot else 0.2,
                    color=col if hot else FAINT, alpha=0.95 if hot else 0.5, zorder=2 if hot else 1)
        hot_ids = [i for i in pos if i in hot_n]
        if hot_ids:
            ax.scatter([pos[i][0] for i in hot_ids], [pos[i][1] for i in hot_ids], s=2.5, color=col,
                       linewidths=0, zorder=4)
        tag = tags.get(cond) or ("Slices, one per\nmarket need" if k == 3 else None)
        if tag:
            ax.text(0.04, 0.95, tag, transform=ax.transAxes, fontsize=5.6, fontweight="bold", color=col,
                    va="top", ha="left", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
        for sp in ax.spines.values():
            sp.set_edgecolor(col)
            sp.set_linewidth(1.2)
        ax.set_xticks([]), ax.set_yticks([])
        ax.set_xlim(-0.03, 1.03)
        ax.set_ylim(-0.7, len(ROWS) - 0.3)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0.06, hspace=0.06)
    fig.savefig(out, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
