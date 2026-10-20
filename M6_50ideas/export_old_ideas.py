#!/usr/bin/env python3
"""
export_old_ideas.py: the main study's M6 ideas, blind, as the material for the codebook.

  cd M6_50ideas
  python export_old_ideas.py          # reads ../runs/rq1_full.jsonl (never changes it)

Writes
  codebook/old_M6_ideas.csv   key, title, new elements, rationale: shuffled, node ids removed,
                              nothing about condition or effort. Build the codebook from this file.
  codebook/old_M6_key.csv     key -> idea_id, condition, effort. Do not open it while building the
                              codebook; it is only for describing afterwards where moves came from.

The main study has 50 M6 calls (A and B at four efforts, R and C at high), so about 250 ideas.
None of this study's new calls are used here: the codebook is fixed before it meets the new data.
"""
from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

from common import CODEBOOK_DIR, NEED, ROOT, idea_records, load_calls


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--logs", nargs="+", type=Path, default=[ROOT / "runs" / "rq1_full.jsonl"])
    ap.add_argument("--seed", type=int, default=6)
    args = ap.parse_args()

    ideas = [i for i in idea_records(load_calls(args.logs), NEED)]
    random.Random(args.seed).shuffle(ideas)
    for n, it in enumerate(ideas, 1):
        it["key"] = f"O{n:03d}"

    CODEBOOK_DIR.mkdir(exist_ok=True)
    with (CODEBOOK_DIR / "old_M6_ideas.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["key", "title", "new_elements", "rationale"])
        w.writerows([it["key"], it["title"], it["elements"], it["rationale"]] for it in ideas)
    with (CODEBOOK_DIR / "old_M6_key.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["key", "idea_id", "condition", "effort"])
        w.writerows([it["key"], it["idea_id"], it["condition"], it["effort"]] for it in ideas)
    n_calls = len({it["run_id"] for it in ideas})
    print(f"{len(ideas)} {NEED} ideas from {n_calls} main-study calls -> {CODEBOOK_DIR / 'old_M6_ideas.csv'}")
    print(f"hidden key -> {CODEBOOK_DIR / 'old_M6_key.csv'} (do not open while building the codebook)")


if __name__ == "__main__":
    main()
