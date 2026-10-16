"""Draw the microwave innovation matrix as a layered graph, with one need slice highlighted.

  python figure_innovation_matrix.py                      # full graph, M8 slice highlighted
  python figure_innovation_matrix.py --need M4            # another need's slice
  python figure_innovation_matrix.py --need none          # full graph only

Reads microwave_base_graph.yaml and slices/B_<need>.yaml; writes
results/charts/0_innovation_matrix[_<need>].png and .pdf.
"""
import argparse
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import yaml

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "charts"

# rows bottom -> top, as in the matrix; actors above the needs, constraints below the fields
ROWS = [("Constraint", "Constraints (X)"), ("Field", "Fields (D)"), ("Technology", "Technologies (T)"),
        ("Component", "Components (C)"), ("Function", "Functions (F)"), ("MarketNeed", "Market needs (M)"),
        ("Actor", "Actors (A)")]
SLICE = "#C77CFF"      # condition B colour used in every chart
INK, INK2, GRID, BASE = "#1f1f1f", "#5f5f5f", "#e6e6e6", "#bdbdbd"


def order_rows(nodes, edges):
    """Place nodes in each row, then reorder rows by the mean position of their neighbours (barycentre
    sweeps) so that edges cross less. Purely cosmetic: it does not change the graph."""
    rows = defaultdict(list)
    for n in nodes:
        if n["type"] in dict(ROWS):
            rows[n["type"]].append(n["id"])
    for r in rows.values():
        r.sort(key=lambda i: (len(i), i))
    nb = defaultdict(set)
    for e in edges:
        nb[e["from"]].add(e["to"])
        nb[e["to"]].add(e["from"])

    def xs():
        pos = {}
        for t, ids in rows.items():
            w = len(ids)
            for k, i in enumerate(ids):
                pos[i] = (k + 0.5) / w
        return pos

    for _ in range(12):
        pos = xs()
        for t in rows:
            rows[t].sort(key=lambda i: sum(pos[j] for j in nb[i] if j in pos) / max(1, sum(j in pos for j in nb[i]))
                         if any(j in pos for j in nb[i]) else pos[i])
    return rows, xs()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--need", default="M8")
    ap.add_argument("--graph", default=str(ROOT / "microwave_base_graph.yaml"))
    a = ap.parse_args()

    g = yaml.safe_load(open(a.graph, encoding="utf-8"))
    nodes, edges = g["nodes"], g["edges"]
    label = {n["id"]: n["label"] for n in nodes}
    in_slice, slice_edges = set(), set()
    if a.need.lower() != "none":
        s = yaml.safe_load(open(ROOT / "slices" / f"B_{a.need}.yaml", encoding="utf-8"))
        in_slice = {n["id"] for n in s["nodes"]}
        slice_edges = {(e["from"], e["to"]) for e in s["edges"]}

    rows, x = order_rows(nodes, edges)
    y = {t: k for k, (t, _) in enumerate(ROWS)}
    W = 16.0
    pos = {i: (x[i] * W, y[t]) for t, ids in rows.items() for i in ids}

    fig, ax = plt.subplots(figsize=(12, 6.8))
    for e in edges:
        u, v = e["from"], e["to"]
        if u not in pos or v not in pos:
            continue
        hot = (u, v) in slice_edges
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], lw=1.1 if hot else 0.45,
                color=SLICE if hot else BASE, alpha=0.95 if hot else 0.55, zorder=2 if hot else 1,
                solid_capstyle="round")
    for i, (px, py) in pos.items():
        hot = i in in_slice
        ax.scatter([px], [py], s=150, zorder=3, color=SLICE if hot else "white",
                   edgecolors=INK if hot else INK2, linewidths=1.0 if hot else 0.7)
        ax.text(px, py, i, ha="center", va="center", fontsize=4.6, zorder=4, color=INK)
    for t, name in ROWS:
        ax.text(-0.5, y[t], name, ha="right", va="center", fontsize=9, color=INK)
        ax.axhline(y[t], color=GRID, lw=0.6, zorder=0)

    n_nodes, n_edges = len(nodes), len(edges)
    ax.set_title("The microwave innovation matrix", loc="left", fontweight="bold", fontsize=12, pad=40)
    sub = f"{n_nodes} nodes · {n_edges} typed edges · product node P1 not drawn (it links to every component)"
    if in_slice:
        sub += (f"\nFilled: the need slice for {a.need} ({label.get(a.need, '')}), "
                f"{len(in_slice)} nodes and {len(slice_edges)} edges, as given to the model in condition B")
    ax.text(0, 1.015, sub, transform=ax.transAxes, fontsize=8.5, color=INK2, va="bottom")
    ax.set_xlim(-0.3, W + 0.3)
    ax.set_ylim(-0.6, len(ROWS) - 0.4)
    ax.axis("off")
    fig.subplots_adjust(left=0.13, right=0.99, top=0.88, bottom=0.02)
    OUT.mkdir(parents=True, exist_ok=True)
    stem = "0_innovation_matrix" + ("" if not in_slice else f"_{a.need}")
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{stem}.{ext}", dpi=300, facecolor="white")
        print(f"-> {OUT / f'{stem}.{ext}'}")


if __name__ == "__main__":
    main()
