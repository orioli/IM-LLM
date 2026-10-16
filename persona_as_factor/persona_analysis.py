#!/usr/bin/env python3
"""
persona_analysis.py: does the best representation depend on the persona?

  cd persona_as_factor
  python persona_analysis.py            # reads results/ideas_ranked.csv (from ../top_ideas.py report)

For every persona x representation (B need slice, C no graph) x effort, and pooled over effort:
  top-idea rate      share of ideas scoring >= 4.0 on the 4-criterion quality score (mean over needs)
  yield              top ideas per 100k tokens (all top ideas / all tokens), 95% CI
  patentable yield   ideas with patentability >= 4 per 100k tokens, 95% CI (needs --rubric patent scores)
  mean novelty, mean patentability
and the interaction: each persona's yield ratio B / C, with a 95% CI, compared across personas.

CIs: 2,000 bootstrap resamples of calls within each need (a call's 5 ideas and its tokens stay together).
Writes results/persona_summary.csv, results/persona_interaction.csv, results/persona_summary.md and
results/charts/10_persona_yield.png.
"""
from __future__ import annotations

import argparse
import csv
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))      # shared look from ../charts.py
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from charts import AXIS, COND, GRID, INK, INK2, MUTED, SURFACE, mark_style  # noqa: E402

# always this study's own folder, wherever the script is run from (running it from the project root
# would otherwise read the main study's results/ideas_ranked.csv)
RESULTS = Path(__file__).resolve().parent / "results"
OUT = RESULTS / "charts"
TOP = 4.0                 # quality score of a top idea (same as the main study)
PATENTABLE = 4            # patentability rating of a patentable idea (1-5 scale)
PERSONAS = ["engineer", "lateral", "patent"]
PERSONA_NAME = {"engineer": "Innovation engineer", "lateral": "Lateral thinker", "patent": "Patent-focused"}
CONDS = ["B", "C"]
COND_LABEL = {"B": "B · need slice", "C": "C · no graph"}
EFFORTS = ["medium", "high", "pooled"]
BOOT = 2000
# ideas that repeat a persona's exemplar (personas.yaml); counted in every cell, so the engineer is the baseline
EXEMPLAR_ECHO = {"lateral": r"wi-?fi|wireless internet|eurostar|enjoyab|entertain",
                 "patent": r"cyclon|bagless|vortex separ|dyson"}
SEED = 0


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load(path: Path) -> dict:
    """run_id -> call: persona, condition, effort, need, tokens, quality scores, patentability, novelty."""
    calls = {}
    with path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            sc = num(r.get("score"))
            if sc is None:
                continue
            c = calls.setdefault(r["run_id"], {
                "persona": r.get("persona") or "engineer", "condition": r["condition"], "effort": r["effort"],
                "need": r["target_need"], "tokens": (num(r["run_input_tokens"]) or 0) + (num(r["run_output_tokens"]) or 0),
                "scores": [], "patent": [], "novelty": [], "text": []})
            c["scores"].append(sc)
            c["patent"].append(num(r.get("patentability")))
            c["novelty"].append(num(r.get("novelty")))
            c["text"].append(" ".join(r.get(k) or "" for k in ("title", "new_elements", "rationale")))
    return calls


def group(calls: dict) -> dict:
    """(persona, condition, effort) -> need -> [calls]; effort 'pooled' holds both efforts."""
    g = defaultdict(lambda: defaultdict(list))
    for c in calls.values():
        for e in (c["effort"], "pooled"):
            g[(c["persona"], c["condition"], e)][c["need"]].append(c)
    return g


def hits(c, kind):
    if kind == "top":
        return sum(s >= TOP for s in c["scores"])
    return sum(p is not None and p >= PATENTABLE for p in c["patent"])


def yld(per_need, kind):
    h = sum(hits(c, kind) for cs in per_need.values() for c in cs)
    t = sum(c["tokens"] for cs in per_need.values() for c in cs)
    return 1e5 * h / t if t else float("nan")


def rate(per_need, kind):
    """Need-balanced share of ideas that are hits."""
    vals = []
    for cs in per_need.values():
        n = sum(len(c["scores"]) for c in cs)
        vals.append(sum(hits(c, kind) for c in cs) / n if n else 0)
    return sum(vals) / len(vals)


def mean_of(per_need, field):
    v = [x for cs in per_need.values() for c in cs for x in c[field] if x is not None]
    return sum(v) / len(v) if v else None


def resample(per_need, rng):
    return {n: [rng.choice(cs) for _ in cs] for n, cs in per_need.items()}


def ci(vals):
    v = sorted(x for x in vals if x == x)
    return (v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]) if v else (None, None)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ideas", type=Path, default=RESULTS / "ideas_ranked.csv")
    args = ap.parse_args()
    calls = load(args.ideas)
    g = group(calls)
    has_patent = any(p is not None for c in calls.values() for p in c["patent"])
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)

    # ── per cell
    rows = []
    for p in PERSONAS:
        for e in EFFORTS:
            for c in CONDS:
                pn = g.get((p, c, e))
                if not pn:
                    continue
                boots = [resample(pn, rng) for _ in range(BOOT)]
                r = {"persona": p, "condition": c, "effort": e, "needs": len(pn),
                     "calls": sum(len(cs) for cs in pn.values()),
                     "ideas": sum(len(x["scores"]) for cs in pn.values() for x in cs),
                     "tokens_per_call": sum(x["tokens"] for cs in pn.values() for x in cs) / sum(len(cs) for cs in pn.values()),
                     "top_ideas": sum(hits(x, "top") for cs in pn.values() for x in cs),
                     "top_rate": rate(pn, "top"), "yield": yld(pn, "top"),
                     "mean_score": mean_of(pn, "scores"), "mean_novelty": mean_of(pn, "novelty")}
                texts = [t for cs in pn.values() for x in cs for t in x["text"]]
                for who, pat in EXEMPLAR_ECHO.items():       # share of ideas repeating each persona's exemplar
                    r[f"echo_{who}_exemplar"] = sum(bool(re.search(pat, t, re.I)) for t in texts) / len(texts)
                r["yield_boot"] = [yld(b, "top") for b in boots]          # unsorted: pairs across cells
                r["yield_lo"], r["yield_hi"] = ci(r["yield_boot"])
                if has_patent:
                    r.update(patentable=sum(hits(x, "pat") for cs in pn.values() for x in cs),
                             patentable_rate=rate(pn, "pat"), patent_yield=yld(pn, "pat"),
                             mean_patentability=mean_of(pn, "patent"))
                    r["patent_yield_lo"], r["patent_yield_hi"] = ci([yld(b, "pat") for b in boots])
                rows.append(r)
    if not rows:
        sys.exit("No persona data found in " + str(args.ideas))

    # ── interaction: B / C yield ratio per persona, with a CI from independent resamples of both arms
    inter = []
    for p in PERSONAS:
        for e in EFFORTS:
            pb, pc = g.get((p, "B", e)), g.get((p, "C", e))
            if not (pb and pc):
                continue
            for kind in (["top", "pat"] if has_patent else ["top"]):
                yb, yc = yld(pb, kind), yld(pc, kind)
                bs = []
                for _ in range(BOOT):
                    b, c_ = yld(resample(pb, rng), kind), yld(resample(pc, rng), kind)
                    bs.append(b / c_ if c_ else float("nan"))
                lo, hi = ci(bs)
                inter.append({"persona": p, "effort": e, "measure": "top ideas" if kind == "top" else "patentable ideas",
                              "yield_B": yb, "yield_C": yc, "ratio_B_over_C": yb / yc if yc else None,
                              "ratio_lo": lo, "ratio_hi": hi})

    write(RESULTS / "persona_summary.csv", rows)
    write(RESULTS / "persona_interaction.csv", inter)
    report(rows, inter, has_patent)
    chart(rows, has_patent)
    chart_persona_boxes(rows)
    # one box per persona: all its calls, both representations and both efforts
    per_persona = {}
    for p in PERSONAS:
        pn = defaultdict(list)
        for c in calls.values():
            if c["persona"] == p:
                pn[c["need"]].append(c)
        if pn:
            per_persona[p] = (yld(pn, "top"), [yld(resample(pn, rng), "top") for _ in range(BOOT)])
    chart_persona_single(per_persona)


def write(path, rows):
    keys = [k for k in dict.fromkeys(k for r in rows for k in r) if k != "yield_boot"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k != "yield_boot"})
    print(f"-> {path}")


def f1(v, d=1):
    return "—" if v is None or v != v else f"{v:.{d}f}"


def report(rows, inter, has_patent):
    md = ["# Persona as a factor: results", "",
          f"Top idea = quality score ≥ {TOP:g} (4 criteria, same prompt as the main study). "
          + (f"Patentable idea = patentability ≥ {PATENTABLE}. " if has_patent else "")
          + "Yield = hits per 100k tokens, 95% CI from resampling calls within need.", "",
          "## Per cell", "",
          "| Persona | Effort | Representation | Calls | Top-idea rate | Yield [95% CI] | Mean novelty"
          + (" | Patentable rate | Patentable yield [95% CI] | Mean patentability |" if has_patent else " |"),
          "| --- | --- | --- | --- | --- | --- | ---" + (" | --- | --- | --- |" if has_patent else " |")]
    for r in rows:
        line = (f"| {PERSONA_NAME[r['persona']]} | {r['effort']} | {COND_LABEL[r['condition']]} | {r['calls']} | "
                f"{r['top_rate']:.1%} | {f1(r['yield'])} [{f1(r['yield_lo'])}–{f1(r['yield_hi'])}] | "
                f"{f1(r['mean_novelty'], 2)}")
        if has_patent:
            line += (f" | {r['patentable_rate']:.1%} | {f1(r['patent_yield'])} "
                     f"[{f1(r['patent_yield_lo'])}–{f1(r['patent_yield_hi'])}] | {f1(r['mean_patentability'], 2)} |")
        else:
            line += " |"
        md.append(line)
    md += ["", "## Echo of the persona exemplars", "",
           "Share of ideas that repeat each persona's exemplar (Eurostar Wi-Fi; Dyson cyclone). "
           "The engineer, who sees neither, is the baseline for chance mentions.", "",
           "| Persona | Effort | Representation | Echo of Eurostar / Wi-Fi | Echo of Dyson / cyclone |",
           "| --- | --- | --- | --- | --- |"]
    for r in rows:
        md.append(f"| {PERSONA_NAME[r['persona']]} | {r['effort']} | {COND_LABEL[r['condition']]} | "
                  f"{r['echo_lateral_exemplar']:.1%} | {r['echo_patent_exemplar']:.1%} |")
    md += ["", "## Interaction: does the slice help some personas more than others?", "",
           "Ratio > 1: the need slice is more efficient than no graph for that persona.", "",
           "| Measure | Persona | Effort | Yield B | Yield C | B ÷ C [95% CI] |", "| --- | --- | --- | --- | --- | --- |"]
    for r in inter:
        md.append(f"| {r['measure']} | {PERSONA_NAME[r['persona']]} | {r['effort']} | {f1(r['yield_B'])} | "
                  f"{f1(r['yield_C'])} | {f1(r['ratio_B_over_C'], 2)} [{f1(r['ratio_lo'], 2)}–{f1(r['ratio_hi'], 2)}] |")
    md += ["", "Personas differ in the slice's benefit if their B ÷ C intervals do not overlap; "
           "overlapping intervals are not evidence of no difference."]
    (RESULTS / "persona_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"-> {RESULTS / 'persona_summary.md'}")


def chart(rows, has_patent):
    """Yield per persona and effort, B vs C side by side; second panel for patentable ideas."""
    panels = [("yield", "top ideas per 100k tokens")] + ([("patent_yield", "patentable ideas per 100k tokens")]
                                                          if has_patent else [])
    fig, axes = plt.subplots(1, len(panels), figsize=(6.2 * len(panels), 4.8), sharey=True, squeeze=False)
    labels = [(p, e) for p in PERSONAS for e in EFFORTS if any(r["persona"] == p and r["effort"] == e for r in rows)]
    ys = {lab: len(labels) - 1 - i for i, lab in enumerate(labels)}
    for ax, (key, title) in zip(axes[0], panels):
        for r in rows:
            y = ys[(r["persona"], r["effort"])] + (0.14 if r["condition"] == "B" else -0.14)
            col = COND[r["condition"]]
            lo, hi = r.get(f"{key}_lo"), r.get(f"{key}_hi")
            if lo is not None:
                ax.plot([lo, hi], [y, y], color=col, linewidth=2, solid_capstyle="round", zorder=1)
            ax.scatter([r[key]], [y], s=46, zorder=2, **mark_style(r["effort"] if r["effort"] != "pooled" else "max",   # pooled: diamond
                                                                   col, 1.6, fill=col))
        ax.set_title(title, fontsize=10, loc="left")
        ax.grid(axis="x", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_xlim(left=0)
        for k in range(1, len(PERSONAS)):                  # separators between personas
            ax.axhline(len(labels) - 0.5 - k * len(EFFORTS), color=AXIS, linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0][0].set_yticks(list(ys.values()), [f"{PERSONA_NAME[p]} · {e}" for p, e in ys])
    from matplotlib.lines import Line2D
    fig.legend(handles=[Line2D([], [], color=COND[c], linewidth=2.5, label=COND_LABEL[c]) for c in CONDS],
               loc="lower center", ncol=2, frameon=False)
    fig.suptitle("Does the best representation depend on the persona?", x=0.02, y=0.985, ha="left", va="top",
                 fontweight="bold")
    fig.text(0.02, 0.915, "Yield with 95% CI · needs M4, M8, M13 · triangle = medium, dot = high, "
             "diamond = pooled (medium and high together)",
             color=INK2, fontsize=9, va="top")
    fig.tight_layout(rect=(0, 0.06, 1, 0.87))
    fig.savefig(OUT / "10_persona_yield.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print(f"-> {OUT / '10_persona_yield.png'}")



def chart_persona_boxes(rows, effort="pooled"):
    """11b_persona_by_representation.png: for each persona, the bootstrap distribution of its yield with the need slice
    (B) and with no graph (C), pooled over effort. Box = middle 50%, whiskers = 95% CI, symbol = observed.
    Above each pair: the chance that B's yield beats C's; under each persona: the chance it beats the
    engineer (same representation), from pairing independent bootstrap draws."""
    cells = {(r["persona"], r["condition"]): r for r in rows if r["effort"] == effort and r.get("yield_boot")}
    personas = [p for p in PERSONAS if any((p, c) in cells for c in CONDS)]
    if not personas:
        return
    fig, ax = plt.subplots(figsize=(8, 5.4))
    pos = {}
    for i, p in enumerate(personas):
        for j, c in enumerate(CONDS):
            if (p, c) not in cells:
                continue
            x = i * 3 + j * 1.1
            pos[(p, c)] = x
            r, col = cells[(p, c)], COND[c]
            kw = dict(positions=[x], widths=0.75, whis=(2.5, 97.5), showfliers=False, patch_artist=True,
                      manage_ticks=False)
            bp = ax.boxplot([r["yield_boot"]], **kw)
            for b in bp["boxes"]:
                b.set(facecolor=col, alpha=0.35, edgecolor=col, linewidth=1.2)
            for k in ("whiskers", "caps"):
                for line in bp[k]:
                    line.set(color=col, linewidth=1.2)
            for m in bp["medians"]:
                m.set(color=col, linewidth=2)
            ax.scatter([x], [r["yield"]], s=36, zorder=3, color=SURFACE, edgecolors=col, linewidths=1.6)

    def p_higher(a, b):
        return sum(x > y for x, y in zip(a, b)) / len(a)

    top = max(max(r["yield_boot"]) for r in cells.values())
    for i, p in enumerate(personas):
        if (p, "B") in cells and (p, "C") in cells:                    # B vs C within persona
            pb = p_higher(cells[(p, "B")]["yield_boot"], cells[(p, "C")]["yield_boot"])
            xm = (pos[(p, "B")] + pos[(p, "C")]) / 2
            ax.plot([pos[(p, "B")], pos[(p, "B")], pos[(p, "C")], pos[(p, "C")]],
                    [top * 1.04, top * 1.07, top * 1.07, top * 1.04], color=AXIS, linewidth=1)
            ax.text(xm, top * 1.09, f"P(B > C) = {pb:.2f}", ha="center", va="bottom", fontsize=8.5, color=INK)
    labels = []
    for p in personas:                                                # persona vs engineer, per representation
        lab = PERSONA_NAME[p]
        if p != "engineer":
            parts = [f"{c}: {p_higher(cells[(p, c)]['yield_boot'], cells[('engineer', c)]['yield_boot']):.2f}"
                     for c in CONDS if (p, c) in cells and ("engineer", c) in cells]
            lab += "\nP(beats engineer)\n" + "  ".join(parts)
        labels.append(lab)
    ax.set_xticks([i * 3 + 0.55 for i in range(len(personas))], labels)
    ax.tick_params(axis="x", length=0, colors=INK)
    ax.set_ylim(0, top * 1.2)
    ax.set_xlim(-0.8, (len(personas) - 1) * 3 + 1.9)
    ax.set_ylabel(f"top ideas (score ≥ {TOP:g}) per 100k tokens")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(facecolor=COND[c], alpha=0.35, edgecolor=COND[c], label=COND_LABEL[c]) for c in CONDS],
               loc="lower center", ncol=2, frameon=False, fontsize=9)
    ax.set_title("Persona effect on top-idea yield", loc="left", fontweight="bold", pad=40)
    ax.text(0, 1.02, f"Needs M4, M8, M13 · {'medium and high effort pooled' if effort == 'pooled' else effort + ' effort'}"
            " · dot = observed yield\nbox = middle 50% of 2,000 bootstrap yields · whiskers = 95% CI",
            transform=ax.transAxes, fontsize=8.5, color=INK2, va="bottom")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(OUT / "11b_persona_by_representation.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print(f"-> {OUT / '11b_persona_by_representation.png'}")


def chart_persona_single(per_persona):
    """11_persona_effect.png: one box per persona, its yield over all of its calls (need slice and no graph,
    medium and high effort; every persona has the same design, so the pooling is like for like).
    Box = middle 50% of 2,000 bootstrap yields, whiskers = 95% CI, dot = observed.
    Above each new persona: the chance its yield beats the engineer's."""
    personas = [p for p in PERSONAS if p in per_persona]
    if not personas:
        return
    fig, ax = plt.subplots(figsize=(7, 5.2))
    col = INK2
    for x, p in enumerate(personas):
        obs, boot = per_persona[p]
        bp = ax.boxplot([boot], positions=[x], widths=0.5, whis=(2.5, 97.5), showfliers=False,
                        patch_artist=True, manage_ticks=False)
        for b in bp["boxes"]:
            b.set(facecolor=GRID, edgecolor=col, linewidth=1.2)
        for k in ("whiskers", "caps"):
            for line in bp[k]:
                line.set(color=col, linewidth=1.2)
        for m in bp["medians"]:
            m.set(color=INK, linewidth=2)
        ax.scatter([x], [obs], s=40, zorder=3, color=SURFACE, edgecolors=INK, linewidths=1.6)
        ax.text(x + 0.3, obs, f"{obs:.1f}", va="center", fontsize=9, color=INK)
    top = max(max(b) for _, b in per_persona.values())
    if "engineer" in per_persona:
        eng = per_persona["engineer"][1]
        for x, p in enumerate(personas):
            if p == "engineer":
                continue
            pb = sum(a > b for a, b in zip(per_persona[p][1], eng)) / len(eng)
            ax.text(x, top * 1.06, f"P(beats engineer) = {pb:.2f}", ha="center", va="bottom", fontsize=8.5, color=INK)
    ax.set_xticks(range(len(personas)), [PERSONA_NAME[p] for p in personas])
    ax.tick_params(axis="x", length=0, colors=INK)
    ax.set_xlim(-0.6, len(personas) - 0.4)
    ax.set_ylim(0, top * 1.18)
    ax.set_ylabel(f"top ideas (score ≥ {TOP:g}) per 100k tokens")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Persona effect on top-idea yield", loc="left", fontweight="bold", pad=40)
    ax.text(0, 1.02, "Needs M4, M8, M13 · need slice and no graph, medium and high effort pooled · dot = observed\n"
            "box = middle 50% of 2,000 bootstrap yields · whiskers = 95% CI",
            transform=ax.transAxes, fontsize=8.5, color=INK2, va="bottom")
    fig.tight_layout()
    fig.savefig(OUT / "11_persona_effect.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print(f"-> {OUT / '11_persona_effect.png'}")


if __name__ == "__main__":
    main()
