#!/usr/bin/env python3
"""
smoke_check.py: did a model's test call deliver what the 50-idea study needs? No API calls.

  GEN_MODEL=qwen bash run_all.sh smoke         # one full-graph call -> runs/smoke_qwen.jsonl, then this check
  python smoke_check.py runs/smoke_qwen.jsonl --host alibaba

Pass (exit 0) only if the latest call in the log:
  - succeeded and its answer parsed as JSON (the prompt's {"ideas": [...]} format)
  - was not cut off at max_tokens
  - returned at least --min-ideas ideas (the Haiku run returned 44-60 when asked for 50)
  - gave every idea a title, new_nodes and a rationale (what the judge and the coder read)
  - was served by the pinned host (--host), when one is given
Prints tokens, reasoning tokens, latency and cost, and the projected cost of the 40-call run.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FULL_RUN_CALLS = 40


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", type=Path)
    ap.add_argument("--host", default=None, help="the OpenRouter endpoint tag the call should have been pinned to")
    ap.add_argument("--min-ideas", type=int, default=44)
    args = ap.parse_args()

    if not args.log.exists():
        sys.exit(f"{args.log} not found")
    recs = [json.loads(l) for l in args.log.open(encoding="utf-8") if l.strip()]
    if not recs:
        sys.exit(f"{args.log} is empty")
    r = recs[-1]
    print(f"{r.get('model')} · {r.get('run_id')} · served by {r.get('served_by') or '-'} "
          f"({r.get('model_version') or '-'})")
    if not r.get("ok"):
        sys.exit(f"FAIL: call failed: {r.get('error')}")

    ideas = r.get("ideas") or []
    complete = [i for i in ideas if isinstance(i, dict) and str(i.get("title") or "").strip()
                and i.get("new_nodes") and str(i.get("rationale") or "").strip()]
    words = [len(" ".join([str(i.get("title", "")), str(i.get("rationale", ""))]).split()) for i in complete]
    checks = [
        ("answer parsed as JSON", bool(r.get("parse_ok"))),
        (f"not cut off (stop: {r.get('stop_reason')})", r.get("stop_reason") != "max_tokens"),
        (f"{len(ideas)} ideas (need >= {args.min_ideas})", len(ideas) >= args.min_ideas),
        (f"{len(complete)}/{len(ideas)} ideas complete (title, new_nodes, rationale)",
         bool(ideas) and len(complete) == len(ideas)),
    ]
    if args.host:
        served = str(r.get("served_by") or "")
        host_name = args.host.split("/")[0].replace("-", "").lower()
        checks.append((f"served by the pinned host {args.host}", host_name in served.replace(".", "").replace("-", "").lower()))
    for name, ok in checks:
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")

    tin, tout, reas = r.get("input_tokens") or 0, r.get("output_tokens") or 0, r.get("reasoning_tokens") or 0
    cost = r.get("cost_usd_billed")
    print(f"  tokens: {tin:,} in, {tout:,} out ({reas:,} reasoning), {r.get('latency_s', 0):.0f} s"
          + (f", ${cost:.4f} billed" if cost is not None else ""))
    if words:
        print(f"  idea length: {sum(words) / len(words):.0f} words (title + rationale) on average")
    if cost is not None:
        print(f"  40-call run, if every call costs this (the full graph is the longest prompt): about "
              f"${cost * FULL_RUN_CALLS:.2f} for generation")
    if all(ok for _, ok in checks):
        print("PASS: run the 40 calls with `generate`.")
    else:
        sys.exit("FAIL: fix the cause (e.g. raise --max-tokens in run_all.sh), or choose another model.")


if __name__ == "__main__":
    main()
