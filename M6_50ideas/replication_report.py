#!/usr/bin/env python3
"""
replication_report.py: the verdicts fixed in CHINESE_REPLICATION.md, for every model that has been run and scored.

  cd M6_50ideas
  python replication_report.py            # no API calls -> results/replication_report.md, replication_*.csv

For each model (the paper's three Claude runs are included as the reference, read with the same rules):

  Runs       calls, ideas returned and scored, top ideas, tokens per call (input, output, reasoning), cost
  Arms       per representation: top ideas, share of top ideas, tokens per call, yield per 100k tokens and
             per US dollar, each with a 95% bootstrap interval
  Contrasts  A - B, A - C, B - C, R - C, A - R in yield per token and per dollar: difference, 95% interval,
             share of resamples in which the first arm is ahead
  Verdicts   C1 (full graph least efficient), C2 (slice no better than no graph), C3 (no graph arm beats no
             graph), per token and, for C3, per dollar; C4 is descriptive (share of top ideas, A against C)
  C5         the net-cost conclusions, from netcost_table.py's numbers

Statistics as in the paper: a top idea scores >= 4.0; yield = all top ideas / all tokens of an arm; 2,000
bootstrap resamples of calls within representation, percentile intervals; a difference between two arms is
the difference of their independently resampled yields. Each model and arm has its own fixed seed.
"""
from __future__ import annotations

import argparse
import csv
import json
import random

import compare_runs_chart as cr
import netcost_table as nt

HERE, tc = cr.HERE, cr.tc
CONDS = ["A", "B", "R", "C"]
COND_NAME = {"A": "Full graph", "B": "Need slice", "R": "Random slice", "C": "No graph"}
CONTRASTS = [("A", "B"), ("A", "C"), ("B", "C"), ("R", "C"), ("A", "R")]
SMALL, LARGE = {"haiku", "deepseek", "qwen", "glm"}, {"opus", "sonnet", "fable", "deepseekpro"}
PAPER = {"haiku", "opus", "sonnet", "fable"}
REPS = 2000


def load(key: str, th: float, tag: str = "") -> dict[str, list[dict]]:
    """condition -> calls, each {ideas, top, tokens, usd}. tag="confirm": the model's confirmation run."""
    runs, scores, _ = nt.files(key)
    if tag:
        runs = runs.with_name(f"{runs.stem}_{tag}.jsonl")
        scores = scores.parent / tag / scores.name
        if not (runs.exists() and scores.exists()):
            return {}
    out = {c: [] for c in CONDS}
    for x in cr.from_study(runs, scores).values():
        pin, pout = cr.PRICES[x["model"]]
        out[x["condition"]].append({"ideas": len(x["scores"]), "top": sum(s >= th for s in x["scores"]),
                                    "tokens": x["in"] + x["out"], "in": x["in"], "out": x["out"],
                                    "usd": (x["in"] * pin + x["out"] * pout) / 1e6})
    return out


def run_facts(key: str) -> dict:
    """What the run log says, whether or not the ideas are scored yet."""
    runs = nt.files(key)[0]
    last = {}
    for line in runs.open(encoding="utf-8"):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("ok"):
            last[r["run_id"]] = r
    rs = list(last.values())
    n = len(rs) or 1
    billed = [r["cost_usd_billed"] for r in rs if r.get("cost_usd_billed") is not None]
    lens = [r.get("n_ideas") or 0 for r in rs]
    return {"calls": len(rs), "parsed": sum(bool(r.get("parse_ok")) for r in rs),
            "cut_off": sum(r.get("stop_reason") == "max_tokens" for r in rs),
            "ideas": sum(lens), "ideas_min": min(lens, default=0), "ideas_max": max(lens, default=0),
            "in_per_call": sum(r.get("input_tokens") or 0 for r in rs) / n,
            "out_per_call": sum(r.get("output_tokens") or 0 for r in rs) / n,
            "reasoning_per_call": (sum(r.get("reasoning_tokens") or 0 for r in rs) / n
                                   if any("reasoning_tokens" in r for r in rs) else None),
            "billed": sum(billed) if billed else None,
            "served_by": sorted({str(r.get("served_by")) for r in rs if r.get("served_by")}),
            "version": sorted({str(r.get("model_version")) for r in rs if r.get("model_version")}),
            "model": sorted({str(r.get("model")) for r in rs})}


def tot(calls: list[dict]) -> dict:
    return {k: sum(c[k] for c in calls) for k in ("ideas", "top", "tokens", "usd")}


def measures(t: dict) -> dict:
    return {"per_token": 1e5 * t["top"] / t["tokens"] if t["tokens"] else float("nan"),
            "per_usd": t["top"] / t["usd"] if t["usd"] else float("nan"),
            "share": t["top"] / t["ideas"] if t["ideas"] else float("nan")}


def ci(vals: list[float]) -> tuple[float, float]:
    v = sorted(vals)
    return v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]


def analyse(key: str, th: float) -> dict:
    data = load(key, th)
    arms, boot = {}, {}
    for c in CONDS:
        if not data[c]:
            continue
        rng = random.Random(f"{tc.SEED}-report-{key}-{c}")
        boot[c] = [measures(tot([rng.choice(data[c]) for _ in data[c]])) for _ in range(REPS)]
        t = tot(data[c])
        arms[c] = {"calls": len(data[c]), **t, **measures(t),
                   "in_per_call": sum(x["in"] for x in data[c]) / len(data[c]),
                   "out_per_call": sum(x["out"] for x in data[c]) / len(data[c])}
        for m in ("per_token", "per_usd", "share"):
            arms[c][m + "_lo"], arms[c][m + "_hi"] = ci([b[m] for b in boot[c]])
    contrasts = {}
    for x, y in CONTRASTS:
        if x not in arms or y not in arms:
            continue
        for m in ("per_token", "per_usd", "share"):
            d = [a[m] - b[m] for a, b in zip(boot[x], boot[y])]
            lo, hi = ci(d)
            contrasts[(x, y, m)] = {"diff": arms[x][m] - arms[y][m], "lo": lo, "hi": hi,
                                    "ratio": arms[x][m] / arms[y][m] if arms[y][m] else float("nan"),
                                    "p_ahead": sum(v > 0 for v in d) / REPS}
    return {"arms": arms, "contrasts": contrasts, "verdicts": verdicts(arms, contrasts)}


def confirmation(key: str, th: float) -> tuple[list[str], str]:
    """Section 4's guard against chance: a contradiction stands only if 10 fresh calls per arm (replicates
    11-20) point the same way and the interval over all 20 calls per arm still excludes 0.
    Returns the report lines and a one-line outcome for the verdict table."""
    fresh = {c: v for c, v in load(key, th, "confirm").items() if v}
    if not fresh:
        return [], ""
    first = load(key, th)
    sets = {"first 10 calls (the run above)": {c: first[c] for c in fresh},
            "fresh 10 calls (replicates 11–20)": fresh,
            "all 20 calls": {c: first[c] + fresh[c] for c in fresh}}
    name = dict(nt.MODELS)[key]
    pairs = [(x, y) for x, y in CONTRASTS if x in fresh and y in fresh]
    L = [f"**{name}**: arms re-tested: {', '.join(COND_NAME[c].lower() for c in CONDS if c in fresh)}.", "",
         "| Calls | " + " | ".join(f"{c} · {COND_NAME[c]}: top ideas / ideas, yield per 100k tokens [95% CI]" for c in CONDS if c in fresh)
         + " | " + " | ".join(f"{x} − {y} per 100k tokens [95% CI] | {x} − {y} per dollar [95% CI]" for x, y in pairs) + " |",
         "|" + " --- |" * (1 + len(fresh) + 2 * len(pairs))]
    diffs = {}
    for label, data in sets.items():
        boot, cells = {}, []
        for c in CONDS:
            if c not in data:
                continue
            rng = random.Random(f"{tc.SEED}-confirm-{key}-{c}-{label}")
            boot[c] = [measures(tot([rng.choice(data[c]) for _ in data[c]])) for _ in range(REPS)]
            t = tot(data[c])
            lo, hi = ci([b["per_token"] for b in boot[c]])
            cells.append(f"{t['top']} / {t['ideas']}, **{measures(t)['per_token']:.1f}** [{lo:.1f}–{hi:.1f}]")
        for x, y in pairs:
            for m in ("per_token", "per_usd"):
                d = measures(tot(data[x]))[m] - measures(tot(data[y]))[m]
                lo, hi = ci([a[m] - b[m] for a, b in zip(boot[x], boot[y])])
                diffs[(label, x, y, m)] = (d, lo, hi)
                cells.append(f"{d:+.1f} [{lo:+.1f}, {hi:+.1f}]" + (" ✱" if lo > 0 or hi < 0 else ""))
        L.append(f"| {label} | " + " | ".join(cells) + " |")
    L.append("")
    labels, outcome = list(sets), []
    for x, y in pairs:
        d0, lo0, hi0 = diffs[(labels[0], x, y, "per_token")]
        if not (lo0 > 0 or hi0 < 0):
            continue                                  # this contrast was not a contradiction to begin with
        d1 = diffs[(labels[1], x, y, "per_token")][0]
        d2, lo2, hi2 = diffs[(labels[2], x, y, "per_token")]
        same = (d1 > 0) == (d0 > 0)
        stands = same and ((lo2 > 0) if d0 > 0 else (hi2 < 0))
        L.append(f"{x} − {y}: the fresh calls point the {'same' if same else 'OPPOSITE'} way ({d1:+.1f}); over all 20 calls "
                 f"the interval {'excludes' if (lo2 > 0 or hi2 < 0) else 'includes'} 0 ({d2:+.1f} [{lo2:+.1f}, {hi2:+.1f}]). "
                 f"**The contradiction {'STANDS (confirmed)' if stands else 'does NOT stand (not confirmed)'}.**")
        outcome.append(f"{x} − {y} {'confirmed' if stands else 'NOT confirmed'}: fresh calls {d1:+.1f}, all 20 calls "
                       f"{d2:+.1f} [{lo2:+.1f}, {hi2:+.1f}]")
    L.append("")
    return L, "; ".join(outcome)


def verdicts(arms: dict, k: dict) -> dict:
    if any(c not in arms for c in CONDS):
        return {}
    above = lambda x, y, m="per_token": k[(x, y, m)]["lo"] > 0          # CI of x - y entirely above 0
    below = lambda x, y, m="per_token": k[(x, y, m)]["hi"] < 0
    lowest = min(CONDS, key=lambda c: arms[c]["per_token"])
    if above("A", "B") or above("A", "C"):
        c1 = "CONTRADICTED"
    elif lowest != "A":
        c1 = f"not replicated ({COND_NAME[lowest].lower()} is lowest)"
    elif below("A", "C"):
        c1 = "replicated"
    else:
        c1 = "same direction, inconclusive"
    c2 = "CONTRADICTED" if above("B", "C") else ("replicated (no graph better)" if below("B", "C") else "replicated")
    c3 = "CONTRADICTED" if above("A", "C") or above("B", "C") else "replicated"
    c3d = ("CONTRADICTED" if above("A", "C", "per_usd") or above("B", "C", "per_usd") else "replicated")
    return {"C1": c1, "C2": c2, "C3": c3, "C3 per dollar": c3d}


def c5(keys: list[str], th: float) -> list[str]:
    """The net-cost conclusions, with netcost_table.py's numbers, seeds and bold rule."""
    names = dict(nt.MODELS)
    data = {k: nt.load(k, th) for k in keys}
    point = {k: nt.totals(d) for k, d in data.items()}
    boot = {k: nt.draws(k, d) for k, d in data.items()}
    measured = [nt.judge_cost_per_idea(k) for k in keys if nt.files(k)[2].exists()]
    judge = round(sum(u for u, _ in measured) / sum(n for _, n in measured), 4)
    cols = [("generation only ($0)", 0.0), (f"AI judge (${judge:g} per idea)", judge), ("human ($0.50 per idea)", nt.HUMAN)]
    beats = lambda a, b, s: sum(nt.net(x, s) < nt.net(y, s) for x, y in zip(boot[a], boot[b])) / nt.REPS
    lines, bold_all = [], set(keys)
    for label, s in cols:
        order = sorted(keys, key=lambda k: nt.net(point[k], s))
        best = order[0]
        tied = [k for k in keys if k != best and beats(k, best, s) >= 0.025]
        bold_all &= {best, *tied}
        lines.append(f"- **{label}:** cheapest is {names[best]} at ${nt.money(nt.net(point[best], s))} per top idea"
                     + (f"; indistinguishable from it: {', '.join(names[k] for k in tied)}" if tied else "")
                     + ". Order: " + ", ".join(f"{names[k]} {nt.money(nt.net(point[k], s))}" for k in order) + ".")
    small, large = [k for k in keys if k in SMALL], [k for k in keys if k in LARGE]
    out = []
    if bold_all:
        out.append("one model is cheapest or indistinguishable from the cheapest in all three columns: "
                   + ", ".join(names[k] for k in keys if k in bold_all))
    for s, label, winners, losers, what in ((judge, "the AI judge's screening cost", large, small, "large"),
                                            (nt.HUMAN, "$0.50 per idea", small, large, "small")):
        for w in winners:
            if losers and all(beats(w, l, s) >= 0.975 for l in losers):
                out.append(f"at {label}, the {what} model {names[w]} is cheaper than every "
                           f"{'small' if what == 'large' else 'large'} model (in at least 97.5% of resamples each)")
    lines.append("")
    lines.append("**C5: " + ("CONTRADICTED.** " + "; ".join(out).capitalize() + "." if out else
                             "replicated.** No model is cheapest in every column, no large model beats every small "
                             "one under AI screening, and no small model beats every large one under human screening."))
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--threshold", type=float, default=4.0)
    args = ap.parse_args()
    th = args.threshold
    names = dict(nt.MODELS)
    keys = [k for k, _ in nt.MODELS if nt.files(k)[0].exists() and nt.files(k)[1].exists()]
    res = {k: analyse(k, th) for k in keys}
    facts = {k: run_facts(k) for k in keys}
    f1 = lambda v: f"{v:.1f}"
    L = ["# Replication report: verdicts per claim", "",
         "Rules: `CHINESE_REPLICATION.md`, Sections 3 and 4. Top idea: score ≥ " + f"{th:g}. Intervals: 95%, "
         f"{REPS:,} bootstrap resamples of calls within representation. The Claude rows are the paper's own runs, "
         "read with the same rules.", "", "## Verdicts", "",
         "| Model | C1 full graph least efficient | C2 slice no better than no graph | C3 no graph arm beats no graph "
         "| C3 per dollar | Re-test of a contradiction (10 fresh calls per arm) |", "| --- | --- | --- | --- | --- | --- |"]
    conf = {k: confirmation(k, th) for k in keys}
    for k in keys:
        v = res[k]["verdicts"]
        if v:
            L.append(f"| {names[k]}{' (paper)' if k in PAPER else ''} | {v['C1']} | {v['C2']} | {v['C3']} | "
                     f"{v['C3 per dollar']} | {conf[k][1] or '–'} |")
    L += ["", "The first four columns read the first 10 calls per arm, the paper's design. A contradiction counts only "
          "if its re-test confirms it (last column)."]
    L += ["", "## Runs", "",
          "| Model | Calls | Parsed | Cut off | Ideas (per call) | Scored | Top ideas | Tokens per call: in | out | "
          "of which reasoning | Cost, list price | Billed | Served by |", "|" + " --- |" * 13]
    for k in keys:
        f, arms = facts[k], res[k]["arms"]
        scored, top = sum(a["ideas"] for a in arms.values()), sum(a["top"] for a in arms.values())
        usd = sum(a["usd"] for a in arms.values())
        L.append(f"| {names[k]} | {f['calls']} | {f['parsed']} | {f['cut_off']} | {f['ideas']:,} "
                 f"({f['ideas_min']}–{f['ideas_max']}) | {scored:,} | {top} ({100 * top / scored:.1f}%) | "
                 f"{f['in_per_call']:,.0f} | {f['out_per_call']:,.0f} | "
                 f"{'-' if f['reasoning_per_call'] is None else format(f['reasoning_per_call'], ',.0f')} | "
                 f"${usd:.2f} | {'-' if f['billed'] is None else '$' + format(f['billed'], '.2f')} | "
                 f"{', '.join(f['served_by']) or 'Anthropic API'} |")
    L += ["", "## Yield per representation", ""]
    arm_rows, con_rows = [], []
    for k in keys:
        L += [f"**{names[k]}**", "",
              "| Representation | Calls | Ideas | Top ideas | Share top [95% CI] | Tokens per call (in + out) | "
              "Top ideas per 100k tokens [95% CI] | per US dollar [95% CI] |", "|" + " --- |" * 8]
        for c in CONDS:
            a = res[k]["arms"].get(c)
            if not a:
                continue
            L.append(f"| {c} · {COND_NAME[c]} | {a['calls']} | {a['ideas']} | {a['top']} | {100 * a['share']:.1f}% "
                     f"[{100 * a['share_lo']:.1f}–{100 * a['share_hi']:.1f}] | {a['in_per_call']:,.0f} + {a['out_per_call']:,.0f} | "
                     f"**{f1(a['per_token'])}** [{f1(a['per_token_lo'])}–{f1(a['per_token_hi'])}] | "
                     f"{a['per_usd']:.1f} [{a['per_usd_lo']:.1f}–{a['per_usd_hi']:.1f}] |")
            arm_rows.append({"model": names[k], "condition": c, **{x: (round(v, 4) if isinstance(v, float) else v)
                                                                  for x, v in a.items()}})
        L += ["", "| Contrast | Yield per 100k tokens: difference [95% CI] | ratio | first arm ahead | "
              "Per dollar: difference [95% CI] | Share of top ideas: difference [95% CI] |", "|" + " --- |" * 6]
        for x, y in CONTRASTS:
            t, d, s = (res[k]["contrasts"].get((x, y, m)) for m in ("per_token", "per_usd", "share"))
            if not t:
                continue
            star = lambda q: " ✱" if q["lo"] > 0 or q["hi"] < 0 else ""
            L.append(f"| {x} − {y} | {t['diff']:+.1f} [{t['lo']:+.1f}, {t['hi']:+.1f}]{star(t)} | {t['ratio']:.2f}× | "
                     f"{100 * t['p_ahead']:.0f}% | {d['diff']:+.1f} [{d['lo']:+.1f}, {d['hi']:+.1f}]{star(d)} | "
                     f"{100 * s['diff']:+.1f} pts [{100 * s['lo']:+.1f}, {100 * s['hi']:+.1f}]{star(s)} |")
            for m, q in (("per_token", t), ("per_usd", d), ("share", s)):
                con_rows.append({"model": names[k], "contrast": f"{x}-{y}", "measure": m,
                                 **{a: round(b, 4) for a, b in q.items()}})
        L.append("")
    L += ["✱ = the interval excludes 0.", "", "## C4: does the full graph lower the share of top ideas?", "",
          "| Model | Share top, full graph | no graph | Difference A − C [95% CI] |", "| --- | --- | --- | --- |"]
    for k in keys:
        a, s = res[k]["arms"], res[k]["contrasts"].get(("A", "C", "share"))
        if s:
            L.append(f"| {names[k]} | {100 * a['A']['share']:.1f}% | {100 * a['C']['share']:.1f}% | "
                     f"{100 * s['diff']:+.1f} pts [{100 * s['lo']:+.1f}, {100 * s['hi']:+.1f}] |")
    conf = [line for k in keys for line in conf[k][0]]
    if conf:
        L += ["", "## Confirmation runs", "",
              "Every contradiction is re-tested with 10 fresh calls per arm (`CHINESE_REPLICATION.md`, Section 4). "
              "The verdict table above reads the first 10 calls only, as the paper's design does.", ""] + conf
    L += ["", "## C5: net cost per top idea", ""] + c5(keys, th)
    out = HERE / "results" / "replication_report.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    for name, rows in (("replication_arms.csv", arm_rows), ("replication_contrasts.csv", con_rows)):
        with (HERE / "results" / name).open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    print("\n".join(L))
    print("-> results/replication_report.md, replication_arms.csv, replication_contrasts.csv")


if __name__ == "__main__":
    main()
