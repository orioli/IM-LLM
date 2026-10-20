#!/usr/bin/env python3
"""
draft_codebook.py: (optional) let the model propose a first codebook of moves from the old M6 ideas.

  cd M6_50ideas
  python draft_codebook.py --dry-run     # writes the prompt to codebook/draft_prompt.txt, no API call
  python draft_codebook.py               # one call -> codebook/codebook_draft.yaml + draft_assignments.csv

The draft is a starting point, not the codebook. Edit it by hand into codebook/codebook.yaml:
merge, split or rename moves, check every definition and category, then set `status: final` and
`version: 1`. Keep codebook_draft.yaml unchanged, so the edits can be reported.

Input: codebook/old_M6_ideas.csv (from export_old_ideas.py): blind, shuffled, node ids removed.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime, timezone

import yaml

from common import (CATEGORIES, CODEBOOK_DIR, CODER_MODEL, NEED, call_claude, fill, load_prompt, need_label,
                    parse_json, render_ideas)


def read_old_ideas() -> list[dict]:
    path = CODEBOOK_DIR / "old_M6_ideas.csv"
    if not path.exists():
        sys.exit(f"{path} not found; run export_old_ideas.py first")
    with path.open(encoding="utf-8") as fh:
        return [{"key": r["key"], "title": r["title"], "elements": r["new_elements"], "rationale": r["rationale"]}
                for r in csv.DictReader(fh)]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=CODER_MODEL)
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--max-tokens", type=int, default=48000)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ideas = read_old_ideas()
    system_t, user_t = load_prompt("draft_codebook.txt")
    user = fill(user_t, {"need_id": NEED, "need_label": need_label(), "n": len(ideas),
                         "ideas": render_ideas(ideas, key="key")})
    if args.dry_run:
        out = CODEBOOK_DIR / "draft_prompt.txt"
        out.write_text(f"=== SYSTEM ===\n{system_t}\n\n=== USER ===\n{user}\n", encoding="utf-8")
        print(f"{len(ideas)} ideas; prompt (~{round(len(system_t + user) / 3.5):,} tokens) -> {out}")
        return

    out_draft, out_assign = CODEBOOK_DIR / "codebook_draft.yaml", CODEBOOK_DIR / "draft_assignments.csv"
    if out_draft.exists():
        sys.exit(f"{out_draft} exists; delete it first if you really want a new draft")
    text, usage = call_claude(system_t, user, args.model, args.effort, args.max_tokens)
    (CODEBOOK_DIR / "draft_response.txt").write_text(text, encoding="utf-8")   # raw, for the record
    data = parse_json(text)
    if not isinstance(data, dict) or not isinstance(data.get("moves"), list):
        sys.exit(f"could not parse the response (saved to codebook/draft_response.txt); usage {usage}")

    moves = []
    for m in data["moves"]:
        cat = m.get("category") if m.get("category") in CATEGORIES else f"CHECK: {m.get('category')}"
        moves.append({"id": str(m.get("id")), "label": m.get("label", ""), "replaces": m.get("replaces", ""),
                      "by": m.get("by", ""), "definition": m.get("definition", ""), "category": cat,
                      "worked_example_echo": bool(m.get("worked_example_echo")), "source": "old_ideas",
                      "prior_art": "unchecked", "prior_art_ref": "", "examples": list(m.get("examples") or [])})
    keys = {i["key"]: i for i in ideas}
    assigned = {a.get("key"): a.get("move") for a in (data.get("assignments") or []) if isinstance(a, dict)}
    counts = Counter(assigned.values())

    doc = {"status": "draft", "version": 0, "need": NEED,
           "built_from": f"codebook/old_M6_ideas.csv ({len(ideas)} main-study ideas, blind)",
           "drafted_by": f"{args.model} (effort {args.effort}), {datetime.now(timezone.utc).date()}",
           "edited_by": "", "moves": moves}
    with out_draft.open("w", encoding="utf-8") as fh:
        fh.write("# DRAFT by the model. Edit into codebook/codebook.yaml, then set status: final, version: 1.\n")
        yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=True, width=110)
    with out_assign.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["key", "move", "move_label", "title"])
        labels = {m["id"]: m["label"] for m in moves}
        for k, it in keys.items():
            mv = assigned.get(k, "")
            w.writerow([k, mv, labels.get(mv, ""), it["title"]])

    missing = [k for k in keys if k not in assigned]
    unknown = sorted({v for v in assigned.values() if v not in labels})
    print(f"{len(moves)} moves drafted -> {out_draft}; assignments -> {out_assign}")
    print(f"  ideas per move: {', '.join(f'{m}:{n}' for m, n in counts.most_common())}")
    if missing:
        print(f"  {len(missing)} ideas not assigned (left blank in the CSV)")
    if unknown:
        print(f"  assignments to unknown move ids: {unknown}")
    print(f"  usage: {usage}")


if __name__ == "__main__":
    main()
