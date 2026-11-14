#!/usr/bin/env python3
"""
cost_breakdown.py: what the Chinese-model round cost, what the paper's own calls cost, and what a next round
would cost, all from the logs. No API calls.

  cd M6_50ideas
  python cost_breakdown.py                 # -> results/cost_breakdown.md
  python cost_breakdown.py --reps 10       # the next-round estimate with other settings (see --help)

1. This round, as billed by OpenRouter (the `cost_usd_billed` of each call and the `usage.cost` of each
   judge batch), and the same calls at list price with no batch discount.
2. Every call logged in the repository for the paper, at list price (no batch or caching discount), so the
   two can be compared on the same basis. Actual bills can be lower if discounts or credits applied.
3. The next round: a 5-idea and a 50-idea part plus judge checks, priced from the unit costs measured in 1.
   Two settings are printed, the full plan of FULL_EXPERIMENT_PLAN.md and a lean one; flags change them.
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LIST = {"claude-haiku-5-5": (0.10, 0.50), "claude-sonnet-5-5": (2.0, 10.0), "claude-opus-5-5": (4.0, 20.0),
        "claude-fable-5-1": (10.0, 50.0), "deepseek/deepseek-v4.1-flash": (0.14, 0.42),
        "qwen/qwen3.8-flash": (0.15, 0.47), "deepseek/deepseek-v4-pro-0813": (0.659, 1.976),
        "z-ai/glm-5.3-flash": (0.15, 0.50)}
GEN = {"haiku": "claude-haiku-5-5", "deepseek": "deepseek/deepseek-v4.1-flash", "qwen": "qwen/qwen3.8-flash",
       "deepseekpro": "deepseek/deepseek-v4-pro-0813", "glm": "z-ai/glm-5.3-flash", "opus": "claude-opus-5-5"}
NAME = {"haiku": "Haiku 5.5", "deepseek": "DeepSeek V4.1 Flash", "qwen": "Qwen3.8 Flash",
        "deepseekpro": "DeepSeek V4 Pro", "glm": "GLM-5.3 Flash", "opus": "Opus 5.5"}


def rows(path: Path) -> list[dict]:
    out = []
    if path.exists():
        for line in path.open(encoding="utf-8"):
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def list_price(r: dict, model: str) -> float:
    pin, pout = LIST[model]
    return ((r.get("input_tokens") or 0) * pin + (r.get("output_tokens") or 0) * pout) / 1e6


def money(v: float) -> str:
    return f"${v:,.2f}"


# ── 1. this round ───────────────────────────────────────────────────
def this_round() -> tuple[list[tuple], dict]:
    items, unit = [], {}
    for key in ("deepseek", "qwen", "deepseekpro"):
        rs = [r for r in rows(HERE / "runs" / f"m6_50ideas_{key}.jsonl") if r.get("ok")]
        billed = sum(r.get("cost_usd_billed") or 0 for r in rs)
        items.append((f"Generation, {NAME[key]}", f"{len(rs)} calls of 50 ideas", billed,
                      sum(list_price(r, GEN[key]) for r in rs)))
        unit[f"gen50_{key}"] = billed / len(rs)
        unit[f"tokens50_{key}"] = (sum(r["input_tokens"] for r in rs) / len(rs), sum(r["output_tokens"] for r in rs) / len(rs),
                                   sum(r.get("reasoning_tokens") or 0 for r in rs) / len(rs))
    rs = [r for r in rows(HERE / "runs" / "m6_50ideas_deepseek_confirm.jsonl") if r.get("ok")]
    items.append(("Generation, confirmation calls (DeepSeek V4.1 Flash)", f"{len(rs)} calls",
                  sum(r.get("cost_usd_billed") or 0 for r in rs), sum(list_price(r, GEN["deepseek"]) for r in rs)))
    smoke = [r for f in sorted(glob.glob(str(HERE / "runs" / "smoke_*.jsonl"))) for r in rows(Path(f)) if r.get("ok")]
    items.append(("Test calls before each run (one per model)", f"{len(smoke)} calls",
                  sum(r.get("cost_usd_billed") or 0 for r in smoke), sum(list_price(r, r["model"]) for r in smoke)))
    unit["gen50_glm"] = next((r.get("cost_usd_billed") or 0) for r in smoke if r["model"] == GEN["glm"])
    # the Sonnet judge, by batch: billed cost from the batch log, list price from the tokens of each request
    n_req = billed = listed = resent = 0.0
    parts = {}
    for f in glob.glob(str(HERE / "results" / "**" / "judge_batches.jsonl"), recursive=True):
        sub = {r["batch_id"]: r for r in rows(Path(f)) if r.get("event") == "submitted"}
        for r in rows(Path(f)):
            if r.get("event") != "fetched":
                continue
            cost = (r.get("usage") or {}).get("cost") or 0
            k = "route check (12 calls the paper had scored)" if "judge_route_check" in f else \
                "confirmation calls" if "/confirm/" in f else f"{NAME[Path(f).parent.name]} run"
            n = len(sub[r["batch_id"]]["requests"])
            p = parts.setdefault(k, [0, 0.0])
            p[0] += n
            p[1] += cost
            n_req += n
            billed += cost
    for f in glob.glob(str(HERE / "results" / "**" / "idea_scores.jsonl"), recursive=True):
        if "second_judge" in f:
            continue
        for r in rows(Path(f)):
            if r.get("judge_api") in ("openrouter-batch", "openrouter") and r.get("ok"):
                listed += list_price(r, "claude-sonnet-5-5")
                if r.get("judge_api") == "openrouter":       # two requests re-sent one by one, at list price
                    resent += list_price(r, "claude-sonnet-5-5")
    for k, (n, c) in sorted(parts.items()):
        items.append((f"Sonnet 5.5 judge, {k}", f"{n:.0f} requests of 5 ideas", c, None))
    items.append(("Sonnet 5.5 judge, two requests re-sent one by one", "2 requests", resent, None))
    unit["judge_req_batch"] = billed / n_req
    unit["judge_req_list"] = listed / max(1, sum(n for n, _ in parts.values()) + 2)
    judge_list_total = listed
    # second judges
    for label, key, sub in (("Second judge DeepSeek V4 Pro, on the Haiku run", "pro", "results/second_judge/deepseek_deepseek-v4-pro-0813"),
                            ("Second judge DeepSeek V4.1 Flash, sample of all six runs", "flash", None)):
        files = [HERE / sub / "idea_scores.jsonl"] if sub else \
            [Path(f) for f in glob.glob(str(HERE / "results" / "**" / "deepseek_deepseek-v4.1-flash" / "idea_scores.jsonl"), recursive=True)]
        rs = [r for f in files for r in rows(f)]
        ok = [r for r in rs if r.get("ok")]
        b = sum(r.get("cost_usd_billed") or 0 for r in rs)
        if ok:
            items.append((label, f"{len(ok)} requests of 5 ideas", b, None))
            unit[f"judge2_{key}"] = b / len(ok)
    return items, {**unit, "judge_list_total": judge_list_total}


# ── 2. the paper's logged calls ──────────────────────────────────────
PAPER = [("Experiment 1, generation (580 calls, Haiku)", ["runs/rq1_full.jsonl"], "claude-haiku-5-5"),
         ("Experiment 1, pilot generation", ["runs/rq1_runs.jsonl", "runs/pilot_high_48k.jsonl"], "claude-haiku-5-5"),
         ("Experiment 1, judge: pairwise set comparisons", ["results/judgments.jsonl"], "claude-sonnet-5-5"),
         ("Experiment 1, judge: idea scores", ["results/idea_scores.jsonl"], "claude-sonnet-5-5"),
         ("Experiment 1, pilot judging", ["results_pilot/judgments.jsonl", "results_pilot/idea_scores.jsonl"], "claude-sonnet-5-5"),
         ("Persona follow-up, generation", ["persona_as_factor/runs/persona_runs.jsonl"], "claude-haiku-5-5"),
         ("Persona follow-up, judge (quality and patent scores)", ["persona_as_factor/results/idea_scores.jsonl",
                                                                   "persona_as_factor/results/patent_scores.jsonl"], "claude-sonnet-5-5"),
         ("Experiment 2, generation, Haiku", ["M6_50ideas/runs/m6_50ideas.jsonl"], "claude-haiku-5-5"),
         ("Experiment 2, generation, Opus", ["M6_50ideas/runs/m6_50ideas_opus.jsonl"], "claude-opus-5-5"),
         ("Experiment 2, generation, Fable", ["M6_50ideas/runs/m6_50ideas_fable.jsonl"], "claude-fable-5-1"),
         ("Experiment 2, judge (three runs)", ["M6_50ideas/results/idea_scores.jsonl", "M6_50ideas/results/opus/idea_scores.jsonl",
                                               "M6_50ideas/results/fable/idea_scores.jsonl"], "claude-sonnet-5-5"),
         ("Experiment 2, re-rating of the extremes (Opus)", ["M6_50ideas/results/extremes/ratings_claude-opus-5-5.jsonl"], "claude-opus-5-5")]


def paper() -> list[tuple]:
    out = []
    for label, files, model in PAPER:
        rs = [r for f in files for r in rows(ROOT / f) if r.get("judge_api") is None and r.get("ok")]
        cr = sum(r.get("cache_read_tokens") or 0 for r in rs)
        cw = sum(r.get("cache_write_tokens") or 0 for r in rs)
        pin = LIST[model][0]
        out.append((label, len(rs), sum(list_price(r, r.get("model") if r.get("model") in LIST else model) for r in rs)
                    + (cr * 0.1 + cw * 1.25) * pin / 1e6))
    return out


# ── 3. next round ───────────────────────────────────────────────────
def gen5(unit: dict, key: str) -> float:
    """A 5-idea call. Haiku: measured in Experiment 1 (medium effort). Others: the prompt and the reasoning of
    their 50-idea calls plus a tenth of the answer, at list price (an estimate, not a measurement)."""
    if key == "haiku":
        rs = [r for r in rows(ROOT / "runs" / "rq1_full.jsonl") if r.get("effort") == "medium" and r.get("ok")]
        return sum(list_price(r, GEN["haiku"]) for r in rs) / len(rs)
    if key == "glm":
        return unit["gen50_glm"] / 4                       # one measured call only: a rough guess
    tin, tout, reas = unit[f"tokens50_{key}"]
    pin, pout = LIST[GEN[key]]
    return (tin * pin + (reas + (tout - reas) / 10) * pout) / 1e6


def gen50(unit: dict, key: str) -> float:
    if key == "haiku":
        rs = [r for r in rows(HERE / "runs" / "m6_50ideas.jsonl") if r.get("ok")]
        return sum(list_price(r, GEN["haiku"]) for r in rs) / len(rs)
    if key == "opus":
        rs = [r for r in rows(HERE / "runs" / "m6_50ideas_opus.jsonl") if r.get("ok")]
        return sum(list_price(r, GEN["opus"]) for r in rs) / len(rs)
    return unit[f"gen50_{key}"]


def estimate(unit: dict, models5: list, reps5: int, models50: list, needs50: int, retest: float, second: float,
             second_judge: str, contingency: float) -> list[tuple]:
    j = unit["judge_req_batch"]
    calls5 = {m: 13 * 4 * reps5 for m in models5}
    calls50 = {m: needs50 * 4 * 10 for m in models50}
    req5 = sum(calls5.values())                             # one judge request per 5-idea call
    req50 = sum(calls50.values()) * 10.2                    # about 51 ideas per 50-idea call, 5 per request
    lines = [("5-idea part: generation", f"{sum(calls5.values()):,} calls ({', '.join(NAME[m] for m in models5)}; "
                                         f"13 needs, 4 representations, {reps5} replicates)",
              sum(n * gen5(unit, m) for m, n in calls5.items())),
             ("5-idea part: Sonnet judge", f"{req5:,.0f} requests", req5 * j),
             ("50-idea part: generation", f"{sum(calls50.values()):,} calls ({', '.join(NAME[m] for m in models50)}; "
                                          f"{needs50} needs, 4 representations, 10 calls)",
              sum(n * gen50(unit, m) for m, n in calls50.items())),
             ("50-idea part: Sonnet judge", f"{req50:,.0f} requests", req50 * j),
             ("Judge re-test (Sonnet again)", f"{retest:.0%} of the requests", retest * (req5 + req50) * j),
             (f"Second judge ({second_judge})", f"{second:.0%} of the requests",
              second * (req5 + req50) * unit["judge2_pro" if second_judge == "DeepSeek V4 Pro" else "judge2_flash"])]
    sub = sum(c for _, _, c in lines)
    lines.append(("Contingency", f"{contingency:.0%}", contingency * sub))
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reps", type=int, default=None, help="next round, custom: replicates per need in the 5-idea part")
    ap.add_argument("--models5", nargs="+", default=None, choices=list(NAME))
    ap.add_argument("--models50", nargs="+", default=None, choices=list(NAME))
    ap.add_argument("--needs50", type=int, default=None, help="new needs in the 50-idea part")
    args = ap.parse_args()

    items, unit = this_round()
    billed = sum(b for _, _, b, _ in items)
    gen_list = sum(l for _, _, _, l in items if l is not None)
    second_list = sum(b for label, _, b, _ in items if label.startswith("Second judge"))   # billed at the listed price
    L = ["# What it cost, and what a next round would cost", "",
         "All numbers come from the logs in this repository (`python cost_breakdown.py`).", "",
         "## 1. This round (OpenRouter key, USD 10 limit)", "",
         "| Item | Size | Billed |", "| --- | --- | --- |"]
    L += [f"| {a} | {b} | {money(c)} |" for a, b, c, _ in items]
    L += [f"| **Total** | | **{money(billed)}** |", "",
          f"The Sonnet judge went through OpenRouter's Batch API, which bills half the list price. At list price, as "
          f"the paper's runs are priced, the same round would have cost about "
          f"{money(gen_list + unit['judge_list_total'] + second_list)}: generation {money(gen_list)}, Sonnet judge "
          f"{money(unit['judge_list_total'])}, second judges {money(second_list)}.", ""]

    pp = paper()
    total = sum(c for _, _, c in pp)
    L += ["## 2. The paper's own calls, at list price", "",
          "Every call logged in the repository, priced at list price with no batch or caching discount, the same "
          "basis as the paper's per-dollar figures. An actual bill can be lower if discounts or credits applied; the "
          "logs cannot show that.", "", "| Item | Calls or requests | List price |", "| --- | --- | --- |"]
    L += [f"| {a} | {n:,} | {money(c)} |" for a, n, c in pp]
    judge = sum(c for a, _, c in pp if "judge" in a.lower() or "judging" in a.lower() or "re-rating" in a)
    L += [f"| **Total** | | **{money(total)}** |", "",
          f"Of this, generation is {money(total - judge)} (Opus and Fable alone {money(sum(c for a, _, c in pp if 'Opus' in a and 'generation' in a) + sum(c for a, _, c in pp if 'Fable' in a))}) "
          f"and judging {money(judge)}.", ""]

    j = unit["judge_req_batch"]
    L += ["## 3. A next round", "",
          "Unit costs, measured in this round unless marked:", "",
          f"- Sonnet judge, one request of 5 ideas, by batch: ${j:.4f} (list price ${unit['judge_req_list']:.4f}).",
          f"- Second judge, one request: DeepSeek V4 Pro ${unit['judge2_pro']:.4f} (mostly at the off-peak price; DeepSeek "
          f"charges twice as much at peak hours), "
          f"DeepSeek V4.1 Flash ${unit.get('judge2_flash', 0):.5f}.",
          "- Generation, one 50-idea call: " + ", ".join(f"{NAME[m]} ${gen50(unit, m):.4f}" for m in ("deepseek", "qwen", "deepseekpro", "glm", "haiku", "opus"))
          + " (GLM from its one test call; Haiku and Opus from the paper's runs at list price).",
          "- Generation, one 5-idea call: " + ", ".join(f"{NAME[m]} ${gen5(unit, m):.4f}" for m in ("deepseek", "qwen", "deepseekpro", "glm", "haiku"))
          + " (Haiku measured in Experiment 1; the others estimated from their 50-idea calls: same prompt and "
          "reasoning, a tenth of the answer).", "",
          f"The judge is the expensive part. Scoring one idea costs about ${j / 5:.4f}, which is more than generating "
          f"it with DeepSeek V4.1 Flash (${gen50(unit, 'deepseek') / 51:.5f}) or Haiku (${gen50(unit, 'haiku') / 52:.5f}). "
          "So the bill grows with the number of ideas judged, almost whatever model writes them.", ""]
    settings = [("Full plan (FULL_EXPERIMENT_PLAN.md)", dict(models5=["haiku", "deepseek", "qwen", "glm", "deepseekpro"], reps5=20,
                                                          models50=["haiku", "deepseek", "qwen", "glm", "deepseekpro"], needs50=7,
                                                          retest=0.20, second=0.15, second_judge="DeepSeek V4 Pro", contingency=0.20)),
                ("Lean", dict(models5=["haiku", "deepseek"], reps5=10, models50=["haiku", "deepseek"], needs50=5,
                              retest=0.20, second=0.15, second_judge="DeepSeek V4.1 Flash", contingency=0.20))]
    if any(v is not None for v in (args.reps, args.models5, args.models50, args.needs50)):
        base = dict(settings[0][1])
        base.update({k: v for k, v in (("reps5", args.reps), ("models5", args.models5), ("models50", args.models50),
                                        ("needs50", args.needs50)) if v is not None})
        settings.append(("Custom", base))
    for label, s in settings:
        lines = estimate(unit, **s)
        L += [f"**{label}**", "", "| Item | Size | Estimate |", "| --- | --- | --- |"]
        L += [f"| {a} | {b} | {money(c)} |" for a, b, c in lines]
        tot = sum(c for _, _, c in lines)
        jshare = sum(c for a, _, c in lines if "judge" in a.lower() or "re-test" in a.lower()) / (tot - lines[-1][2])
        L += [f"| **Total** | | **{money(tot)}** |", "", f"Judging is {jshare:.0%} of it before contingency.", ""]
    out = HERE / "results" / "cost_breakdown.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"-> {out.relative_to(HERE)}")


if __name__ == "__main__":
    main()
