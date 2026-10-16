#!/usr/bin/env python3
"""
analyze.py — turn the RQ1 run logs into results.

Three steps, each its own subcommand:

  stats    cost, validity and structure tables per cell (no API calls)
             python analyze.py stats --logs runs/rq1_runs.jsonl runs/pilot_high_48k.jsonl

  judge    blind pairwise quality judging with a stronger model (API calls, resumable)
             python analyze.py judge --logs ... --pair condition A B          # A vs B, effort fixed per pair
             python analyze.py judge --logs ... --pair effort low high        # low vs high, condition fixed
             python analyze.py judge --logs ... --arms A:low B:high           # two arms, both factors differ

  summary  win rates, sign tests and the length check from the judgments (no API calls)
             python analyze.py summary --logs runs/rq1_runs.jsonl runs/pilot_high_48k.jsonl

--logs: when the same run_id appears in several log files, the LATER file wins
(e.g. high-effort reruns with a larger max_tokens replace the truncated originals).
Outputs go to results/.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
import statistics as st
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import yaml

RESULTS = Path("results")
ECHO = re.compile(r"web\s*-?cam|camera|transparent", re.I)     # the prompt's two worked examples


# ── Loading ─────────────────────────────────────────────────────────
def load_runs(paths: list[Path]) -> dict[str, dict]:
    """run_id -> record; successful calls only; later files override earlier ones."""
    runs = {}
    for p in paths:
        with p.open(encoding="utf-8") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("ok"):
                    runs[r["run_id"]] = r
    if not runs:
        sys.exit("No successful calls found in the logs.")
    return runs


def load_graph_and_slices(graph: Path, manifest: Path):
    g = yaml.safe_load(graph.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in g["nodes"]}
    edge_types = set(g["meta"]["edge_types"])
    with manifest.open(encoding="utf-8") as fh:
        slices = {row["slice_id"]: set(row["node_ids"].split()) for row in csv.DictReader(fh)}
    return nodes, edge_types, slices


def mean(xs, nd: int = 2):
    xs = [x for x in xs if x is not None]
    return round(st.mean(xs), nd) if xs else ""


# ── STATS ───────────────────────────────────────────────────────────
def idea_structure(r: dict, nodes: dict, edge_types: set, slices: dict) -> dict:
    """Per-call structural measures computed from the parsed ideas."""
    ideas = r.get("ideas") or []
    need_slice = slices.get(f"B_{r['target_need']}", set())
    seen = slices.get(r["slice_id"], set())                  # nodes this call actually saw
    anchors = [a for i in ideas for a in (i.get("anchors") or []) if isinstance(a, str)]
    edges = [e for i in ideas for e in (i.get("new_edges") or []) if isinstance(e, dict)]
    valid = [a for a in anchors if a in nodes]
    text = " ".join(f"{i.get('title', '')} " + " ".join(str(n.get("label", "")) for n in (i.get("new_nodes") or [])
                                                        if isinstance(n, dict)) for i in ideas)
    return {
        "n_anchors": len(anchors),
        "hallucinated_anchor_share": (len(anchors) - len(valid)) / len(anchors) if anchors else None,
        "anchor_not_in_prompt_share": sum(a not in seen for a in valid) / len(valid) if valid else None,
        "anchor_outside_need_slice_share": sum(a not in need_slice for a in valid) / len(valid) if valid else None,
        "new_nodes_per_idea": sum(len(i.get("new_nodes") or []) for i in ideas) / len(ideas) if ideas else None,
        "invalid_edge_type_share": (sum(e.get("type") not in edge_types for e in edges) / len(edges)) if edges else None,
        "ideas_echoing_example": sum(bool(ECHO.search(f"{i.get('title', '')} {json.dumps(i.get('new_nodes'))}"))
                                     for i in ideas),
        # length of what the judge reads: the detail-bias check
        "set_words": set_words(ideas) if ideas else None,
        "words_per_idea": set_words(ideas) / len(ideas) if ideas else None,
    }


def cmd_stats(args) -> None:
    runs = load_runs(args.logs)
    nodes, edge_types, slices = load_graph_and_slices(args.graph, args.manifest)
    RESULTS.mkdir(exist_ok=True)

    # one flat row per call (handy for your own pandas / R analysis)
    flat = []
    for r in runs.values():
        row = {k: r.get(k) for k in ("run_id", "condition", "target_need", "effort", "rep", "slice_id",
                                     "slice_n_nodes", "max_tokens", "stop_reason", "input_tokens",
                                     "output_tokens", "cache_read_tokens", "latency_s", "parse_ok", "n_ideas")}
        row["truncated"] = r.get("stop_reason") == "max_tokens"
        row["total_tokens"] = (r.get("input_tokens") or 0) + (r.get("output_tokens") or 0)
        if args.price_in is not None and args.price_out is not None:
            row["cost_usd"] = round((r["input_tokens"] * args.price_in + r["output_tokens"] * args.price_out) / 1e6, 5)
        row.update(idea_structure(r, nodes, edge_types, slices))
        row["persona"] = r.get("persona", "engineer")       # runs without a persona are the engineer
        flat.append(row)
    flat.sort(key=lambda x: (x["condition"], x["effort"] or "", x["target_need"], x["rep"]))
    write_csv(RESULTS / "calls.csv", flat)

    # aggregate per cell
    def agg(keys):
        groups = defaultdict(list)
        for row in flat:
            groups[tuple(row[k] for k in keys)].append(row)
        out = []
        for key, rows in sorted(groups.items(), key=lambda kv: [str(x) for x in kv[0]]):
            d = dict(zip(keys, key))
            d.update(
                n_calls=len(rows),
                parse_rate=round(sum(bool(x["parse_ok"]) for x in rows) / len(rows), 3),
                five_ideas_rate=round(sum(x["n_ideas"] == 5 for x in rows) / len(rows), 3),
                truncated_rate=round(sum(x["truncated"] for x in rows) / len(rows), 3),
                input_tokens=mean(x["input_tokens"] for x in rows),
                output_tokens=mean(x["output_tokens"] for x in rows),
                total_tokens=mean(x["total_tokens"] for x in rows),
                latency_s=mean(x["latency_s"] for x in rows),
            )
            if "cost_usd" in rows[0]:
                d["cost_usd_per_call"] = mean((x["cost_usd"] for x in rows), 5)
            for m in ("hallucinated_anchor_share", "anchor_not_in_prompt_share",
                      "anchor_outside_need_slice_share", "new_nodes_per_idea",
                      "invalid_edge_type_share", "ideas_echoing_example", "set_words", "words_per_idea"):
                d[m] = mean(x[m] for x in rows)
            out.append(d)
        return out

    # persona is a grouping key only when the logs hold more than one (persona_as_factor study),
    # so the main study's summaries keep exactly their columns and rows
    lead = ["persona"] if len({row["persona"] for row in flat}) > 1 else []
    by_cond_effort = agg(lead + ["condition", "effort"])
    by_cell = agg(lead + ["condition", "effort", "target_need"])
    write_csv(RESULTS / "summary_condition_effort.csv", by_cond_effort)
    write_csv(RESULTS / "summary_cells.csv", by_cell)

    cols = lead + ["condition", "effort", "n_calls", "parse_rate", "truncated_rate", "input_tokens",
            "output_tokens", "total_tokens", "words_per_idea", "anchor_outside_need_slice_share",
            "ideas_echoing_example"]
    if args.price_in is not None:
        cols.insert(8, "cost_usd_per_call")
    print_table(by_cond_effort, cols)
    print(f"\n{len(flat)} calls -> results/calls.csv, results/summary_condition_effort.csv, results/summary_cells.csv")


# ── JUDGE ───────────────────────────────────────────────────────────
JUDGE_SYSTEM = (
    "You are an expert panel judging product-innovation brainstorming. You compare two sets of ideas "
    "produced for the same brief. Judge only the ideas themselves; ignore length and formatting. "
    "Respond with valid JSON only.")

JUDGE_USER = """BRIEF
Product: {product}
Target market need: {need_id}: {need_label}
Innovation operator: {operator}
The brief asked for radical, wild ideas that serve the target need.

SET 1
{set1}

SET 2
{set2}

Score each set from 1 (poor) to 5 (excellent) on:
- relevance: how well the ideas serve the target need
- novelty: how radical and non-obvious the ideas are
- feasibility: how technically plausible the ideas are
- specificity: how concrete the ideas are (named components, mechanisms)
- diversity: how different the ideas are from each other

Then pick the better set overall for this brief.

Return JSON:
{{"set_1": {{"relevance": 0, "novelty": 0, "feasibility": 0, "specificity": 0, "diversity": 0}},
 "set_2": {{"relevance": 0, "novelty": 0, "feasibility": 0, "specificity": 0, "diversity": 0}},
 "winner": "set_1" | "set_2" | "tie",
 "reason": "one sentence"}}"""

CRITERIA = ["relevance", "novelty", "feasibility", "specificity", "diversity"]


def render_ideas(ideas: list) -> str:
    """Titles, new parts and rationale only: no node ids, so nothing hints at the graph context."""
    lines = []
    for k, i in enumerate(ideas, 1):
        parts = "; ".join(f"{n.get('label', '')} ({n.get('detail', '')})".strip()
                          for n in (i.get("new_nodes") or []) if isinstance(n, dict))
        lines.append(f"{k}. {i.get('title', '(untitled)')}\n   New elements: {parts or '-'}\n"
                     f"   Why: {i.get('rationale', '-')}")
    return "\n".join(lines)


def set_words(ideas: list | None) -> int:
    """Words in the text the judge sees for these ideas (titles, new elements, rationale)."""
    return len(render_ideas(ideas).split()) if ideas else 0


def build_arm_pairs(runs: dict, x: str, y: str) -> list[dict]:
    """Match two arms given as CONDITION:EFFORT (e.g. A:low vs B:high) on the same need and rep."""
    def parse(arm):
        c, _, e = arm.partition(":")
        if not e:
            sys.exit(f"--arms expects CONDITION:EFFORT, got '{arm}'")
        return c, e
    (cx, ex), (cy, ey) = parse(x), parse(y)
    index = {(r["condition"], r["effort"], r["target_need"], r["rep"]): r for r in runs.values()}
    pairs = []
    for (c, e, need, rep), rx in index.items():
        if (c, e) != (cx, ex):
            continue
        ry = index.get((cy, ey, need, rep))
        if ry:
            pairs.append({"pair_id": f"arms:{x}-vs-{y}|{need}|r{rep:02d}", "factor": "arms",
                          "x": x, "y": y, "target_need": need, "rep": rep, "run_x": rx, "run_y": ry})
    return sorted(pairs, key=lambda p: p["pair_id"])


def build_pairs(runs: dict, factor: str, x: str, y: str) -> list[dict]:
    """Match runs that differ only in `factor` (x vs y): same need, rep and the other factor."""
    other = "effort" if factor == "condition" else "condition"
    index = {(r[factor], r[other], r["target_need"], r["rep"]): r for r in runs.values()}
    pairs = []
    for (fv, ov, need, rep), rx in index.items():
        if fv != x:
            continue
        ry = index.get((y, ov, need, rep))
        if ry:
            pairs.append({"pair_id": f"{factor}:{x}-vs-{y}|{other}={ov}|{need}|r{rep:02d}",
                          "factor": factor, "x": x, "y": y, other: ov, "target_need": need,
                          "rep": rep, "run_x": rx, "run_y": ry})
    return sorted(pairs, key=lambda p: p["pair_id"])


def parse_json(text: str):
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    m = re.search(r"\{.*\}", cleaned, re.S)
    try:
        return json.loads(m.group() if m else cleaned)
    except (json.JSONDecodeError, AttributeError):
        return None


def judge_one(client, pair: dict, order: str, args, labels: dict) -> dict:
    """order 'xy' shows run_x as Set 1; 'yx' shows run_y as Set 1. Result is mapped back to x/y."""
    first, second = (pair["run_x"], pair["run_y"]) if order == "xy" else (pair["run_y"], pair["run_x"])
    rec = {k: pair[k] for k in pair if not k.startswith("run_")}
    rec.update(order=order, judge_model=args.judge_model, run_x=pair["run_x"]["run_id"],
               run_y=pair["run_y"]["run_id"], ts=datetime.now(timezone.utc).isoformat(),
               words_x=set_words(pair["run_x"].get("ideas")), words_y=set_words(pair["run_y"].get("ideas")))

    # a side with no parsed ideas loses automatically; no API call needed
    nx, ny = bool(pair["run_x"].get("ideas")), bool(pair["run_y"].get("ideas"))
    if not (nx and ny):
        rec.update(ok=True, winner="tie" if not (nx or ny) else ("x" if nx else "y"),
                   reason="one or both sides returned no parsed ideas", auto=True)
        return rec

    prompt = JUDGE_USER.format(product=args.product_name, need_id=pair["target_need"],
                               need_label=labels.get(pair["target_need"], ""),
                               operator=args.operator_name,
                               set1=render_ideas(first["ideas"]), set2=render_ideas(second["ideas"]))
    t0 = time.perf_counter()
    try:
        with client.messages.stream(model=args.judge_model, max_tokens=args.max_tokens, system=JUDGE_SYSTEM,
                                    messages=[{"role": "user", "content": prompt}],
                                    extra_body={"output_config": {"effort": args.judge_effort}}) as s:
            resp = s.get_final_message()
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        out = parse_json(text)
        if not out or out.get("winner") not in ("set_1", "set_2", "tie"):
            raise ValueError(f"unparseable judge output: {text[:200]}")
        to_xy = {"set_1": "x" if order == "xy" else "y", "set_2": "y" if order == "xy" else "x", "tie": "tie"}
        sx, sy = (out["set_1"], out["set_2"]) if order == "xy" else (out["set_2"], out["set_1"])
        rec.update(ok=True, auto=False, winner=to_xy[out["winner"]], reason=out.get("reason", ""),
                   scores_x={c: sx.get(c) for c in CRITERIA}, scores_y={c: sy.get(c) for c in CRITERIA},
                   input_tokens=resp.usage.input_tokens, output_tokens=resp.usage.output_tokens,
                   latency_s=round(time.perf_counter() - t0, 2))
    except Exception as exc:
        rec.update(ok=False, error=f"{type(exc).__name__}: {exc}")
    return rec


def cmd_judge(args) -> None:
    runs = load_runs(args.logs)
    if args.arms:
        x, y = args.arms
        pairs = build_arm_pairs(runs, x, y)
    else:
        factor, x, y = args.pair
        if factor not in ("condition", "effort"):
            sys.exit("--pair FACTOR must be 'condition' or 'effort'")
        pairs = build_pairs(runs, factor, x, y)
    if args.needs:
        pairs = [p for p in pairs if p["target_need"] in args.needs]
    if not pairs:
        sys.exit(f"No matched {x} / {y} pairs found in the logs.")
    g = yaml.safe_load(args.graph.read_text(encoding="utf-8"))
    labels = {n["id"]: n["label"] for n in g["nodes"] if n["type"] == "MarketNeed"}

    rng = random.Random(args.seed)
    orders = ["xy", "yx"] if args.both_orders else None
    jobs = []
    for p in pairs:
        for o in (orders or [rng.choice(["xy", "yx"])]):        # random position per pair, or both
            jobs.append((p, o))

    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / "judgments.jsonl"
    done = set()
    if out.exists():
        for line in out.open(encoding="utf-8"):
            try:
                r = json.loads(line)
                if r.get("ok") and r.get("judge_model") == args.judge_model:
                    done.add((r["pair_id"], r["order"] if args.both_orders else ""))
            except json.JSONDecodeError:
                pass
    todo = [(p, o) for p, o in jobs if (p["pair_id"], o if args.both_orders else "") not in done]
    print(f"{len(jobs)} judgments planned ({len(pairs)} pairs), {len(jobs) - len(todo)} done, "
          f"{len(todo)} to run with {args.judge_model} -> {out}")
    if not todo:
        return

    import anthropic
    client = anthropic.Anthropic(max_retries=5)
    lock = threading.Lock()
    with out.open("a", encoding="utf-8") as fh, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(judge_one, client, p, o, args, labels) for p, o in todo]
        for i, f in enumerate(as_completed(futs), 1):
            rec = f.result()
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
            msg = f"winner={rec['winner']}" if rec.get("ok") else rec["error"][:80]
            print(f"[{i}/{len(todo)}] {rec['pair_id']:<48} {msg}")


# ── SUMMARY ─────────────────────────────────────────────────────────
def sign_test_p(wins: int, losses: int) -> float:
    """Two-sided exact binomial test of wins vs losses (ties excluded)."""
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def wilson(p_hat: float, n: int, z: float = 1.96):
    if n == 0:
        return (None, None)
    d = 1 + z * z / n
    c = (p_hat + z * z / (2 * n)) / d
    h = z * math.sqrt(p_hat * (1 - p_hat) / n + z * z / (4 * n * n)) / d
    return round(c - h, 3), round(c + h, 3)


def collapse_pairs(js: list[dict]):
    """Merge the verdicts for each pair (one per presentation order) into one pair-level record.

    Each verdict counts x=1, tie=0.5, y=0; the pair's winner is the side whose average is above 0.5,
    so two agreeing verdicts give a win, and a split (x once, y once) gives a tie.
    Scores and lengths are averaged over the pair's verdicts.
    """
    by_pair = defaultdict(list)
    for j in js:
        by_pair[(j["pair_id"], j.get("judge_model"))].append(j)
    out = []
    for verdicts in by_pair.values():
        v = {"x": 1.0, "tie": 0.5, "y": 0.0}
        s = sum(v[j["winner"]] for j in verdicts) / len(verdicts)
        rec = {k: verdicts[0][k] for k in verdicts[0]
               if k not in ("winner", "scores_x", "scores_y", "order", "reason", "ts", "auto")}
        rec["winner"] = "x" if s > 0.5 else "y" if s < 0.5 else "tie"
        rec["n_orders"] = len(verdicts)
        rec["orders_agree"] = len({j["winner"] for j in verdicts}) == 1
        rec["auto"] = all(j.get("auto") for j in verdicts)
        scored = [j for j in verdicts if not j.get("auto") and j.get("scores_x") and j.get("scores_y")]
        for side in ("x", "y"):
            rec[f"scores_{side}"] = {c: (sum(j[f"scores_{side}"][c] for j in scored) / len(scored)
                                         if scored and all(isinstance(j[f"scores_{side}"].get(c), (int, float))
                                                           for j in scored) else None) for c in CRITERIA}
        out.append(rec)
    both = [r for r in out if r["n_orders"] == 2]
    return out, (sum(r["orders_agree"] for r in both) / len(both) if both else None)


def cmd_summary(args) -> None:
    path = RESULTS / "judgments.jsonl"
    if not path.exists():
        sys.exit("No results/judgments.jsonl yet; run the judge step first.")
    js = [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]
    js = [j for j in js if j.get("ok")]

    # judgments made before length was logged: recover it from the run logs, if given
    if args.logs:
        runs = load_runs(args.logs)
        for j in js:
            for side in ("x", "y"):
                if f"words_{side}" not in j and j[f"run_{side}"] in runs:
                    j[f"words_{side}"] = set_words(runs[j[f"run_{side}"]].get("ideas"))

    # one record per PAIR: with --both-orders each pair is judged twice, and the two verdicts are not
    # independent, so testing them as separate observations would overstate certainty
    js, consistency = collapse_pairs(js)

    groups = defaultdict(list)
    for j in js:
        other = {"condition": "effort", "effort": "condition"}.get(j["factor"], "matched_on")
        groups[(j["factor"], j["x"], j["y"], other, j.get(other, "need+rep"))].append(j)

    rows = []
    for (factor, x, y, other, ov), items in sorted(groups.items(), key=lambda kv: [str(v) for v in kv[0]]):
        for need in sorted({i["target_need"] for i in items}) + ["ALL"]:
            sel = [i for i in items if need == "ALL" or i["target_need"] == need]
            w = sum(i["winner"] == "x" for i in sel)
            l = sum(i["winner"] == "y" for i in sel)
            t = sum(i["winner"] == "tie" for i in sel)
            n = len(sel)
            rate = (w + 0.5 * t) / n if n else 0          # ties count as half a win
            lo, hi = wilson(rate, n)
            both = [i for i in sel if i["n_orders"] == 2]
            row = {"comparison": f"{factor}: {x} vs {y}", other: ov, "target_need": need, "n_pairs": n,
                   f"{x}_wins": w, f"{y}_wins": l, "ties": t, f"{x}_win_rate": round(rate, 3),
                   "ci95_low": lo, "ci95_high": hi, "sign_test_p": round(sign_test_p(w, l), 4),
                   "orders_agree": round(sum(i["orders_agree"] for i in both) / len(both), 3) if both else "",
                   "auto_decided": sum(bool(i.get("auto")) for i in sel)}
            for c in CRITERIA:
                diffs = [i["scores_x"][c] - i["scores_y"][c] for i in sel
                         if not i.get("auto") and isinstance(i["scores_x"].get(c), (int, float))
                         and isinstance(i["scores_y"].get(c), (int, float))]
                row[f"{c}_diff_{x}_minus_{y}"] = mean(diffs)
            # detail-bias check: words each side showed the judge, and how often the longer set won
            have = [i for i in sel if isinstance(i.get("words_x"), int) and isinstance(i.get("words_y"), int)]
            row[f"{x}_words"] = mean(i["words_x"] for i in have)
            row[f"{y}_words"] = mean(i["words_y"] for i in have)
            decided = [i for i in have if not i.get("auto") and i["winner"] != "tie" and i["words_x"] != i["words_y"]]
            row["longer_set_won"] = (round(sum((i["words_x"] > i["words_y"]) == (i["winner"] == "x")
                                               for i in decided) / len(decided), 3) if decided else "")
            rows.append(row)
    write_csv(RESULTS / "pairwise_summary.csv", rows)
    for comp in dict.fromkeys(r["comparison"] for r in rows):
        sub = [r for r in rows if r["comparison"] == comp]
        print(f"\n{comp}")
        print_table(sub, [k for k in sub[0] if k != "comparison"])
    if consistency is not None:
        print(f"\nOrder consistency: the judge gave the same verdict in both presentation orders "
              f"for {consistency:.0%} of pairs judged twice.")
    print("Counts and tests are per pair (both orders combined), not per verdict.")
    print("\n-> results/pairwise_summary.csv")


# ── Helpers ─────────────────────────────────────────────────────────
def write_csv(path: Path, rows: list[dict]) -> None:
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def print_table(rows: list[dict], cols: list[str]) -> None:
    fmt = lambda v: f"{v:.3f}" if isinstance(v, float) else str(v)
    widths = [max(len(c), *(len(fmt(r.get(c, ""))) for r in rows)) for c in cols]
    print("  ".join(c.ljust(w) for c, w in zip(cols, widths)))
    for r in rows:
        print("  ".join(fmt(r.get(c, "")).ljust(w) for c, w in zip(cols, widths)))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("stats", help="cost, validity and structure tables")
    s.add_argument("--logs", nargs="+", type=Path, default=[Path("runs/rq1_runs.jsonl")])
    s.add_argument("--graph", type=Path, default=Path("microwave_base_graph.yaml"))
    s.add_argument("--manifest", type=Path, default=Path("slices/manifest.csv"))
    s.add_argument("--price-in", type=float, help="USD per million input tokens (current price)")
    s.add_argument("--price-out", type=float, help="USD per million output tokens (current price)")

    j = sub.add_parser("judge", help="blind pairwise quality judging (API calls)")
    j.add_argument("--logs", nargs="+", type=Path, default=[Path("runs/rq1_runs.jsonl")])
    j.add_argument("--graph", type=Path, default=Path("microwave_base_graph.yaml"))
    j.add_argument("--pair", nargs=3, metavar=("FACTOR", "X", "Y"), default=["condition", "A", "B"],
                   help="compare two levels of one factor, the other factor matched")
    j.add_argument("--arms", nargs=2, metavar=("COND:EFFORT", "COND:EFFORT"),
                   help="compare two arms differing in both factors, e.g. A:low B:high (overrides --pair)")
    j.add_argument("--needs", nargs="*", help="limit to these target needs")
    j.add_argument("--judge-model", default="claude-sonnet-5-5")
    j.add_argument("--judge-effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    j.add_argument("--max-tokens", type=int, default=16000)
    j.add_argument("--both-orders", action="store_true", help="judge each pair twice, sets swapped")
    j.add_argument("--product-name", default="microwave")
    j.add_argument("--operator-name", default="SUBSTITUTE (replace parts with something cheaper or simpler "
                                              "that fulfils the same function equally well or better)")
    j.add_argument("--workers", type=int, default=4)
    j.add_argument("--seed", type=int, default=7)

    m = sub.add_parser("summary", help="win rates and sign tests from the judgments")
    m.add_argument("--logs", nargs="*", type=Path, default=[],
                   help="run logs, to add idea length to judgments made before it was logged")

    args = ap.parse_args()
    {"stats": cmd_stats, "judge": cmd_judge, "summary": cmd_summary}[args.cmd](args)


if __name__ == "__main__":
    main()
