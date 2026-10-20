#!/usr/bin/env python3
"""
score_ideas.py: blind quality scores for every idea, with the main study's judge prompt, 5 ideas per request.

  cd M6_50ideas
  python score_ideas.py score      # API calls, resumable  -> results/idea_scores.jsonl
  python score_ideas.py table      # no API calls          -> results/ideas_scored.csv

In the main study the judge rated each call's 5 ideas in one request. Here a call has 50 ideas, so
they are sent as ten requests of 5 consecutive ideas (positions 1-5, 6-10, ...): every request looks
exactly like a main-study request. The prompt and the four criteria (relevance, novelty,
feasibility, specificity; score = their mean) are imported unchanged from ../top_ideas.py.
The judge sees each idea's title, new elements and rationale only: no condition, position or graph.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from common import NEED, RESULTS, ROOT, RUNS, call_claude, load_calls, need_label, parse_json

sys.path.insert(0, str(ROOT))
from top_ideas import IDEA_CRITERIA, JUDGE_SYSTEM, JUDGE_USER, render_for_judge  # noqa: E402

SCORES = RESULTS / "idea_scores.jsonl"
TABLE = RESULTS / "ideas_scored.csv"
OPERATOR = ("SUBSTITUTE (replace parts with something cheaper or simpler "
            "that fulfils the same function equally well or better)")      # ../top_ideas.py's default, verbatim
CHUNK = 5


def chunks(calls: dict) -> list[dict]:
    out = []
    for run_id, c in calls.items():
        ideas = c.get("ideas") or []
        for start in range(0, len(ideas), CHUNK):
            out.append({"run_id": run_id, "start": start + 1, "ideas": ideas[start:start + CHUNK]})
    return out


def done_keys() -> set:
    keys = set()
    if SCORES.exists():
        for line in SCORES.open(encoding="utf-8"):
            r = json.loads(line)
            if r.get("ok"):
                keys.add((r["run_id"], r["start"]))
    return keys


def score_chunk(ch: dict, args) -> dict:
    prompt = JUDGE_USER.format(product="microwave", need_id=NEED, need_label=need_label(), operator=OPERATOR,
                               ideas=render_for_judge(ch["ideas"]))
    rec = {"run_id": ch["run_id"], "start": ch["start"], "n": len(ch["ideas"]), "judge_model": args.model,
           "ts": datetime.now(timezone.utc).isoformat()}
    try:
        text, usage = call_claude(JUDGE_SYSTEM, prompt, args.model, args.effort, args.max_tokens)
        out = parse_json(text)
        ratings = out.get("ratings") if isinstance(out, dict) else None
        if not isinstance(ratings, list) or len(ratings) != len(ch["ideas"]):
            raise ValueError(f"expected {len(ch['ideas'])} ratings, got: {text[:200]}")
        rec.update(ok=True, ratings=ratings, **usage)
    except Exception as exc:
        rec.update(ok=False, error=f"{type(exc).__name__}: {exc}")
    return rec


def cmd_score(args) -> None:
    calls = load_calls(args.logs)
    todo = [c for c in chunks(calls) if (c["run_id"], c["start"]) not in done_keys()]
    print(f"{len(calls)} calls; {len(todo)} requests of up to {CHUNK} ideas to score with {args.model}")
    if not todo:
        return
    RESULTS.mkdir(exist_ok=True)
    lock = threading.Lock()
    with SCORES.open("a", encoding="utf-8") as fh, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(score_chunk, c, args) for c in todo]
        for i, f in enumerate(as_completed(futs), 1):
            rec = f.result()
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
            print(f"[{i}/{len(todo)}] {rec['run_id']} ideas {rec['start']}-{rec['start'] + rec['n'] - 1}: "
                  f"{'ok' if rec.get('ok') else rec['error'][:70]}")
    print("re-run the same command to retry any failures; then `table`")


def cmd_table(args) -> None:
    calls = load_calls(args.logs)
    got = {}
    if SCORES.exists():
        for line in SCORES.open(encoding="utf-8"):
            r = json.loads(line)
            if r.get("ok"):
                got[(r["run_id"], r["start"])] = r["ratings"]          # later lines win
    rows = []
    for run_id, c in calls.items():
        for k, idea in enumerate(c.get("ideas") or [], 1):
            start = (k - 1) // CHUNK * CHUNK + 1
            ratings = got.get((run_id, start))
            if not ratings or len(ratings) < k - start + 1 or not isinstance(ratings[k - start], dict):
                continue
            rt = ratings[k - start]
            vals = [rt.get(x) for x in IDEA_CRITERIA if isinstance(rt.get(x), (int, float))]
            if not vals:
                continue
            rows.append({"idea_id": f"{run_id}#{k}", "run_id": run_id, "condition": c["condition"], "position": k,
                         "score": round(sum(vals) / len(vals), 2), **{x: rt.get(x) for x in IDEA_CRITERIA},
                         "title": idea.get("title", "")})
    n_ideas = sum(len(c.get("ideas") or []) for c in calls.values())
    RESULTS.mkdir(exist_ok=True)
    with TABLE.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["idea_id", "run_id", "condition", "position", "score", *IDEA_CRITERIA,
                                           "title"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} of {n_ideas} ideas scored -> {TABLE}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("score", "table"):
        p = sub.add_parser(name)
        p.add_argument("--logs", nargs="+", default=[RUNS])
    s = sub.choices["score"]
    s.add_argument("--model", default="claude-sonnet-5-5")
    s.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    s.add_argument("--max-tokens", type=int, default=16000)
    s.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    {"score": cmd_score, "table": cmd_table}[args.cmd](args)


if __name__ == "__main__":
    main()
