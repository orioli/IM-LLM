# M6_50ideas: does the graph matter once the model has to go past its first five ideas?

A follow-up to the main RQ1 experiment, on one market need, asking for **50 ideas per call** instead
of 5. Everything here is kept apart from the main study: its own run log, codes, scores, tables and
charts. The main study's files are only read, never changed.

The same 40 calls were run with three generator models: Claude Haiku 5.5 (the pre-registered run),
Claude Opus 5.5 and Claude Fable 5.1 (added afterwards, see *Models* below). Each has its own run log
and results folder; prompts, judge, coder and codebook are shared.

## Why

The main study asked for 5 ideas per call. Read one by one, those ideas converge on the same few moves
whatever the representation and whatever the effort (solid-state RF, RF thawing, sensor auto-stop):
asked for five, the model gives its five most obvious answers. With the answer saturated at five, the
experiment cannot show what the graph contributes. At high effort the need slice and the full graph
even have almost the same top-idea rate (14.7% vs 13.5%), so most of the slice's yield advantage came
from cheaper calls.

Asking for 50 ideas in one call forces the model past the obvious ones: within one answer it cannot
repeat itself, so after the main five it must find other moves. That is where the graph may matter:
with no graph the model has only its memory, with the slice it has 28 nodes of structure relevant to
the need, and with the full graph 123 nodes, more to build on but much of it off the need.

## Question

**RQ.** When the model must produce 50 ideas for one need in one answer, does the representation of
the product graph change how many different ideas (moves) it finds, how long it stays on the need,
and how far it gets beyond the main five?

## Hypotheses

Written down on 2026-10-19, before any 50-idea call was run.

- **H12 (the full graph gives more to build on).** A 50-idea list made with the full graph (A)
  contains more distinct moves than one made with the need slice (B). Supported if the 95% CI of
  A − B (distinct moves per call) is above 0.
- **H13 (a relevant graph gives depth).** A 50-idea list made with the need slice (B) contains more
  distinct moves than one made with no graph (C). Supported if the 95% CI of B − C is above 0.
- **H14 (the slice keeps the list on the need).** In the second half of the list (ideas 26–50), the
  share of ideas the judge rates on the need (relevance ≥ 4) is higher with the slice than (a) with the
  full graph and (b) with no graph. Each supported if the 95% CI of the difference is above 0.
- **H15 (the main five come first).** Over all conditions, ideas 1–5 of a list are more often one of
  the main five moves (the five moves found in the most of the main study's 5-idea M6 calls) than
  ideas 6–50 are. Supported if the 95% CI of the difference in shares is above 0. This checks the
  premise of the study: that a 5-idea call returns the main five.

How the outcomes would read:

- **H12 or H13 supported.** The graph matters for depth even though it barely mattered for the first
  five ideas.
- **Neither supported.** The model runs through the same moves with or without a graph, also deep in
  the list.
- **H14 supported.** The slice's value is focus: it keeps the later ideas on the need.
- **H15 supported.** This confirms that the 5-idea design measured the model's first answers only.

**An earlier plan, dropped.** The first version of this folder (also 2026-10-19) ran 50 calls of 5
ideas per condition, with hypotheses H8–H11. It was dropped before any analysis, because more 5-idea
calls only re-sample the same main five. Calls already logged in `runs/m6_runs.jsonl`, if any, are
not used.

## Choice of need

Applied to the 13 needs of the main study, in order:

1. **No overlap with the worked example.** The prompt's worked example (a webcam, a transparent
   casing) must not itself be a move for the need. This excludes M8 (know when food is ready) and
   M16 (not having to stand by the appliance).
2. **Every arm found something.** Each representation must have found at least one top idea for the
   need at high effort. This excludes M1, M5 and M11.
3. **Same order as the pooled result.** The representations must rank as in the pooled result at
   high effort (B > C > R > A). This excludes M3, M4, M7, M12 and M17.
4. **Chosen by the authors from the rest.** That left M6, M13 and M14. The authors chose M6 for
   relevance: operation is a central, long-standing usability problem of the appliance, and no
   single technology dominates its idea space.

## Design

| Factor | Level |
| --- | --- |
| Target need | M6, *simple operation with no learning curve* (slice: 28 nodes, 23% of the graph) |
| Representation | A full graph, B need slice, R random slice (same draw as the main study, `s1`), C no graph: the main study's files in `../slices/` |
| Ideas per call | **50** (the main study: 5) |
| Calls | **10 per representation**, 40 in total, 2,000 ideas, in random order (`--order-seed 6`) |
| Persona, operator, worked example | as in the main study: the innovation engineer's sentence, SUBSTITUTE, the webcam/transparent-casing example |
| Effort | medium (the model's default) |
| Generator | `claude-haiku-5-5` (pre-registered), `max_tokens` 48,000; also `claude-opus-5-5` and `claude-fable-5-1` (see *Models*) |

**Deviation: list length** (noted on 2026-10-19, after generation and before any coding or
analysis). Asked for 50, the model returned between 44 and 60 ideas per call. So that lists are
compared on equal length, every list is cut to its first *K* ideas, where *K* is the shortest list (44
in this run). All per-call measures use those *K* ideas: H14 uses ideas 26–*K*, H15 compares 1–5 with
6–*K*, and the last position band is 41–*K*. Tokens per list count the whole prompt plus the output in
proportion to the ideas kept. `discovery_analysis.py --positions N` changes *K*.

**Models** (added on 2026-10-20, after the Haiku run had been scored, so exploratory). To see whether
the result depends on the generator, the identical 40 calls were repeated with Claude Opus 5.5 and
Claude Fable 5.1. Nothing else changed: same prompts, same order, same effort, same judge. The switch is
the environment variable `GEN_MODEL` (`haiku`, the default, `opus`, `sonnet` or `fable`; see
`common.py` and `run_all.sh`):

| `GEN_MODEL` | Model | Run log | Results |
| --- | --- | --- | --- |
| `haiku` (default) | `claude-haiku-5-5` | `runs/m6_50ideas.jsonl` | `results/` |
| `opus` | `claude-opus-5-5` | `runs/m6_50ideas_opus.jsonl` | `results/opus/` |
| `fable` | `claude-fable-5-1` | `runs/m6_50ideas_fable.jsonl` | `results/fable/` |
| `deepseek` | `deepseek/deepseek-v4.1-flash` (OpenRouter) | `runs/m6_50ideas_deepseek.jsonl` | `results/deepseek/` |
| `deepseekpro` | `deepseek/deepseek-v4-pro-0813` (OpenRouter) | `runs/m6_50ideas_deepseekpro.jsonl` | `results/deepseekpro/` |
| `qwen` | `qwen/qwen3.8-flash` (OpenRouter) | `runs/m6_50ideas_qwen.jsonl` | `results/qwen/` |
| `glm` | `z-ai/glm-5.3-flash` (OpenRouter; smoke call only, not run) | `runs/m6_50ideas_glm.jsonl` | `results/glm/` |

Prefix every step of a run with the same `GEN_MODEL`, e.g. `GEN_MODEL=opus bash run_all.sh score`.
The cost tables of `../analyze.py stats` go to `results/<model>/stats/results/` for the added models,
so the Haiku tables in `results/` are not overwritten. The hypotheses H12–H15 refer to the Haiku run;
the other models are compared descriptively.

**Chinese models** (run on 2026-11-12). The same 40 calls were repeated with three models from Chinese
labs, to see whether the paper's claims hold for models from another family. Which claims we tested, what
would count as breaking each one, the models and the order of work were written down before any call
(`prereg/`, with SHA-256 hashes). The deviations and results are in
[`CHINESE_REPLICATION.md`](CHINESE_REPLICATION.md); this section is about how the runs were made.

| `GEN_MODEL` | Model | Host endpoint, pinned | USD per M tokens, in / out |
| --- | --- | --- | --- |
| `deepseek` | DeepSeek V4.1 Flash (small, Haiku's price tier) | `deepinfra/fp8` | 0.14 / 0.42 |
| `qwen` | Qwen3.8 Flash (small, Haiku's price tier) | `alibaba` (first party) | 0.15 / 0.47 |
| `deepseekpro` | DeepSeek V4 Pro 0813 (DeepSeek's flagship) | `baidu/fp8` | 0.659 / 1.976 |
| `glm` | GLM-5.3 Flash (reserve: passed its smoke call, not run for lack of budget) | `z-ai/fp8` (first party) | 0.15 / 0.50 |

*What is the same as in the Claude runs, and what is not.*

- Same prompts word for word (`check_prompts.py` passes for every `GEN_MODEL`), same order, same
  `max_tokens` (48,000, reasoning included, as Claude's thinking is), same judge model, prompt and effort.
- The models are reached through OpenRouter (`OPENROUTER_API_KEY`). The system and user prompts go as two
  chat messages; no temperature is sent (provider defaults, as with Claude); JSON is asked for by the
  prompt only, with no structured-output mode.
- Effort `medium` is sent as OpenRouter's `reasoning.effort`. Each lab maps it to its own reasoning budget,
  so "medium" is the same setting in name only: per call, Qwen3.8 Flash reasoned for about 12,400 tokens
  and the DeepSeek models for 3,600 to 5,200. `reasoning_tokens` is logged per call.
- Each call is pinned to one host endpoint with no fallback (`--or-host`), so all calls of a run use the
  same weights and quantisation. Cheaper listings exist, but on fp4 hosts. The log records the host that
  served the call (`served_by`), the model version (`model_version`) and the price actually billed
  (`cost_usd_billed`). The per-dollar charts use the table's list prices, like the Claude runs.
- A call that ends empty without hitting `max_tokens`, or that the provider breaks off, is logged as failed
  and retried by the next `generate`; a call cut off at `max_tokens` is a result, as before.
- **The judge** is the paper's (`claude-sonnet-5-5`, effort medium, the main study's prompt, 5 ideas per
  request), but reached through OpenRouter instead of the Anthropic API: `JUDGE_API=openrouter` routes
  `score_ideas.py` through OpenRouter's Messages API, and `judge_batch.py` (step `score-batch`) sends the
  same requests through its Batch API at about half price. Both are pinned to Anthropic as the provider.
  `judge_route_check.py` scored 596 ideas a second time through the new route: mean score 3.35 → 3.34,
  share of top ideas 12.8% → 11.7% (`results/judge_route_check.md`). In batch requests the output cap is
  2,000 tokens instead of 16,000, because OpenRouter reserves requests × cap against the key until a batch
  finishes; the judge's longest answer in about 2,800 requests was 530 tokens.

*Cost.* All of it ran on one OpenRouter key limited to USD 10: generation $0.23 (DeepSeek V4.1 Flash),
$0.49 (Qwen3.8 Flash) and $1.18 (DeepSeek V4 Pro), judging about $1.20 per model at batch price.
`python cost_breakdown.py` itemizes every call from the logs, prices the paper's own logged calls on the
same basis, and estimates a next round (`results/cost_breakdown.md`).

*Steps*, per model (shown for `qwen`):

```bash
export OPENROUTER_API_KEY=...             # generation and judge;  echo ${OPENROUTER_API_KEY:+set}
GEN_MODEL=qwen bash run_all.sh prompts    # dry run + prompt check, free
GEN_MODEL=qwen bash run_all.sh smoke      # ONE full-graph call -> runs/smoke_qwen.jsonl; must print PASS
GEN_MODEL=qwen bash run_all.sh generate   # the 40 calls
GEN_MODEL=qwen bash run_all.sh score-batch   # blind Sonnet judge by batch (submit, wait, tables)
GEN_MODEL=qwen bash run_all.sh chart      # Figure 8 for this run
```

With an Anthropic key, `score` works as before (`ANTHROPIC_API_KEY`); `JUDGE_API=openrouter bash
run_all.sh score` sends the same calls one by one through OpenRouter at list price. `smoke` sends the
longest prompt (full graph) once and checks that the answer parses, is not cut off, has at least 44 ideas,
each with a title, new elements and a rationale, and was served by the pinned host; it also prints the
projected cost of the run. A model that fails is replaced, not tuned. Smoke calls are kept apart from the
run logs and are not analysed. Do not edit `run_all.sh` while a step is running: bash reads the script
as it goes.

*Reading the runs.* No API calls:

```bash
python replication_report.py      # verdict per claim and model, yields, contrasts -> results/replication_report.md
python netcost_table.py           # the paper's net-cost table with a row per model -> results/netcost_table.{csv,md,tex}
python compare_stack_chart.py --models opus fable deepseek deepseekpro qwen   # the paper's yield figure with the new models added
python compare_runs_chart.py  --models opus fable deepseek deepseekpro qwen --unit dollars
python judge_family_check.py      # does the Claude judge prefer Claude-written ideas? -> results/judge_family_check.md
python cost_breakdown.py          # costs, from the logs -> results/cost_breakdown.md
```

The charts in `results/charts/` and `results/<model>/charts/` were drawn with this repository's chart code,
unchanged, and with Inter as matplotlib's default font, as in the paper's figures (the code doesn't set a
font, so on a machine without Inter they come out in DejaVu Sans). One difference from the paper's copy
of this figure: it was saved before the "standard labels" commit (2f23ffc), so its legend still reads "Full
graph, Slice, ..." where the current code writes "A · full graph, B · need slice, ...".

`compare_stack_chart.py` redraws the paper's yield figure (per dollar above, per token below) with one more
panel per new model on the same axes, so the Chinese models are read against Haiku, Opus and Fable
directly. The comparison charts draw the Chinese models only when asked with `--models`, and then write
files with the suffix `__<models>`, so the default figures (the Claude runs, used in the paper) never
change. `netcost_table.py` is the paper's last results table of Experiment 2, *net cost per top idea for a
given screening cost per idea*: generation only, screened by the automated judge (its measured cost, about
$0.0012 per idea), and screened by a person ($0.50 per idea). It has a row for every model that has been
run and scored, with bootstrap intervals, the cheapest model of each column in bold, and for each model
the screening cost at which it becomes cheaper than Haiku; for the three Claude models it reproduces the
paper's table.

*Easier-to-read version of the comparison figure.* With seven runs the stacked box-plot figure gets too wide
to read, so `compare_dotplot_chart.py` draws the same numbers with one row per run on a shared axis:
`fig_yield_dotplot*.png` (A per dollar, B per 100k tokens, each representation a dot with its 95% bootstrap
interval) and `fig_ratio_forest*.png` (each representation's yield divided by no graph's, per run and pooled
over runs). Same colours as the other figures, plus a marker shape per representation. `--models` works as
for the other comparison charts; without it the figures show only the paper's three runs.

*Confirmation runs.* A contrast that contradicts the paper is re-tested with 10 fresh calls per arm
(replicates 11 to 20), kept apart from the run: `CONFIRM="B C" GEN_MODEL=deepseek bash run_all.sh confirm`,
then every scoring step with `RUN_TAG=confirm` (run log `runs/m6_50ideas_<model>_confirm.jsonl`, results
in `results/<model>/confirm/`). `replication_report.py` reads them.

*Second judge.* `second_judge.py` scores a run's ideas again with a model from another family, with the
paper's judge prompt, and compares the ranking of the representations under the two judges
(`results[/<model>]/second_judge/<judge>/report.md`). With `--sample-per-arm N` it scores a random N requests
per representation instead of all of them, which is what `judge_family_check.py` uses.

**Prompts.** `check_prompts.py` checks that each prompt is the main study's, word for word, except
the one line "Return exactly 5 ideas" → "Return exactly 50 ideas". It does this by putting the 5 back
and matching the `prompt_sha256` logged in `../runs/rq1_full.jsonl`.

**Run ids.** The persona file `personas_50ideas.yaml` repeats the main study's engineer sentence
verbatim under the name `engineer50`. The name only prefixes the run ids (`engineer50_A_M6_medium_r01`),
so they never collide with the main study's calls.

**Cost.** Each 50-idea call writes roughly 15–25k output tokens, so expect about 0.8–1M generation
tokens per model, and a few minutes per call (longer for Opus and Fable). At list prices the 40 calls
cost about $0.35 with Haiku, $13 with Opus and $31 with Fable (see *Yield* below). If a call stops at `max_tokens`, raise `--max-tokens` to 64000 in
`run_all.sh` and run `generate` again (finished calls are skipped).

**The number of calls** is one setting (`--reps` in `run_all.sh`). In a test run on simulated data, 10
calls per condition separated differences of about 2–3 distinct moves per list.

## What is counted: moves

A **move** is a distinct way of serving the need, defined by *what* an idea replaces (a control, a
display, a setting step, a component or a user action) and *by what* (the principle that replaces it).

- **Same move.** Two ideas are the same move if an engineer would build them on the same principle,
  even if names, numbers or extras differ.
- **Different moves.** A dial with food pictures, a code on the packaging and a camera that
  recognises the food are three moves, although all three replace setting the time and power.
- **The target granularity.** A move should be the level at which a product manager would brief
  different engineering teams.

Each idea gets one **primary** move (its main change) and up to two **secondary** moves. All measures
use the primary move.

**Categories.** Each move has one category, from its main change:

- **Technology:** a technical principle or component is the point of the move (a sensor, an
  actuator, a heating or power technology, a material).
- **Interaction:** how the user tells the oven what to do, or how the oven tells the user (controls,
  display, voice, sound, an app).
- **Behaviour:** a decision, a step or the need to know something is removed (defaults, automatic
  start or stop, one-touch routines), using existing technology.
- **Ecosystem:** the move relies on something outside the appliance (food packaging, settings or
  recipes from a service, other devices).

When a move both adds a technology and removes a step, choose *technology* if the new technology is
what would be patented, and *behaviour* if an existing technology is only reused.

## Measures

The unit is one call, that is, one list of 50 ideas. The *position* of an idea is its place in the
list.

- **Distinct moves per call** (H12, H13), and per 100k tokens.
- **Within-call curve:** distinct moves after the first *p* ideas, for *p* = 1 to 50.
- **By position band** (1–5, 6–10, 11–20, 21–30, 31–40, 41–50):
  - the share of ideas that add a move not yet in the list
  - the mean quality score
  - the on-need share, judge relevance ≥ 4 (H14 uses positions 26–50)
  - the share of top ideas
- **Main-5 share** (H15): the share of ideas whose move is one of the main five. The main five are
  defined by the main study's 50 five-idea M6 calls, which are coded with the same codebook.
- **Over all calls of a condition:** moves found, the Chao2 estimate of how many moves the condition
  would find with unlimited calls, and sample coverage.
- **Descriptive measures:** distinct top moves per call (moves with an idea scoring ≥ 4.0), the share
  of non-technology moves, the share of ideas echoing the worked example, and novel moves (prior art
  not found).

**Intervals.** The CIs come from 2,000 bootstrap resamples of calls within each condition, as
percentile intervals. Chao2 uses the estimate ± 1.96 bootstrap SE. A hypothesis is supported only if
the CI of its pre-registered difference is above 0.

**Quality scores.** `score_ideas.py` uses the main study's judge prompt and criteria, imported
unchanged from `../top_ideas.py`. A 50-idea list goes to the judge as ten requests of five
consecutive ideas, so every request looks like a main-study request. The judge sees titles, new
elements and rationales only: no condition, no position. `ideas_scored.csv` has one row per idea: the
four criteria and their mean (`score`), the idea's `position` in its list, and, for human checking,
the idea as the judge saw it (`title`, `new_elements`, `rationale`) and the judge's one-sentence
`judge_comment`. Hide `condition`, `run_id` and `idea_id` before giving the sheet to a blind rater.

## Yield: top ideas per token and per dollar

These measures need only the judge scores, not the codebook, so they can be read before the coding
without biasing it.

- **Top idea:** an idea whose score (mean of the four criteria) is ≥ 4.0, as in the main study.
- **Yield:** all top ideas of an arm ÷ all its tokens (input + output), per 100k tokens: the slope of
  a line through the origin in the main study's Figure 8. All ideas of a call are counted (no cut to
  *K*), since yield is a rate per token.
- **Per dollar:** the same with each call's cost at the API list price, in USD per million tokens
  (input / output): Haiku 5.5 $0.10 / $0.50, Opus 5.5 $4 / $20, Fable 5.1 $10 / $50
  ([pricing](https://platform.claude.com/docs/en/about-claude/pricing), 2026-10-20). No batch or
  caching discount; output tokens include thinking. The judge's cost is the same for every model and
  is left out.
- **Two kinds of box plot.** *Bootstrap* boxes (default) show 2,000 resampled values of the arm's
  pooled yield (calls resampled within need): the uncertainty of the arm's average, box = middle 50%,
  whiskers = 95% CI. *Per-call* boxes (`--box calls`) show each call's own yield, one dot per call: the
  call-to-call variation, which is about √(calls) times wider. Compare arms with the bootstrap boxes.

**Results so far** (M6, 50 ideas asked per call, medium effort, 10 calls per arm; top ideas per 100k
tokens, and per dollar in brackets):

| Arm | Haiku 5.5 | Opus 5.5 | Fable 5.1 |
| --- | --- | --- | --- |
| Full graph (A) | 9.4 (266) | 26.3 (19.3) | 26.4 (7.5) |
| Need slice (B) | 20.4 (459) | 39.9 (22.9) | 51.3 (11.9) |
| Random slice (R) | 10.9 (246) | 37.2 (21.1) | 37.0 (8.5) |
| No graph (C) | 22.2 (468) | 34.8 (18.2) | 53.6 (11.4) |
| Top ideas / ideas | 126 / 2,080 | 270 / 1,985 | 295 / 2,001 |
| Cost of the 40 calls | $0.35 | $13.32 | $30.89 |

- The full graph is the least efficient arm for every model.
- The need slice and no graph are indistinguishable for every model (overlapping 95% CIs).
- For Opus and Fable the full graph does not lower the share of top ideas (14.2% and 15.6%, against
  13.1% and 14.5% with no graph); it only costs more tokens. For Haiku it lowers it too (5.4% vs 7.0%).
- Stronger models find up to about twice as many top ideas per token, but Haiku finds 20–40 times more
  per dollar.
- Ideas are shorter than in the main study (about 40 words against 100), and the judge scores them
  lower, so yields are not directly comparable with the main study's.

## Codebook

1. **Export the old ideas.** `export_old_ideas.py` writes the main study's 250 M6 ideas, from its
   5-idea calls, shuffled and blind to `codebook/old_M6_ideas.csv`. The key to where they came from is
   in a separate file; don't open it while building the codebook.
2. **Draft (optional).** `draft_codebook.py` has the coder model propose moves and assign the old
   ideas to them, writing `codebook/codebook_draft.yaml` and `draft_assignments.csv`.
3. **Edit by hand.** Edit the draft into `codebook/codebook.yaml` (schema:
   `codebook/codebook_template.yaml`). Check every definition and category, then set `status: final`
   and `version: 1`. Keep the draft unchanged, so the edits can be reported. Version 1 (2026-10-20,
   before any new idea was coded) has 35 moves; its edits from the 37-move draft are listed under
   `changes_from_draft` in the file: MV03 widened to food-picture presets on any control, MV13 redefined
   as one control with a few plain levels (MV35 merged in), MV25 merged into MV19, MV02 restricted to
   weighing (O150 moved to MV24, electrical or RF load sensing), tie-break rules written into the
   definitions, and the drawer, lid, sliding door and power cradle relabelled *interaction*. IDs are kept
   stable, so MV25 and MV35 are gaps.
4. **Bump the version** whenever moves or definitions change. Filling in prior art does not need a
   new version.

The codebook is built from the old ideas, before it meets the new lists. The new lists will contain
moves the old 5-idea calls never reached (that is the point of the study); they enter the codebook
through the NEW loop below, blind to condition.

## Coding

- **Who codes, and how blind.** The coder is `claude-sonnet-5-5` at medium effort. Ideas from all
  four conditions and all positions are shuffled together and coded in batches of 10. The coder sees
  each idea's title, new elements and rationale, with node ids removed, and never the condition or
  the position.
- **What gets coded.** Both the new 2,000 ideas and the main study's 250 M6 ideas are coded against
  the same codebook. The old ideas are needed to define the main five. Each model's run is coded into
  its own results folder (`GEN_MODEL=opus bash run_all.sh code`, and so on), with the same codebook
  version, so the main-study ideas are coded once per model folder.
- **The loop.** Run `code`, then `review` (which writes the NEW proposals, without conditions). Add
  the real new moves to the codebook (`source: new_run`) and bump the version, then run `code` again,
  which recodes the NEW ideas. Repeat until NEW is under 2% of ideas.
- **The final pass.** Run `recode` with the final codebook, then resolve any remaining NEW the same
  way. The analysis refuses to run while any NEW remain.

## Human check

- **Sample.** `code_moves.py sample` draws 100 new ideas, 25 per representation, shuffled and blind,
  into `results/human_coding_sheet.csv`, with `results/codebook_for_coders.md` as the coding guide.
  Code them without looking at `results/moves.jsonl`.
- **Agreement.** `code_moves.py agree` reports Cohen's kappa on the primary move and on its category.
- **Threshold, set in advance:** kappa ≥ 0.6. Below that, revise the definitions behind the most
  frequent disagreements, bump the version, recode everything, and code a fresh sample
  (`sample --force --seed 12`).

## Prior art

For every move in the final codebook, search patents (Google Patents, Espacenet) and products. Record
`prior_art` (`commercial`, `patented`, `published` or `not_found`) and `prior_art_ref`. Do this from
the codebook alone and before running the analysis: the codebook does not show which representation
found a move.

## Running it

`bash run_all.sh <step>`, in this order (steps marked *hand* are done by a person). For Opus or
Fable, prefix each step with `GEN_MODEL=opus` or `GEN_MODEL=fable`. Use `bash run_all.sh`, not
`./run_all.sh`: copying the file can drop its execute permission. In zsh, don't paste the `#`
comments from this README after a command; zsh reads them as arguments.

| Step | What it does |
| --- | --- |
| `prompts` | dry run (40 calls planned) and the check that only the number of ideas differs |
| `export` | the main study's 250 M6 ideas, blind, for the codebook |
| `draft` | optional model draft of the codebook |
| `codebook` | *hand*: edit into `codebook/codebook.yaml`, `status: final` |
| `smoke` | one test call (full graph) to `runs/smoke_<model>.jsonl`, checked by `smoke_check.py`; for new models, before `generate` |
| `generate` | the 40 calls of 50 ideas |
| `score` | quality scores (the main study's judge, 5 ideas per request), cost tables |
| `code` | code the new ideas and the main study's M6 ideas into moves |
| `review` | NEW proposals; *hand*: update the codebook, bump the version, `code` again |
| `recode` | final pass with the final codebook |
| `sample` / `agree` | *hand* coding of 100 ideas, then agreement |
| `priorart` | *hand*: prior art for every move |
| `analyze` | tests, tables, charts |
| `chart` | Figure 8 for this run (running count, box plot of slopes, key): per-call and bootstrap versions |

The comparison charts across runs need no step: `python compare_runs_chart.py` and
`python compare_stack_chart.py` (options below). No API calls.

Generation can run while you edit the codebook. Just don't read `runs/m6_50ideas.jsonl` until
`codebook.yaml` is final.

Every API step needs `ANTHROPIC_API_KEY` set in the terminal it runs in (`echo ${ANTHROPIC_API_KEY:+set}`
to check). A step run without it logs every request as failed within seconds; set the key and run the
same step again, which retries only what failed.

**Charts across runs:**

| Command | Chart |
| --- | --- |
| `python yield_chart.py` | Figure 8 for one run (`GEN_MODEL` picks the run): running count of top ideas against tokens, box plot of slopes, ranked key; `--box bootstrap` for bootstrap boxes, `--threshold` for another cut-off |
| `python compare_runs_chart.py` | box plots of yield side by side: Haiku · 5 ideas/call (main study), then Haiku, Opus, Fable · 50 ideas/call (each added once its scores exist), one shared y axis and legend |
| `... --n5-needs all` | the 5-idea panel over all 13 needs instead of M6 only |
| `... --unit dollars` | top ideas per dollar at list price (log axis) |
| `... --box calls` | one dot per call instead of bootstrap boxes (zeros shown on a symlog axis with dollars) |
| `python compare_stack_chart.py` | two of those charts stacked, one legend, model titles once; rows set with `--top` / `--bottom NEEDS:BOX:UNIT`, e.g. `--top all:bootstrap:dollars --bottom all:bootstrap:tokens` |
| `python netcost_table.py` | not a chart: the net-cost table (cost per top idea at a given screening cost per idea) for every model run and scored; `--models`, `--screen` |
| `python m6_thumb.py` | the "what each prompt contains" panel for M6 (full graph, no graph, random slice, slice); built automatically by the charts |

## Outputs

| File | Contents |
| --- | --- |
| `runs/m6_50ideas.jsonl` | every generation call |
| `results/idea_scores.jsonl`, `ideas_scored.csv` | quality scores per idea, with position |
| `results/moves.jsonl` | every coding (latest per idea wins) |
| `results/new_move_proposals.csv` | NEW ideas and proposed moves, for review |
| `results/human_coding_sheet.csv`, `human_agreement.md`, `human_disagreements.csv` | human check |
| `results/discovery_summary.md`, `.csv`, `discovery_by_position.csv`, `discovery_tests.csv`, `move_incidence.csv` | results |
| `results/charts/m6_within_call.png` | distinct moves along a 50-idea list, per representation |
| `results/charts/m6_by_position.png` | new-move, on-need and main-5 shares by position |
| `results/charts/m6_incidence.png` | which moves each representation found, next to the main study's 5-idea calls |
| `runs/m6_50ideas_opus.jsonl`, `runs/m6_50ideas_fable.jsonl`, `results/opus/`, `results/fable/` | the same for Opus and Fable |
| `results/yield_m6_50ideas[_opus\|_fable].csv` | yield per arm: calls, ideas, top ideas, tokens, top ideas per 100k tokens and 95% CI |
| `results[/<model>]/charts/8_top_ideas_vs_tokens_m6_50ideas*.png` | Figure 8 for each run (plain, `_box` per call, `_box_bootstrap`) |
| `results/charts/compare_slopes_haiku5_haiku50_opus50*.png`, `results/compare_slopes*.csv` | the comparison across runs; suffixes `_calls`, `_n5allneeds`, `_usd` follow the options |
| `results/charts/compare_stack_*.png`, `results/compare_stack_row*.csv` | stacked comparison |
| `results/charts/m6_prompts_thumb.png` | the M6 prompt panel used in these charts |

## Files

`common.py` (shared helpers, the `GEN_MODEL` switch), `personas_50ideas.yaml`, `check_prompts.py`, `smoke_check.py`,
`export_old_ideas.py`, `draft_codebook.py`, `score_ideas.py`, `code_moves.py`, `discovery_analysis.py`,
`yield_chart.py` (Figure 8 per run, reusing `../tail_charts.py`), `compare_runs_chart.py` and
`compare_stack_chart.py` (comparisons across runs), `m6_thumb.py`, `prompts/` (coding and drafting
prompts), `codebook/`, `run_all.sh`.

## References

- Chao, A. (1987). Estimating the population size for capture-recapture data with unequal catchability. *Biometrics, 43*(4), 783–791.
- Chao, A., & Jost, L. (2012). Coverage-based rarefaction and extrapolation: standardizing samples by completeness rather than size. *Ecology, 93*(12), 2533–2547.
