#!/usr/bin/env python3
"""
check_prompts.py: do this study's prompts differ from the main study's ONLY in the number of ideas?

  cd M6_50ideas
  bash run_all.sh prompts        # dry run (writes runs/dry_run/engineer50_<cond>_M6.txt), then this check

For each condition, the dry-run prompt is rebuilt exactly as the runner hashes it (system + blank line +
user), the single line "Return exactly 50 ideas as JSON:" is put back to the main study's "5 ideas",
and the result must hash to the prompt_sha256 logged for the same condition and need in
../runs/rq1_full.jsonl. Exits 1 if anything else differs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from common import CONDITIONS, HERE, N_IDEAS, NEED, PERSONA, REF_LOGS

HEAD, SEP = "=== SYSTEM ===\n", "\n\n=== USER ===\n"
MAIN_IDEAS = 5


def read_dry_run(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith(HEAD) or SEP not in text:
        sys.exit(f"{path}: not a dry-run prompt file")
    system, user = text[len(HEAD):].split(SEP, 1)
    return system, (user[:-1] if user.endswith("\n") else user)     # the runner adds one newline at the end


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run-dir", type=Path, default=HERE / "runs" / "dry_run")
    ap.add_argument("--main-logs", nargs="+", type=Path, default=REF_LOGS)
    args = ap.parse_args()

    ref = {}
    for p in args.main_logs:
        for line in p.open(encoding="utf-8"):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("target_need") == NEED and r.get("prompt_sha256") and r.get("persona", "engineer") == "engineer":
                ref.setdefault(r["condition"], set()).add(r["prompt_sha256"])

    ours, theirs = f"Return exactly {N_IDEAS} ideas as JSON:", f"Return exactly {MAIN_IDEAS} ideas as JSON:"
    bad = 0
    print(f"{'cond':<5} {'asks for':<9} {'other differences from the main study':<40}")
    for cond in CONDITIONS:
        f = args.dry_run_dir / f"{PERSONA}_{cond}_{NEED}.txt"
        if not f.exists():
            print(f"{cond:<5} {'-':<9} missing: run the dry run first ({f.name})")
            bad += 1
            continue
        system, user = read_dry_run(f)
        n = user.count(ours)
        if n != 1:
            print(f"{cond:<5} {'?':<9} expected the line '{ours}' once, found it {n} times")
            bad += 1
            continue
        back = system + "\n\n" + user.replace(ours, theirs)
        ok = hashlib.sha256(back.encode("utf-8")).hexdigest() in ref.get(cond, set())
        bad += not ok
        print(f"{cond:<5} {N_IDEAS:<9} {'none (identical apart from the number of ideas)' if ok else 'DIFFERENT'}")
    if bad:
        sys.exit(f"{bad} condition(s) differ from the main study in more than the number of ideas: do not run.")
    print(f"All four prompts are the main study's, word for word, except '{MAIN_IDEAS} ideas' -> '{N_IDEAS} ideas'.")


if __name__ == "__main__":
    main()
