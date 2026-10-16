#!/usr/bin/env python3
"""
top_ideas.py — rank individual ideas and list the best and worst N for the paper.

The pairwise judge in analyze.py scores whole sets of 5 ideas, so individual ideas
have no score yet. This script adds one:

  score    the judge rates every idea on its own (one API call per run, resumable)
             python top_ideas.py score --logs runs/rq1_runs.jsonl runs/pilot_high_48k.jsonl

  report   rank all ideas and write the top N and bottom N with who made them,
           what they cost, and full details (no API calls)
             python top_ideas.py report --logs runs/rq1_runs.jsonl runs/pilot_high_48k.jsonl --n 10

Outputs: results/idea_scores.jsonl (raw), results/ideas_ranked.csv (every idea),
results/top_ideas.md (paper-ready tables and detail blocks).

Patentability (--rubric patent) is scored in a SEPARATE call with its own prompt, so the four
quality ratings above are produced by exactly the same prompt as before and stay comparable:
             python top_ideas.py score --rubric patent --logs ...      -> results/patent_scores.jsonl
`report` adds the patent columns to ideas_ranked.csv whenever that file exists. Runs that carry a
persona (persona_as_factor study) get a persona column; runs without one count as "engineer".

The judge sees only each idea's title, new elements and rationale: no condition,
effort, node ids or graph, so scores are blind to who made the idea.
"""
from __future__ import annotations

import argparse
import csv
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import yaml

from analyze import CRITERIA, load_runs, parse_json

RESULTS = Path("results")
SCORES = RESULTS / "idea_scores.jsonl"
PATENT_SCORES = RESULTS / "patent_scores.jsonl"
COND_NAME = {"A": "full graph", "B": "need slice", "R": "random slice", "C": "no graph"}

JUDGE_SYSTEM = (
    "You are an expert panel judging product-innovation ideas. Rate each idea on its own merits, "
    "independently of the others. Ignore writing style and length. Respond with valid JSON only.")

JUDGE_USER = """BRIEF
Product: {product}
Target market need: {need_id}: {need_label}
Innovation operator: {operator}
The brief asked for radical, wild ideas that serve the target need.

IDEAS
{ideas}

Rate EACH idea from 1 (poor) to 5 (excellent) on:
- relevance: how well it serves the target need
- novelty: how radical and non-obvious it is
- feasibility: how technically plausible it is
- specificity: how concrete it is (named components, mechanisms)

Return JSON with one entry per idea, in the same order:
{{"ratings": [{{"idea": 1, "relevance": 0, "novelty": 0, "feasibility": 0, "specificity": 0,
               "comment": "one sentence"}}]}}"""

PATENT_SYSTEM = (
    "You are an experienced patent examiner assessing product-innovation ideas. Rate each idea on its own "
    "merits, independently of the others. Ignore writing style and length. Respond with valid JSON only.")

PATENT_USER = """BRIEF
Product: {product}
Target market need: {need_id}: {need_label}
Innovation operator: {operator}
The brief asked for radical, wild ideas that serve the target need.

IDEAS
{ideas}

Rate EACH idea from 1 (poor) to 5 (excellent) on the three requirements for a patent:
- new: not already known, on the market or published in the form described
- non_obvious: not an obvious step for a skilled engineer in the field
- applicable: can be made and used as described (industrial applicability)
and give an overall patentability from 1 to 5: how likely a patent with a meaningful claim
could be granted for the idea as described. You cannot search prior art; use your knowledge
of existing products, patents and published work.

Return JSON with one entry per idea, in the same order:
{{"ratings": [{{"idea": 1, "new": 0, "non_obvious": 0, "applicable": 0, "patentability": 0,
               "comment": "one sentence"}}]}}"""

PATENT_FIELDS = ["patentability", "new", "non_obvious", "applicable"]
RUBRICS = {"quality": (JUDGE_SYSTEM, JUDGE_USER, SCORES), "patent": (PATENT_SYSTEM, PATENT_USER, PATENT_SCORES)}

IDEA_CRITERIA = [c for c in CRITERIA if c != "diversity"]   # diversity is a property of a set, not an idea


# ── Rendering ───────────────────────────────────────────────────────
def render_for_judge(ideas: list) -> str:
    """No node ids: nothing hints at the graph context."""
    out = []
    for k, i in enumerate(ideas, 1):
        parts = "; ".join(f"{n.get('label', '')} ({n.get('detail', '')})"
                          for n in (i.get("new_nodes") or []) if isinstance(n, dict))
        out.append(f"{k}. {i.get('title', '(untitled)')}\n   New elements: {parts or '-'}\n"
                   f"   Why: {i.get('rationale', '-')}")
    return "\n".join(out)


# ── SCORE ───────────────────────────────────────────────────────────
def score_run(client, run: dict, args, labels: dict) -> dict:
    system, user_t, _ = RUBRICS[args.rubric]
    rec = {"run_id": run["run_id"], "judge_model": args.judge_model, "rubric": args.rubric,
           "ts": datetime.now(timezone.utc).isoformat()}
    ideas = run.get("ideas") or []
    prompt = user_t.format(product=args.product_name, need_id=run["target_need"],
                               need_label=labels.get(run["target_need"], ""),
                               operator=args.operator_name, ideas=render_for_judge(ideas))
    t0 = time.perf_counter()
    try:
        with client.messages.stream(model=args.judge_model, max_tokens=args.max_tokens, system=system,
                                    messages=[{"role": "user", "content": prompt}],
                                    extra_body={"output_config": {"effort": args.judge_effort}}) as s:
            resp = s.get_final_message()
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        out = parse_json(text)
        ratings = out.get("ratings") if isinstance(out, dict) else None
        if not isinstance(ratings, list) or len(ratings) != len(ideas):
            raise ValueError(f"expected {len(ideas)} ratings, got: {text[:200]}")
        rec.update(ok=True, ratings=ratings, input_tokens=resp.usage.input_tokens,
                   output_tokens=resp.usage.output_tokens, latency_s=round(time.perf_counter() - t0, 2))
    except Exception as exc:
        rec.update(ok=False, error=f"{type(exc).__name__}: {exc}")
    return rec


def cmd_score(args) -> None:
    runs = [r for r in load_runs(args.logs).values() if r.get("ideas")]
    g = yaml.safe_load(args.graph.read_text(encoding="utf-8"))
    labels = {n["id"]: n["label"] for n in g["nodes"] if n["type"] == "MarketNeed"}
    RESULTS.mkdir(exist_ok=True)
    path = RUBRICS[args.rubric][2]
    done = set()
    if path.exists():
        for line in path.open(encoding="utf-8"):
            r = json.loads(line)
            if r.get("ok") and r.get("judge_model") == args.judge_model:
                done.add(r["run_id"])
    todo = [r for r in runs if r["run_id"] not in done]
    print(f"{len(runs)} runs with ideas, {len(done)} scored, {len(todo)} to score with {args.judge_model} "
          f"({args.rubric} rubric -> {path})")
    if not todo:
        return
    import anthropic
    client = anthropic.Anthropic(max_retries=5)
    lock = threading.Lock()
    with path.open("a", encoding="utf-8") as fh, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(score_run, client, r, args, labels) for r in todo]
        for i, f in enumerate(as_completed(futs), 1):
            rec = f.result()
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
            print(f"[{i}/{len(todo)}] {rec['run_id']:<22} {'ok' if rec.get('ok') else rec['error'][:80]}")


# ── REPORT ──────────────────────────────────────────────────────────
def node_label(nid: str, nodes: dict) -> str:
    n = nodes.get(nid)
    return f"{nid} ({n['label']})" if n else f"{nid} (not in graph)"


def cmd_report(args) -> None:
    runs = load_runs(args.logs)
    g = yaml.safe_load(args.graph.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in g["nodes"]}
    if not SCORES.exists():
        raise SystemExit("No results/idea_scores.jsonl yet; run `python top_ideas.py score` first.")
    scores = {}
    for line in SCORES.open(encoding="utf-8"):
        r = json.loads(line)
        if r.get("ok") and (not args.judge_model or r["judge_model"] == args.judge_model):
            scores[r["run_id"]] = r                       # later lines win
    patent = {}
    if PATENT_SCORES.exists():
        for line in PATENT_SCORES.open(encoding="utf-8"):
            r = json.loads(line)
            if r.get("ok") and (not args.judge_model or r["judge_model"] == args.judge_model):
                patent[r["run_id"]] = r["ratings"]

    ideas = []
    for run_id, s in scores.items():
        run = runs.get(run_id)
        if not run:
            continue
        n_ideas = len(run["ideas"])
        tok_in, tok_out = run.get("input_tokens") or 0, run.get("output_tokens") or 0
        for k, (idea, rating) in enumerate(zip(run["ideas"], s["ratings"]), 1):
            vals = {c: rating.get(c) for c in IDEA_CRITERIA}
            nums = [v for v in vals.values() if isinstance(v, (int, float))]
            if not nums:
                continue
            row = {
                "idea_id": f"{run_id}#{k}", "title": idea.get("title", ""),
                "score": round(sum(nums) / len(nums), 2), **vals,
                "persona": run.get("persona", "engineer"),
                "condition": run["condition"], "condition_name": COND_NAME.get(run["condition"], ""),
                "effort": run.get("effort"), "target_need": run["target_need"],
                "need_label": nodes.get(run["target_need"], {}).get("label", ""),
                "model": run.get("model"), "run_id": run_id,
                "run_input_tokens": tok_in, "run_output_tokens": tok_out,
                "tokens_per_idea": round((tok_in + tok_out) / n_ideas),
                "anchors": "; ".join(node_label(a, nodes) for a in (idea.get("anchors") or []) if isinstance(a, str)),
                "new_elements": "; ".join(f"{n.get('type', '')}: {n.get('label', '')} — {n.get('detail', '')}"
                                          for n in (idea.get("new_nodes") or []) if isinstance(n, dict)),
                "new_edges": "; ".join(f"{e.get('from')} -[{e.get('type')}]-> {e.get('to')}"
                                       for e in (idea.get("new_edges") or []) if isinstance(e, dict)),
                "rationale": idea.get("rationale", ""), "judge_comment": rating.get("comment", ""),
                "idea_words": len(render_for_judge([idea]).split()),
            }
            if patent:                                    # patentability columns, when that rubric was scored
                pr = patent.get(run_id)
                pr = pr[k - 1] if pr and len(pr) >= k and isinstance(pr[k - 1], dict) else {}
                row.update({("patentability" if f == "patentability" else f"pat_{f}"): pr.get(f)
                            for f in PATENT_FIELDS})
            if args.price_in is not None and args.price_out is not None:
                row["usd_per_idea"] = round((tok_in * args.price_in + tok_out * args.price_out) / 1e6 / n_ideas, 5)
            ideas.append(row)
    if not ideas:
        raise SystemExit("No scored ideas matched the logs.")

    # rank: mean score, then novelty, then relevance as tie-breakers
    ideas.sort(key=lambda r: (r["score"], r.get("novelty") or 0, r.get("relevance") or 0), reverse=True)
    for i, r in enumerate(ideas, 1):
        r["rank"] = i
    keys = ["rank"] + [k for k in ideas[0] if k != "rank"]
    with (RESULTS / "ideas_ranked.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(ideas)

    n = min(args.n, len(ideas) // 2) if len(ideas) > 1 else 1
    top, bottom = ideas[:n], ideas[-n:][::-1]                   # bottom listed worst first
    md = [f"# Top {n} and bottom {n} ideas", "",
          f"{len(ideas)} ideas scored individually and blind by `{next(iter(scores.values()))['judge_model']}` "
          f"on {', '.join(IDEA_CRITERIA)} (1–5). Score = mean of the four criteria. "
          "Cost per idea = the generating call's total tokens divided by its number of ideas.", ""]
    md += composition(top, bottom)
    for title, items in (("Top", top), ("Bottom", bottom)):
        md += [f"## {title} {n}", "", table(items, args), ""]
        for r in items:
            md += detail(r, args)
    (RESULTS / "top_ideas.md").write_text("\n".join(md), encoding="utf-8")
    print(f"{len(ideas)} ideas ranked -> results/ideas_ranked.csv, results/top_ideas.md (top/bottom {n})")
    for label, items in (("TOP", top), ("BOTTOM", bottom)):
        print(f"\n{label}")
        for r in items:
            print(f"  #{r['rank']:<4} {r['score']:.2f}  {r['condition']}/{r['effort']:<6} {r['target_need']:<4} "
                  f"{r['tokens_per_idea']:>6} tok  {r['title'][:60]}")


def composition(top, bottom) -> list[str]:
    """Who made the best and worst ideas: counts per condition × effort (× persona, if several)."""
    many = len({r["persona"] for r in top + bottom}) > 1
    key = (lambda r: (r["persona"], r["condition"], r["effort"])) if many else (lambda r: ("", r["condition"], r["effort"]))
    arms = sorted({key(r) for r in top + bottom})
    lines = ["## Who made them", "", "| Arm | In top | In bottom |", "| --- | --- | --- |"]
    for arm in arms:
        p, c, e = arm
        lines.append(f"| {p + ', ' if p else ''}{c} ({COND_NAME.get(c, '')}), {e} effort | "
                     f"{sum(key(r) == arm for r in top)} | {sum(key(r) == arm for r in bottom)} |")
    return lines + [""]


def table(items, args) -> str:
    cost_col = "USD / idea" if args.price_in is not None and args.price_out is not None else "Tokens / idea"
    head = f"| Rank | Idea | Score | Rel | Nov | Feas | Spec | Condition | Effort | Need | {cost_col} |"
    rows = [head, "| " + " | ".join(["---"] * 11) + " |"]
    for r in items:
        cost = f"${r['usd_per_idea']:.4f}" if "usd_per_idea" in r else f"{r['tokens_per_idea']:,}"
        rows.append(f"| {r['rank']} | {esc(r['title'])} | {r['score']:.2f} | {r['relevance']} | {r['novelty']} | "
                    f"{r['feasibility']} | {r['specificity']} | {r['condition']} ({r['condition_name']}) | "
                    f"{r['effort']} | {r['target_need']} | {cost} |")
    return "\n".join(rows)


def detail(r, args) -> list[str]:
    cost = (f"{r['tokens_per_idea']:,} tokens per idea (run: {r['run_input_tokens']:,} in + "
            f"{r['run_output_tokens']:,} out, 5 ideas)")
    if "usd_per_idea" in r:
        cost += f", ${r['usd_per_idea']:.4f}"
    return [f"### #{r['rank']} {esc(r['title'])}", "",
            f"- **Score:** {r['score']:.2f} (relevance {r['relevance']}, novelty {r['novelty']}, "
            f"feasibility {r['feasibility']}, specificity {r['specificity']})",
            f"- **Made by:** {r['model']}, condition {r['condition']} ({r['condition_name']}), "
            f"{r['effort']} effort · run `{r['run_id']}`",
            f"- **Target need:** {r['target_need']} — {r['need_label']}",
            f"- **Cost:** {cost}",
            f"- **Applied to:** {r['anchors'] or '-'}",
            f"- **New elements:** {r['new_elements'] or '-'}",
            f"- **New edges:** {r['new_edges'] or '-'}",
            f"- **Rationale:** {r['rationale'] or '-'}",
            f"- **Judge:** {r['judge_comment'] or '-'}", ""]


def esc(s: str) -> str:
    return str(s).replace("|", "\\|")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("score", "report"):
        p = sub.add_parser(name)
        p.add_argument("--logs", nargs="+", type=Path, default=[Path("runs/rq1_runs.jsonl")])
        p.add_argument("--graph", type=Path, default=Path("microwave_base_graph.yaml"))
    s = sub.choices["score"]
    s.add_argument("--judge-model", default="claude-sonnet-5-5")
    s.add_argument("--judge-effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    s.add_argument("--max-tokens", type=int, default=16000)
    s.add_argument("--product-name", default="microwave")
    s.add_argument("--operator-name", default="SUBSTITUTE (replace parts with something cheaper or simpler "
                                              "that fulfils the same function equally well or better)")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--rubric", choices=sorted(RUBRICS), default="quality",
                   help="quality = the 4 criteria (default, unchanged); patent = patentability, scored separately")
    r = sub.choices["report"]
    r.add_argument("--n", type=int, default=10, help="how many best and worst ideas to list")
    r.add_argument("--judge-model", default=None, help="only use scores from this judge model")
    r.add_argument("--price-in", type=float, help="USD per million input tokens of the generation model")
    r.add_argument("--price-out", type=float, help="USD per million output tokens of the generation model")
    args = ap.parse_args()
    {"score": cmd_score, "report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    main()
