#!/usr/bin/env bash
# persona_as_factor: every step, in order. Run from inside this folder:
#   cd persona_as_factor && bash run_all.sh          (or copy the lines one at a time)
# Each step is resumable: re-running it skips calls that are already logged.
set -euo pipefail

ROOT=..
GEN=(--graph $ROOT/microwave_base_graph.yaml --manifest $ROOT/slices/manifest.csv
     --template $ROOT/template_prompt.txt --personas-file personas.yaml
     --persona engineer lateral patent --conditions B C --needs M8 M13 M4
     --effort medium high --reps 15 --max-tokens 48000 --out runs/persona_runs.jsonl)

# 1. reuse the main study's 45 engineer calls (and their quality scores); reads, never changes, ../runs
python seed_from_main.py --logs $ROOT/runs/rq1_full.jsonl --scores $ROOT/results/idea_scores.jsonl

# 2. check the plan: 540 calls planned, 45 already logged, 495 to run; prompts written to runs/dry_run/
python $ROOT/KG_informed_brainstorm_AB_Test.py "${GEN[@]}" --dry-run

# 3. generate (about 495 calls)
python $ROOT/KG_informed_brainstorm_AB_Test.py "${GEN[@]}"

# 4. score: quality (same prompt as the main study; seeded calls are already scored) and patentability
python $ROOT/top_ideas.py score --logs runs/persona_runs.jsonl --graph $ROOT/microwave_base_graph.yaml
python $ROOT/top_ideas.py score --rubric patent --logs runs/persona_runs.jsonl --graph $ROOT/microwave_base_graph.yaml

# 5. tables and charts
python $ROOT/analyze.py stats --logs runs/persona_runs.jsonl --graph $ROOT/microwave_base_graph.yaml --manifest $ROOT/slices/manifest.csv
python $ROOT/top_ideas.py report --logs runs/persona_runs.jsonl --graph $ROOT/microwave_base_graph.yaml --n 10
python persona_analysis.py
