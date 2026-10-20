#!/usr/bin/env python3
"""
compare_runs_chart.py: the slope box plots of three runs side by side, on one shared axis and one legend.

  cd M6_50ideas
  python compare_runs_chart.py                 # no API calls
  python compare_runs_chart.py --n5-needs all  # panel 1 over all 13 needs instead of M6 only
  python compare_runs_chart.py --box calls     # boxes of each call's slope instead of bootstrap slopes

Panels (each arm: full graph, slice, random graph, no graph):
  Haiku · 5 ideas/call    the main study (../results/ideas_ranked.csv), M6 only by default, A and B at medium
                          effort, R and C at high (the only effort they were run at), 5 calls per arm on M6
  Haiku · 50 ideas/call   this study, runs/m6_50ideas.jsonl + results/ideas_scored.csv, medium, 10 calls per arm
  Opus · 50 ideas/call    this study, runs/m6_50ideas_opus.jsonl + results/opus/ideas_scored.csv, medium, 10 calls
  Sonnet / Fable · 50     added automatically once runs/m6_50ideas_<model>.jsonl and results/<model>/ideas_scored.csv exist

Slope = top ideas (score >= 4.0) per 100k tokens. By default each box holds the arm's 2,000 bootstrap slopes
(calls resampled within need, as chart 8b): box = middle 50%, whiskers = 95% CI. The triangle and the number
are the pooled slope (all top ideas / all tokens). All panels share the y axis, so heights compare directly.
Writes results/charts/compare_slopes_haiku5_haiku50_opus50.png and results/compare_slopes.csv.

  python compare_runs_chart.py --unit dollars   # top ideas per US dollar instead of per 100k tokens

With --unit dollars every call's cost is its input and output tokens at the model's standard API list price
(PRICES, USD per million tokens, no batch or caching discount; output includes thinking), and the y axis is
logarithmic, because Haiku and Opus differ about 20-fold per dollar. Files get the suffix _usd.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import m6_thumb  # noqa: E402
import tail_charts as tc  # noqa: E402  (the main study's colours, names and bootstrap)

ORDER = ["A", "B", "R", "C"]                                  # same order in every panel
MAIN_EFFORT = {"A": "medium", "B": "medium", "R": "high", "C": "high"}
OUT_PNG = HERE / "results" / "charts" / "compare_slopes_haiku5_haiku50_opus50.png"   # name kept when Fable is added
OUT_CSV = HERE / "results" / "compare_slopes.csv"
EXTRA_MODELS = [("opus", "Opus"), ("sonnet", "Sonnet"), ("fable", "Fable")]   # GEN_MODEL key, panel name
# standard API list prices, USD per million tokens (input, output), from
# https://platform.claude.com/docs/en/about-claude/pricing (Haiku: prompts up to 100k tokens)
PRICES = {"claude-haiku-5-5": (0.10, 0.50), "claude-sonnet-5-5": (2.0, 10.0), "claude-opus-5-5": (4.0, 20.0),
          "claude-fable-5-1": (10.0, 50.0)}
PLOTS_RIGHT = None                                          # right edge of the 3 box panels; thumbnail after


def from_main(path: Path, needs: str) -> dict:
    """run_id -> call, from the main study's ranked ideas (5 ideas per call)."""
    calls = {}
    with path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            c, e, n = r["condition"], r["effort"], r["target_need"]
            if MAIN_EFFORT.get(c) != e or (needs == "M6" and n != "M6"):
                continue
            x = calls.setdefault(r["run_id"], {"run_id": r["run_id"], "condition": c, "effort": e, "need": n,
                                               "scores": [], "in": float(r["run_input_tokens"]),
                                               "out": float(r["run_output_tokens"]),
                                               "model": r.get("model") or "claude-haiku-5-5"})
            x["scores"].append(float(r["score"]))
    return calls


def from_study(runs: Path, scores: Path) -> dict:
    """run_id -> call, from this study's run log (tokens) and scored ideas (scores)."""
    log = {}
    for line in runs.open(encoding="utf-8"):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("ok"):
            log[r["run_id"]] = r
    calls = {}
    with scores.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            run = log.get(r["run_id"])
            if run is None:
                continue
            x = calls.setdefault(r["run_id"], {"run_id": r["run_id"], "condition": run["condition"],
                                               "effort": run.get("effort", "medium"), "need": run["target_need"],
                                               "scores": [], "in": run.get("input_tokens") or 0,
                                               "out": run.get("output_tokens") or 0, "model": run.get("model")})
            x["scores"].append(float(r["score"]))
    return calls


def compute(n5_needs: str, box: str, usd: bool, th: float):
    """The panels (title, calls) and one stats dict per panel x arm; "_box" holds what the box plot draws."""
    panels = [("Haiku · 5 ideas/call", from_main(ROOT / "results" / "ideas_ranked.csv", n5_needs)),
              ("Haiku · 50 ideas/call", from_study(HERE / "runs" / "m6_50ideas.jsonl",
                                                   HERE / "results" / "ideas_scored.csv"))]
    for key, name in EXTRA_MODELS:                     # a panel for every further model that has been run and scored
        runs, scores = HERE / "runs" / f"m6_50ideas_{key}.jsonl", HERE / "results" / key / "ideas_scored.csv"
        if runs.exists() and scores.exists():
            panels.append((f"{name} · 50 ideas/call", from_study(runs, scores)))
    # tail_charts computes 1e5 x top ideas / "tokens"; for dollars, "tokens" is set to cost x 1e5, so the
    # same functions return top ideas per dollar
    for _, calls in panels:
        for x in calls.values():
            if usd:
                if x["model"] not in PRICES:
                    sys.exit(f"no price for model {x['model']!r}: add it to PRICES")
                pin, pout = PRICES[x["model"]]
                x["usd"] = (x["in"] * pin + x["out"] * pout) / 1e6
                x["tokens"] = x["usd"] * 1e5
            else:
                x["tokens"] = x["in"] + x["out"]
    rng = random.Random(tc.SEED)
    stats = []
    for title, calls in panels:
        groups = tc.by_arm_need(calls)
        for c in ORDER:
            key = next((k for k in groups if k[0] == c), None)
            if key is None:
                continue
            pn = groups[key]
            lo, hi, draws = tc.bootstrap_yield(pn, th, rng)
            per_call = [1e5 * sum(s >= th for s in x["scores"]) / x["tokens"] for cs in pn.values() for x in cs]
            stats.append({"panel": title, "condition": c, "effort": key[1], "needs": len(pn),
                          "calls": sum(len(cs) for cs in pn.values()),
                          "ideas": sum(len(x["scores"]) for cs in pn.values() for x in cs),
                          "top_ideas": sum(s >= th for cs in pn.values() for x in cs for s in x["scores"]),
                          "tokens": sum(x["in"] + x["out"] for cs in pn.values() for x in cs),
                          "cost_usd": sum(x.get("usd", 0) for cs in pn.values() for x in cs) if usd else "",
                          "yield_per_100k": tc.yield_per_100k(pn, th), "yield_lo": lo, "yield_hi": hi,
                          "_box": draws if box == "bootstrap" else per_call})
    return panels, stats


def draw_row(axes, panels, stats, box: str, usd: bool, th: float, titles: bool = True) -> None:
    """One row of box-plot panels sharing a y axis; titles=False leaves out the panel (model) titles."""
    jitter = random.Random(1)
    for ax, (title, _) in zip(axes, panels):
        ax.set_facecolor(tc.SURFACE)
        rows = [s for s in stats if s["panel"] == title]
        pos = list(range(1, len(rows) + 1))
        bp = ax.boxplot([s["_box"] for s in rows], positions=pos, widths=0.6, showfliers=False, patch_artist=True,
                        whis=(2.5, 97.5) if box == "bootstrap" else 1.5, medianprops={"linewidth": 1.6})
        for i, s in enumerate(rows):
            col = tc.COND.get(s["condition"], tc.MUTED)
            bp["boxes"][i].set(facecolor=col + "26", edgecolor=col, linewidth=1.3)
            bp["medians"][i].set(color=col)
            for k in ("whiskers", "caps"):
                for line in bp[k][2 * i:2 * i + 2]:
                    line.set(color=col, linewidth=1.1)
            if box == "calls":
                ax.scatter([pos[i] + jitter.uniform(-0.17, 0.17) for _ in s["_box"]], s["_box"], s=11, color=col,
                           alpha=0.65, linewidths=0, zorder=3)
            ax.scatter([pos[i]], [s["yield_per_100k"]], marker="^", s=55, facecolor=tc.SURFACE, edgecolor=col,
                       linewidth=1.6, zorder=4)
            top = max(bp["caps"][2 * i + 1].get_ydata()[0], s["yield_per_100k"])
            if box == "calls":
                top = max(top, max(s["_box"]))
            v = s["yield_per_100k"]
            ax.text(pos[i], top * 1.06 if usd else top + 0.8, f"{v:.0f}" if usd and v >= 100 else f"{v:.1f}",
                    ha="center", va="bottom", fontsize=9, color=col, fontweight="bold")
        ax.set_xticks(pos, [""] * len(pos))
        ax.tick_params(axis="x", length=0)
        ax.grid(axis="y", color=tc.GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        n = rows[0]
        need = "M6" if n["needs"] == 1 else f"{n['needs']} needs"
        if titles:
            ax.set_title(title, fontsize=12, fontweight="bold", color=tc.INK, pad=22)
        cost = (f" · \\${sum(s['cost_usd'] for s in rows):,.2f} spent" if usd else "")
        ax.text(0.5, 1.015, f"{need} · {n['calls']} calls per arm · "
                f"{sum(s['top_ideas'] for s in rows)}/{sum(s['ideas'] for s in rows)} top ideas{cost}",
                transform=ax.transAxes, ha="center", va="bottom", fontsize=8.5, color=tc.INK2)
    hi = max(max(s["yield_hi"], max(s["_box"])) if box == "calls" else s["yield_hi"] for s in stats)
    if usd:
        axes[0].set_ylabel(f"top ideas (score ≥ {th:g}) per US dollar\n(log scale"
                           + (", linear below 1)" if box == "calls" else ")"))
        if box == "calls":
            # calls with no top idea have slope 0, which a log axis cannot show: symlog is linear below 1
            # and logarithmic above, so they sit on the 0 line
            axes[0].set_yscale("symlog", linthresh=1, linscale=0.6)
            axes[0].set_ylim(0, hi * 1.6)
            for ax, (title, _) in zip(axes, panels):
                for i, s_ in enumerate([s for s in stats if s["panel"] == title], 1):
                    z = sum(v == 0 for v in s_["_box"])
                    if z:
                        ax.text(i, 0.25, f"{z}/{len(s_['_box'])} at 0", ha="center", va="bottom", fontsize=7.5,
                                color=tc.INK2, zorder=6)
        else:
            lo = min(s["yield_lo"] for s in stats)
            axes[0].set_yscale("log")
            axes[0].set_ylim(lo * 0.7, hi * 1.6)
        axes[0].yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    else:
        axes[0].set_ylabel(f"top ideas (score ≥ {th:g})\nper 100k tokens")
        axes[0].set_ylim(0, hi * 1.12)


def legend_handles():
    handles = [Patch(facecolor=tc.COND[c] + "26", edgecolor=tc.COND[c], linewidth=1.3,
                     label=tc.SPREAD_NAMES[c]) for c in ORDER]
    handles.append(plt.Line2D([], [], marker="^", linestyle="", markersize=8, markerfacecolor=tc.SURFACE,
                              markeredgecolor=tc.INK2, label="pooled slope (number above)"))
    return handles


def describe(box: str, usd: bool) -> str:
    what = ("box = 2,000 bootstrap slopes (calls resampled within need): middle 50%, whiskers 95% CI"
            if box == "bootstrap" else "box = one dot per call, that call's top ideas ÷ its " + ("cost" if usd else "tokens"))
    return f"{what} · triangle and number = pooled slope, all top ideas ÷ all {'dollars' if usd else 'tokens'}"


PRICE_NOTE = (r"cost = tokens at API list price per million tokens (input / output): Haiku \$0.10 / \$0.50, "
              r"Opus \$4 / \$20, Fable \$10 / \$50; no batch or caching discount")
EFFORT_NOTE = ("efforts: 50-idea runs at medium; in the 5-idea run full graph and slice at medium, "
               "random graph and no graph at high (the only effort they were run at)")
GRID_THUMB = ROOT / "results" / "charts" / "0b_slices_grid_thumb.png"


def write_csv(stats, out_csv: Path) -> None:
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=[k for k in stats[0] if not k.startswith("_")])
        w.writeheader()
        w.writerows({k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items() if not k.startswith("_")}
                    for s in stats)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--threshold", type=float, default=4.0)
    ap.add_argument("--n5-needs", choices=["M6", "all"], default="M6")
    ap.add_argument("--box", choices=["bootstrap", "calls"], default="bootstrap")
    ap.add_argument("--unit", choices=["tokens", "dollars"], default="tokens",
                    help="cost unit: top ideas per 100k tokens (default) or per US dollar at list price")
    args = ap.parse_args()
    th = args.threshold
    usd = args.unit == "dollars"
    panels, stats = compute(args.n5_needs, args.box, usd, th)

    fig, axes = plt.subplots(1, len(panels), figsize=(4.3 * len(panels) + 3.1, 6.0), sharey=True)
    fig.patch.set_facecolor(tc.SURFACE)
    draw_row(axes, panels, stats, args.box, usd, th)
    plots_right = PLOTS_RIGHT or 1 - 3.6 / fig.get_size_inches()[0]   # leave ~3.6 in for the thumbnail
    fig.legend(handles=legend_handles(), loc="lower center", ncol=5, frameon=False, fontsize=9.5,
               bbox_to_anchor=((0.05 + plots_right) / 2, 0.01))
    fig.text(0.05, 0.975, ("Top ideas per dollar" if usd else "Top ideas per token") + ": 5 vs 50 ideas per call, "
             + " vs ".join(dict.fromkeys(t.split(" · ")[0] for t, _ in panels)), fontsize=14,
             fontweight="bold", color=tc.INK, va="top")
    fig.text(0.05, 0.925, describe(args.box, usd) + "\n" + (PRICE_NOTE + "\n" if usd else "") + EFFORT_NOTE,
             fontsize=9, color=tc.INK2, va="top", linespacing=1.4)
    top = 0.74 if usd else 0.76
    fig.subplots_adjust(left=0.05, right=plots_right, top=top, bottom=0.12, wspace=0.08)
    # right-hand panel: what each prompt contains. M6 only: the four prompts this study sent (m6_thumb.py);
    # with --n5-needs all, panel 1 spans all 13 need slices, so the main study's 4 x 4 grid is shown instead
    tc.THUMB = GRID_THUMB if args.n5_needs == "all" else m6_thumb.path()
    left = plots_right + 0.025
    tc.add_slices_thumbnail(fig, (left, 0, 0.985 - left), top=top + 0.035)
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    name = OUT_PNG if args.box == "bootstrap" else OUT_PNG.with_name(OUT_PNG.stem + "_calls.png")
    if args.n5_needs == "all":
        name = name.with_name(name.stem + "_n5allneeds.png")
    if usd:
        name = name.with_name(name.stem + "_usd.png")
    fig.savefig(name, dpi=200, facecolor=tc.SURFACE)
    plt.close(fig)

    out_csv = OUT_CSV.with_name(OUT_CSV.stem + name.stem.replace(OUT_PNG.stem, "") + ".csv")
    write_csv(stats, out_csv)
    for s in stats:
        print(f"{s['panel']:<24} {s['condition']} · {s['effort']:<6} {s['calls']:>3} calls {s['top_ideas']:>3}/"
              f"{s['ideas']:<4} top  {s['yield_per_100k']:6.1f} [{s['yield_lo']:.1f}–{s['yield_hi']:.1f}] per "
              + (f"$  (cost ${s['cost_usd']:.3f})" if usd else "100k tokens"))
    print(f"-> {name.relative_to(HERE)}, {out_csv.relative_to(HERE)}")


if __name__ == "__main__":
    main()
