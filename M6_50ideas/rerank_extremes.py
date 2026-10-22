#!/usr/bin/env python3
"""
rerank_extremes.py: does a content-only judge still see Fable's ideas as better?

  cd M6_50ideas
  python rerank_extremes.py pick       # no API: top 20 and bottom 20 of each model -> results/extremes/extremes_120.csv
  python rerank_extremes.py rate       # API (Opus): rate the 120 ideas on content only -> results/extremes/ratings.jsonl
  python rerank_extremes.py chart      # no API: Opus's top 20 and bottom 20, pie charts by model

Pick. From each model's ideas_scored.csv (Haiku: results/, Opus: results/opus/, Fable: results/fable/), the
20 ideas with the highest Sonnet score and the 20 with the lowest (ties broken at random, seed 7). 120 ideas.
By construction each model has 20 of Sonnet's "top" and 20 of its "bottom".

Rate. A second judge (default claude-opus-5-5, high effort) rates every idea 1-10 on four criteria, told to
judge the engineering content only and to disregard wording, polish, length and jargon. Ideas are shuffled
together (seed 7) and sent in batches of 10, with no model, condition, Sonnet score or position shown.
Resumable: re-running only rates what is missing.

Chart. Content score = mean of the four ratings. The 20 highest and the 20 lowest of the 120 by content score
(ties at the cut broken by Sonnet's score, then at random) are split by the model that wrote them: two pies,
plus how many of each pie came from Sonnet's own top or bottom 20. If the content-only judge spread the top
20 evenly (about 7 per model), the models' ideas are comparable once style is set aside.

Caveat: Opus rates its own ideas here, blind to authorship, but a model may still prefer its own style;
--model claude-sonnet-5-5 repeats the rating with another judge.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

from common import HERE, call_claude, need_label, parse_json

OUT = HERE / "results" / "extremes"
PICK = OUT / "extremes_120.csv"
SOURCES = [("Haiku", HERE / "results" / "ideas_scored.csv"),
           ("Opus", HERE / "results" / "opus" / "ideas_scored.csv"),
           ("Fable", HERE / "results" / "fable" / "ideas_scored.csv")]
N = 20
SEED = 7
CRITERIA = ["relevance", "novelty", "feasibility", "specificity"]
MODEL_COLOR = {"Haiku": "#4C78A8", "Opus": "#F58518", "Fable": "#54A24B"}

SYSTEM = (
    "You are an expert panel of product engineers judging product-innovation ideas for their engineering "
    "content only. Judge what the idea would actually do and how, never how it is written. Respond with "
    "valid JSON only.")

USER = """BRIEF
Product: countertop microwave oven
Target market need: M6: {need_label}
Innovation operator: SUBSTITUTE (replace parts with something cheaper or simpler that fulfils the same function equally well or better)

HOW TO JUDGE
Before rating an idea, restate it to yourself in plain words: what it replaces, what replaces it, how that works.
Rate that restatement, not the text. Disregard entirely:
- wording, eloquence, confidence, enthusiasm and catchy titles;
- length: a short idea with a clear mechanism is as good as a long one with the same mechanism;
- jargon, part numbers and technical-sounding detail that add no real mechanism.
Two ideas with the same mechanism must get the same ratings however differently they are written.

IDEAS
{ideas}

Rate EACH idea from 1 (poor) to 10 (excellent) on:
- relevance: how well the mechanism serves the target need
- novelty: how far the mechanism goes beyond what microwave ovens already do
- feasibility: how technically plausible the mechanism is
- specificity: how clearly the mechanism is defined (what, by what, how), not how much detail is written

Return JSON with one entry per idea, in the same order:
{{"ratings": [{{"key": "X001", "relevance": 0, "novelty": 0, "feasibility": 0, "specificity": 0}}]}}"""


def idea_text(r: dict) -> str:
    return (f"{r['title']}\n   New elements: {r.get('new_elements') or '-'}\n"
            f"   Why: {r.get('rationale') or '-'}")


def cmd_pick(args) -> None:
    rng = random.Random(SEED)
    rows = []
    for model, path in SOURCES:
        if not path.exists():
            sys.exit(f"{path} not found")
        ideas = list(csv.DictReader(path.open(encoding="utf-8")))
        if "rationale" not in ideas[0]:
            sys.exit(f"{path} has no idea text: re-run `score_ideas.py table` for {model}")
        for r in ideas:
            r["_tie"] = rng.random()
        ideas.sort(key=lambda r: (-float(r["score"]), r["_tie"]))
        for group, part in (("top", ideas[:N]), ("bottom", ideas[-N:])):
            for r in part:
                rows.append({"model": model, "sonnet_group": group, "sonnet_score": r["score"],
                             "idea_id": r["idea_id"], "condition": r["condition"], "position": r["position"],
                             "title": r["title"], "new_elements": r.get("new_elements", ""),
                             "rationale": r.get("rationale", "")})
    rng.shuffle(rows)
    for k, r in enumerate(rows, 1):
        r["key"] = f"X{k:03d}"                         # the only id the second judge sees
    OUT.mkdir(parents=True, exist_ok=True)
    with PICK.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["key", "model", "sonnet_group", "sonnet_score", "idea_id", "condition",
                                           "position", "title", "new_elements", "rationale"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} ideas -> {PICK}")
    for model, _ in SOURCES:
        sc = [float(r["sonnet_score"]) for r in rows if r["model"] == model]
        top = [float(r["sonnet_score"]) for r in rows if r["model"] == model and r["sonnet_group"] == "top"]
        bot = [float(r["sonnet_score"]) for r in rows if r["model"] == model and r["sonnet_group"] == "bottom"]
        print(f"  {model:<6} Sonnet top 20: {min(top):.2f}-{max(top):.2f}   bottom 20: {min(bot):.2f}-{max(bot):.2f}")


def ratings_path(model: str) -> Path:
    return OUT / f"ratings_{model}.jsonl"


def done(model: str) -> dict:
    got = {}
    p = ratings_path(model)
    if p.exists():
        for line in p.open(encoding="utf-8"):
            r = json.loads(line)
            if r.get("ok"):
                for x in r["ratings"]:
                    got[x["key"]] = x
    return got


def cmd_rate(args) -> None:
    if not PICK.exists():
        sys.exit("run `python rerank_extremes.py pick` first")
    rows = list(csv.DictReader(PICK.open(encoding="utf-8")))
    have = done(args.model)
    todo = [r for r in rows if r["key"] not in have]
    batches = [todo[i:i + args.batch] for i in range(0, len(todo), args.batch)]
    print(f"{len(rows)} ideas, {len(have)} rated, {len(todo)} to rate in {len(batches)} requests with {args.model}")
    label = need_label()
    for b in batches:
        ideas = "\n".join(f"{r['key']}. {idea_text(r)}" for r in b)
        prompt = USER.format(need_label=label, ideas=ideas)
        if args.dry_run:
            print(SYSTEM, "\n\n", prompt)
            return
        rec = {"model": args.model, "keys": [r["key"] for r in b]}
        try:
            text, usage = call_claude(SYSTEM, prompt, args.model, args.effort, args.max_tokens)
            out = parse_json(text)
            rt = out.get("ratings") if isinstance(out, dict) else None
            keys = {r["key"] for r in b}
            good = [x for x in (rt or []) if isinstance(x, dict) and x.get("key") in keys
                    and all(isinstance(x.get(c), (int, float)) for c in CRITERIA)]
            if len(good) != len(b):
                raise ValueError(f"expected {len(b)} ratings, got {len(good)}: {text[:150]}")
            rec.update(ok=True, ratings=good, **usage)
        except Exception as exc:                       # logged; re-run to retry
            rec.update(ok=False, error=f"{type(exc).__name__}: {exc}")
        with ratings_path(args.model).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"  {rec['keys'][0]}..{rec['keys'][-1]}: {'ok' if rec.get('ok') else rec['error'][:80]}")
    left = len(rows) - len(done(args.model))
    print(f"{left} ideas still unrated" + (" (re-run the same command)" if left else "; next: chart"))


def cmd_chart(args) -> None:
    import matplotlib.pyplot as plt

    rows = list(csv.DictReader(PICK.open(encoding="utf-8")))
    have = done(args.model)
    missing = [r["key"] for r in rows if r["key"] not in have]
    if missing:
        sys.exit(f"{len(missing)} ideas unrated: run `python rerank_extremes.py rate` again")
    rng = random.Random(SEED)
    for r in rows:
        r["content"] = sum(have[r["key"]][c] for c in CRITERIA) / len(CRITERIA)
        r["_tie"] = rng.random()
    rows.sort(key=lambda r: (-r["content"], -float(r["sonnet_score"]), r["_tie"]))
    top, bottom = rows[:N], rows[-N:]
    judge = args.model.replace("claude-", "").replace("-5-5", " 5.5").replace("-5-1", " 5.1").title()

    with (OUT / f"rerank_{args.model}.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["rank", "key", "model", "sonnet_group", "sonnet_score", "content",
                                           *CRITERIA, "title"])
        w.writeheader()
        for k, r in enumerate(rows, 1):
            w.writerow({"rank": k, "key": r["key"], "model": r["model"], "sonnet_group": r["sonnet_group"],
                        "sonnet_score": r["sonnet_score"], "content": round(r["content"], 2),
                        **{c: have[r["key"]][c] for c in CRITERIA}, "title": r["title"]})

    models = [m for m, _ in SOURCES]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.4))
    for ax, part, name in ((axes[0], top, "top 20"), (axes[1], bottom, "bottom 20")):
        cnt = Counter(r["model"] for r in part)
        keep = [m for m in models if cnt[m]]
        from_top = Counter(r["model"] for r in part if r["sonnet_group"] == "top")
        labels = [f"{m}: {cnt[m]} of 20\n({from_top[m]} also in\nSonnet's top 20)" for m in keep]
        ax.pie([cnt[m] for m in keep], labels=labels, colors=[MODEL_COLOR[m] for m in keep], startangle=90,
               counterclock=False, wedgeprops={"linewidth": 1.5, "edgecolor": "white"},
               radius=0.8, labeldistance=1.15, textprops={"fontsize": 10})
        ax.set_title(f"Second judge ({judge}): {name}", fontsize=13, fontweight="bold")
    agree_top = sum(r["sonnet_group"] == "top" for r in top)
    agree_bot = sum(r["sonnet_group"] == "bottom" for r in bottom)
    fig.suptitle("Who wrote the best and worst ideas, judged on content only?", fontsize=14, fontweight="bold",
                 x=0.03, ha="left", y=0.98)
    import textwrap
    note = (f"Two judges. The first judge (Sonnet 5.5, the study's judge) picked the 120 ideas: the 20 it scored "
            f"highest and the 20 it scored lowest for each model (M6, 50 ideas per call). The second judge ({judge}) "
            f"re-rated all 120 blind, on four criteria (1-10), told to disregard wording, polish, length and jargon; "
            f"the pies show its own top 20 and bottom 20, split by the model that wrote the ideas. An even split is "
            f"about 7 per model. In brackets: how many of those ideas the first judge had in a top 20. Overall, "
            f"{agree_top} of the second judge's top 20 and {agree_bot} of its bottom 20 match the first judge's.")
    fig.text(0.03, 0.915, textwrap.fill(note, 150), fontsize=9, color="#52514e", va="top", linespacing=1.4)
    fig.subplots_adjust(top=0.78, bottom=0.06, left=0.1, right=0.9, wspace=0.6)
    png = OUT / f"extremes_pies_{args.model}.png"
    fig.savefig(png, dpi=200, facecolor="white")
    plt.close(fig)

    print(f"{judge}'s top 20 by model:    " + ", ".join(f"{m} {Counter(r['model'] for r in top)[m]}" for m in models))
    print(f"{judge}'s bottom 20 by model: " + ", ".join(f"{m} {Counter(r['model'] for r in bottom)[m]}" for m in models))
    print(f"agreement with Sonnet: top {agree_top}/20, bottom {agree_bot}/20")
    print(f"-> {png}, {OUT / f'rerank_{args.model}.csv'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pick")
    r = sub.add_parser("rate")
    c = sub.add_parser("chart")
    for p in (r, c):
        p.add_argument("--model", default="claude-opus-5-5")
    r.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    r.add_argument("--batch", type=int, default=10)
    r.add_argument("--max-tokens", type=int, default=32000)
    r.add_argument("--dry-run", action="store_true", help="print the first request and stop")
    args = ap.parse_args()
    {"pick": cmd_pick, "rate": cmd_rate, "chart": cmd_chart}[args.cmd](args)


if __name__ == "__main__":
    main()
