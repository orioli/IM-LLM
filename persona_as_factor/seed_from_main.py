#!/usr/bin/env python3
"""
seed_from_main.py: copy the main study's innovation-engineer calls that this study reuses.

  cd persona_as_factor
  python seed_from_main.py                                  # defaults: ../runs/rq1_full.jsonl, ../results/idea_scores.jsonl

The engineer's prompts are byte-identical in both studies, so its existing calls for these cells are
reused instead of being paid for again: conditions B and C, needs M4, M8 and M13, medium and high effort
(45 calls in the main study: 5 per cell, no C at medium). The runner then tops each cell up to 15.

Copies, never moves: the main study's files are only read. Each copied call gets "persona": "engineer"
and "seeded_from" (the source file). Their quality scores are copied too, so they are not scored twice.
Safe to run again: run ids already present here are skipped.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

CONDITIONS = {"B", "C"}
NEEDS = {"M4", "M8", "M13"}
EFFORTS = {"medium", "high"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--logs", nargs="+", type=Path, default=[Path("../runs/rq1_full.jsonl")],
                    help="main-study run logs (later files win, as in analyze.py)")
    ap.add_argument("--scores", type=Path, default=Path("../results/idea_scores.jsonl"),
                    help="main-study quality scores (top_ideas.py score)")
    ap.add_argument("--out", type=Path, default=Path("runs/persona_runs.jsonl"))
    ap.add_argument("--out-scores", type=Path, default=Path("results/idea_scores.jsonl"))
    args = ap.parse_args()

    picked = {}
    for path in args.logs:
        for line in path.open(encoding="utf-8"):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if (r.get("ok") and r.get("condition") in CONDITIONS and r.get("target_need") in NEEDS
                    and r.get("effort") in EFFORTS and r.get("persona", "engineer") == "engineer"):
                picked[r["run_id"]] = {**r, "persona": "engineer", "seeded_from": str(path)}

    args.out.parent.mkdir(parents=True, exist_ok=True)
    have = set()
    if args.out.exists():
        have = {json.loads(l)["run_id"] for l in args.out.open(encoding="utf-8") if l.strip()}
    new = [r for rid, r in sorted(picked.items()) if rid not in have]
    with args.out.open("a", encoding="utf-8") as fh:
        for r in new:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    cells = {}
    for r in picked.values():
        k = (r["condition"], r["target_need"], r["effort"])
        cells[k] = cells.get(k, 0) + 1
    print(f"{len(picked)} engineer calls found, {len(new)} copied -> {args.out}")
    for k in sorted(cells):
        print(f"  {k[0]} {k[1]:<4} {k[2]:<6} {cells[k]} calls")

    if args.scores.exists():
        args.out_scores.parent.mkdir(parents=True, exist_ok=True)
        have_s = set()
        if args.out_scores.exists():
            have_s = {json.loads(l)["run_id"] for l in args.out_scores.open(encoding="utf-8") if l.strip()}
        scores = {}
        for line in args.scores.open(encoding="utf-8"):
            s = json.loads(line)
            if s.get("ok") and s["run_id"] in picked:
                scores[s["run_id"]] = s                    # later lines win
        with args.out_scores.open("a", encoding="utf-8") as fh:
            for rid in sorted(scores):
                if rid not in have_s:
                    fh.write(json.dumps({**scores[rid], "seeded_from": str(args.scores)}, ensure_ascii=False) + "\n")
        print(f"{len(scores)} quality scores found, {len([r for r in scores if r not in have_s])} copied -> {args.out_scores}")
    else:
        print(f"(no {args.scores}: the seeded calls will be scored again by top_ideas.py score)")


if __name__ == "__main__":
    main()
