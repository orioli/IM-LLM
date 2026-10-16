# Persona as a factor

A follow-up to the main RQ1 experiment. The main study found that a relevant slice of the product graph (B) gives the most top ideas per token, with no graph (C) close behind, and the full graph (A) far behind. All of it used one persona, an innovation engineer. This study asks whether that ranking depends on **who is thinking**.

Everything here is kept apart from the main study: its own run log, scores, tables and charts. The main study's files are only read, never changed.

## Question and hypotheses

**RQ.** Does the most efficient representation of the product (need slice vs no graph) depend on the persona the model is asked to adopt?

These hypotheses were written down before any persona call was run (2026-10-16).

- **H5 (lateral thinker prefers less structure).** The lateral thinker's yield ratio of need slice to no graph (B ÷ C, top ideas per 100k tokens) is lower than the innovation engineer's. Reframing works by leaving the product's structure, so the graph should help this persona less.
- **H6 (patent persona prefers more structure).** The patent-focused persona's B ÷ C ratio for *patentable* ideas is higher than the engineer's. Claimable inventions need specific components and mechanisms, which the slice supplies.
- **H7 (personas do what they are told).** The patent-focused persona produces a higher mean patentability than the engineer, and the lateral thinker a higher mean novelty.

**Primary measure:** yield, top ideas (quality score ≥ 4.0, the main study's threshold) per 100k tokens, pooled over the three needs and both efforts, with 95% CIs from resampling calls within need. **Secondary:** patentable yield (patentability ≥ 4), mean novelty, mean patentability; per-effort and per-need results are descriptive. A difference between personas is claimed only if the B ÷ C intervals do not overlap.

## Design

| Factor | Levels |
| --- | --- |
| Persona | `engineer` (main study's wording, verbatim), `lateral`, `patent` (`personas.yaml`) |
| Representation | B (need slice), C (no graph): the same slice files as the main study (`../slices/`) |
| Target need | M8 (small slice, 25 nodes; the branch of the prompt's worked example), M13 (45 nodes), M4 (51 nodes) |
| Effort | medium, high |
| Calls per cell | 15 |

36 cells × 15 = **540 calls**. Everything else (model `claude-haiku-5-5`, operator SUBSTITUTE, worked example, output format, 5 ideas per call, `max_tokens` 48,000) is as in the main study.

**Personas** describe a way of thinking and replace only the first sentence of the system prompt. None asks the model to *be* a real person. Each new persona ends with one short exemplar of its way of thinking, credited to its author: Rory Sutherland's Eurostar observation (make the journey more enjoyable, e.g. with Wi-Fi, rather than the train faster) for the lateral thinker, and James Dyson's bagless cyclone vacuum (a patented substitution of the dust bag) for the patent-focused persona. Both new personas get exactly one exemplar, so they differ from each other in the way of thinking, not in whether they had an example. The engineer's sentence is the main study's, with no exemplar, so its prompts are byte-identical to the main study's (checked for all 52 condition × need prompts).

**Exemplar echo.** An exemplar can be copied (a microwave "with Wi-Fi" is a literal echo of the Eurostar case). `persona_analysis.py` reports, for every cell, the share of ideas mentioning either exemplar (Wi-Fi, Eurostar, entertainment; cyclone, bagless, Dyson), with the engineer, who sees neither, as the baseline. A persona effect that is mostly echo is reported as such.

**Reused calls.** The main study already has 45 engineer calls in these cells (5 each for B and C at high, B at medium; C at medium was not run). `seed_from_main.py` copies them, with their quality scores, into this folder; the runner then tops every engineer cell up to 15. The top-up calls are made later than the originals with the same model and prompt; they are pooled with them.

**New calls:** 495 (engineer 135, lateral 180, patent 180), about 4–5M tokens.

## Scoring

- **Quality:** the main study's individual-scoring prompt, unchanged (relevance, novelty, feasibility, specificity, 1–5; score = mean of the four), so quality scores are comparable across both studies.
- **Patentability:** a separate call per run with its own prompt (`top_ideas.py --rubric patent`): new, non-obvious, industrially applicable (1–5 each) and an overall patentability (1–5). It is a separate call so that asking about patents cannot shift the quality ratings. The judge cannot search prior art; patentability is its estimate from what it knows, not a legal assessment.

Both use `claude-sonnet-5-5`, blind to persona, condition and effort (it sees each idea's title, new elements and rationale only).

## Running it

From inside this folder (each step can be re-run; finished calls are skipped):

```bash
cd persona_as_factor
bash run_all.sh            # or copy the steps one at a time
```

1. `seed_from_main.py`: copy the 45 engineer calls and their scores.
2. Dry run: should report 540 planned, 45 already logged, 495 to run, and write the 18 distinct prompts to `runs/dry_run/` for inspection.
3. Generation (495 calls).
4. Scoring: quality (495 calls; the seeded 45 are already scored) and patentability (540 calls).
5. `analyze.py stats`, `top_ideas.py report`, `persona_analysis.py`.

## Outputs

| File | Contents |
| --- | --- |
| `runs/persona_runs.jsonl` | every call (seeded calls carry `seeded_from`) |
| `results/idea_scores.jsonl`, `results/patent_scores.jsonl` | raw judge outputs |
| `results/calls.csv`, `results/summary_*.csv` | cost and structure per call and per persona × condition × effort |
| `results/ideas_ranked.csv`, `results/top_ideas.md` | every idea with quality and patentability scores |
| `results/persona_summary.csv`, `.md` | per cell: top-idea rate, yield, patentable yield, means, CIs, exemplar echo |
| `results/persona_interaction.csv` | B ÷ C yield ratio per persona and effort, with CIs (H5, H6) |
| `results/charts/10_persona_yield.png` | yield per persona × representation × effort |

## Code changes in the main folder

Persona support was added to the shared scripts so that the main study's results are unchanged:

- `template_prompt.txt`: the first sentence of the system prompt is now `{persona}`; for the engineer it is filled with the original sentence.
- `KG_informed_brainstorm_AB_Test.py`: `--persona`, `--personas-file`; persona in each log record; engineer run ids unchanged, other personas prefixed (`lateral_B_M8_high_r01`); slice files found from a sub-folder; the dry run reports what is still to run.
- `top_ideas.py`: `--rubric patent` (separate prompt and file); a `persona` column and, when patent scores exist, patentability columns in `ideas_ranked.csv`.
- `analyze.py`: a `persona` column in `calls.csv`; summaries split by persona only when a log holds more than one.

Re-running the main study's analysis with the changed scripts gives identical summaries, tail results and top-ideas report (checked with the old and new scripts side by side on all 579 runs and 2,892 ideas of the main study, rebuilt from `results/ideas_ranked.csv` and the real quality scores); `calls.csv` and `ideas_ranked.csv` gain one column, `persona`, set to `engineer`. To confirm on the original log, re-run `analyze.py stats` and `top_ideas.py report` in the main folder and compare `summary_condition_effort.csv` and `top_ideas.md` with the versions from before.
