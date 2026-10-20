#!/usr/bin/env python3
"""
compare_stack_chart.py: two versions of the comparison chart in one figure, one row above the other,
with one shared legend at the bottom.

  cd M6_50ideas
  python compare_stack_chart.py                        # top: per dollar, bootstrap boxes, 5-idea panel over all
                                                       # 13 needs; bottom: per token, one dot per call, M6 only
  python compare_stack_chart.py --top all:bootstrap:dollars --bottom M6:calls:tokens   # the same, spelled out

Each row is given as NEEDS:BOX:UNIT, with NEEDS = M6 | all (the 5-idea panel), BOX = bootstrap | calls,
UNIT = tokens | dollars; the options mean what they mean in compare_runs_chart.py, which draws each row.
Each row has its own y axis (shared across its panels). The model titles head the columns once, and one
"what each prompt contains" panel (the four M6 prompts) serves the whole figure.
Writes results/charts/compare_stack_<top>__<bottom>.png. No API calls.
"""
from __future__ import annotations

import argparse

import matplotlib.pyplot as plt

import compare_runs_chart as cr
import m6_thumb

tc = cr.tc


def spec(text: str) -> tuple[str, str, str]:
    needs, box, unit = text.split(":")
    if needs not in ("M6", "all") or box not in ("bootstrap", "calls") or unit not in ("tokens", "dollars"):
        raise argparse.ArgumentTypeError(f"{text!r}: expected NEEDS:BOX:UNIT, e.g. all:bootstrap:dollars")
    return needs, box, unit


def row_title(needs: str, box: str, unit: str) -> str:
    what = "Top ideas per dollar" if unit == "dollars" else "Top ideas per 100k tokens"
    how = "bootstrap slopes" if box == "bootstrap" else "one dot per call"
    where = "5-idea panel over all 13 needs" if needs == "all" else "all panels on M6"
    return f"{what} · {how} · {where}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", type=spec, default=("all", "bootstrap", "dollars"))
    ap.add_argument("--bottom", type=spec, default=("M6", "calls", "tokens"))
    ap.add_argument("--threshold", type=float, default=4.0)
    args = ap.parse_args()
    th = args.threshold

    rows = []
    for needs, box, unit in (args.top, args.bottom):
        panels, stats = cr.compute(needs, box, unit == "dollars", th)
        rows.append((needs, box, unit, panels, stats))
    n = max(len(r[3]) for r in rows)

    fig = plt.figure(figsize=(4.3 * n + 3.1, 11.0))
    fig.patch.set_facecolor(tc.SURFACE)
    plots_right = 1 - 3.6 / fig.get_size_inches()[0]
    gs = fig.add_gridspec(2, n, left=0.06, right=plots_right, top=0.80, bottom=0.07, hspace=0.36, wspace=0.08)
    for k, (needs, box, unit, panels, stats) in enumerate(rows):
        axes = [fig.add_subplot(gs[k, 0])]
        axes += [fig.add_subplot(gs[k, j], sharey=axes[0]) for j in range(1, len(panels))]
        for ax in axes[1:]:
            ax.tick_params(labelleft=False)
        # the model titles head the columns once, above the top row
        cr.draw_row(axes, panels, stats, box, unit == "dollars", th, titles=(k == 0))
        y1 = axes[0].get_position().y1
        head = y1 + (0.075 if k == 0 else 0.042)
        fig.text(0.06, head, f"{'AB'[k]}  {row_title(needs, box, unit)}", fontsize=13, fontweight="bold",
                 color=tc.INK, va="bottom")
        fig.text(0.06, head - 0.018, cr.describe(box, unit == "dollars"), fontsize=8.5, color=tc.INK2, va="bottom")
        cr.write_csv(stats, cr.HERE / "results" / f"compare_stack_row{'AB'[k]}_{needs}_{box}_{unit}.csv")
    # one "what each prompt contains" panel for the whole figure: the four M6 prompts of the 50-idea runs
    tc.THUMB = m6_thumb.path()
    left = plots_right + 0.025
    tc.add_slices_thumbnail(fig, (left, 0, 0.985 - left), top=0.62)

    models = " vs ".join(dict.fromkeys(t.split(" · ")[0] for t, _ in max((r[3] for r in rows), key=len)))
    fig.text(0.06, 0.985, f"Top ideas per token and per dollar: 5 vs 50 ideas per call, {models}", fontsize=15,
             fontweight="bold", color=tc.INK, va="top")
    notes = cr.EFFORT_NOTE + ("\n" + cr.PRICE_NOTE if any(r[2] == "dollars" for r in rows) else "")
    fig.text(0.06, 0.962, notes, fontsize=9, color=tc.INK2, va="top", linespacing=1.4)
    fig.legend(handles=cr.legend_handles(), loc="lower center", ncol=5, frameon=False, fontsize=10,
               bbox_to_anchor=((0.06 + plots_right) / 2, 0.005))
    tag = "__".join("_".join(r[:3]) for r in rows)
    out = cr.HERE / "results" / "charts" / f"compare_stack_{tag}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor=tc.SURFACE)
    plt.close(fig)
    print(f"-> {out.relative_to(cr.HERE)}")


if __name__ == "__main__":
    main()
