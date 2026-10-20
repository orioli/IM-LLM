# M6_50ideas: does the graph matter once the model has to go past its first five ideas?

A follow-up to the main RQ1 experiment, on one market need, asking for **50 ideas per call** instead
of 5. Everything here is kept apart from the main study: its own run log, codes, scores, tables and
charts. The main study's files are only read, never changed.

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
| Generator | `claude-haiku-5-5`, `max_tokens` 48,000 |

**Prompts.** `check_prompts.py` checks that each prompt is the main study's, word for word, except
the one line "Return exactly 5 ideas" → "Return exactly 50 ideas". It does this by putting the 5 back
and matching the `prompt_sha256` logged in `../runs/rq1_full.jsonl`.

**Run ids.** The persona file `personas_50ideas.yaml` repeats the main study's engineer sentence
verbatim under the name `engineer50`. The name only prefixes the run ids (`engineer50_A_M6_medium_r01`),
so they never collide with the main study's calls.

**Cost.** Each 50-idea call writes roughly 15–25k output tokens, so expect about 1M generation tokens
in all, and a few minutes per call. If a call stops at `max_tokens`, raise `--max-tokens` to 64000 in
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
elements and rationales only: no condition, no position.

## Codebook

1. **Export the old ideas.** `export_old_ideas.py` writes the main study's 250 M6 ideas, from its
   5-idea calls, shuffled and blind to `codebook/old_M6_ideas.csv`. The key to where they came from is
   in a separate file; don't open it while building the codebook.
2. **Draft (optional).** `draft_codebook.py` has the coder model propose moves and assign the old
   ideas to them, writing `codebook/codebook_draft.yaml` and `draft_assignments.csv`.
3. **Edit by hand.** Edit the draft into `codebook/codebook.yaml` (schema:
   `codebook/codebook_template.yaml`). Check every definition and category, then set `status: final`
   and `version: 1`. Keep the draft unchanged, so the edits can be reported.
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
  the same codebook. The old ideas are needed to define the main five.
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

`bash run_all.sh <step>`, in this order (steps marked *hand* are done by a person):

| Step | What it does |
| --- | --- |
| `prompts` | dry run (40 calls planned) and the check that only the number of ideas differs |
| `export` | the main study's 250 M6 ideas, blind, for the codebook |
| `draft` | optional model draft of the codebook |
| `codebook` | *hand*: edit into `codebook/codebook.yaml`, `status: final` |
| `generate` | the 40 calls of 50 ideas |
| `score` | quality scores (the main study's judge, 5 ideas per request), cost tables |
| `code` | code the new ideas and the main study's M6 ideas into moves |
| `review` | NEW proposals; *hand*: update the codebook, bump the version, `code` again |
| `recode` | final pass with the final codebook |
| `sample` / `agree` | *hand* coding of 100 ideas, then agreement |
| `priorart` | *hand*: prior art for every move |
| `analyze` | tests, tables, charts |

Generation can run while you edit the codebook. Just don't read `runs/m6_50ideas.jsonl` until
`codebook.yaml` is final.

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

## Files

`common.py` (shared helpers), `personas_50ideas.yaml`, `check_prompts.py`, `export_old_ideas.py`,
`draft_codebook.py`, `score_ideas.py`, `code_moves.py`, `discovery_analysis.py`, `prompts/` (coding
and drafting prompts), `codebook/`, `run_all.sh`.

## References

- Chao, A. (1987). Estimating the population size for capture-recapture data with unequal catchability. *Biometrics, 43*(4), 783–791.
- Chao, A., & Jost, L. (2012). Coverage-based rarefaction and extrapolation: standardizing samples by completeness rather than size. *Ecology, 93*(12), 2533–2547.
