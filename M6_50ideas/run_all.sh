#!/usr/bin/env bash
# M6_50ideas: every step, one at a time, run from anywhere:   bash M6_50ideas/run_all.sh <step>
# Steps marked (hand) are done by a person; the script only prints what to do.
# Every API step is resumable: re-running it skips work already logged.
set -euo pipefail
SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
cd "$(dirname "$SELF")"
ROOT=..
# 50 ideas per call, 10 calls per condition (2,000 ideas). The persona file holds the main study's
# engineer sentence verbatim; its name only prefixes the run ids (engineer50_A_M6_medium_r01).
GEN=(--graph $ROOT/microwave_base_graph.yaml --manifest $ROOT/slices/manifest.csv
     --template $ROOT/template_prompt.txt --needs M6 --conditions A B R C --effort medium
     --n-ideas 50 --reps 10 --persona engineer50 --personas-file personas_50ideas.yaml
     --r-seed 1 --max-tokens 48000 --order-seed 6 --out runs/m6_50ideas.jsonl)

case "${1:-help}" in
  # ── before any generation call ─────────────────────────────────────
  prompts)    # 40 calls planned; prompts checked: the main study's, except "5 ideas" -> "50 ideas"
    python $ROOT/KG_informed_brainstorm_AB_Test.py "${GEN[@]}" --dry-run
    python check_prompts.py ;;
  export)     # the main study's 250 M6 ideas (5-idea calls), blind -> codebook/old_M6_ideas.csv
    python export_old_ideas.py ;;
  draft)      # (optional) one model call drafts moves -> codebook/codebook_draft.yaml
    python draft_codebook.py --dry-run
    python draft_codebook.py ;;
  codebook)   # (hand)
    echo "Edit codebook/codebook_draft.yaml (or codebook_template.yaml) into codebook/codebook.yaml:"
    echo "  merge/split moves, check definitions and categories, then set status: final and version: 1." ;;
  # ── generation and scoring ─────────────────────────────────────────
  generate)   # 40 calls of 50 ideas (about 1M tokens; each call takes a few minutes)
    python $ROOT/KG_informed_brainstorm_AB_Test.py "${GEN[@]}" ;;
  score)      # quality scores with the main study's judge prompt, 5 ideas per request; cost tables
    python score_ideas.py score
    python score_ideas.py table
    python $ROOT/analyze.py stats --logs runs/m6_50ideas.jsonl --graph $ROOT/microwave_base_graph.yaml \
           --manifest $ROOT/slices/manifest.csv ;;
  # ── coding into moves ──────────────────────────────────────────────
  code)       # the new ideas, and the main study's M6 ideas (the 5-idea reference) -> results/moves.jsonl
    python code_moves.py code --dry-run
    python code_moves.py code
    python code_moves.py code --logs $ROOT/runs/rq1_full.jsonl ;;
  review)     # ideas coded NEW -> results/new_move_proposals.csv; then (hand) add real moves, bump version, `code`
    python code_moves.py review ;;
  recode)     # last coding pass: everything with the final codebook version
    python code_moves.py code --all
    python code_moves.py code --all --logs $ROOT/runs/rq1_full.jsonl
    python code_moves.py review ;;
  sample)     # 100 new ideas (25 per condition), blind -> results/human_coding_sheet.csv
    python code_moves.py sample ;;
  agree)      # after (hand) coding the sheet: kappa >= 0.6 required
    python code_moves.py agree ;;
  priorart)   # (hand)
    echo "For every move in codebook/codebook.yaml, search patents and products; fill prior_art and prior_art_ref."
    echo "Do it from the codebook alone, before running the analysis (the codebook does not show which arm found a move)." ;;
  # ── analysis ───────────────────────────────────────────────────────
  analyze)
    python discovery_analysis.py ;;
  help|*)
    grep -E '^  [a-z|]+\)' "$SELF" | sed 's/)//' ;;
esac
