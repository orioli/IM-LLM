# Adversarial replication with Chinese models: can they break the paper?

**Status of this file.** Sections 1–7 were written on 2026-11-12 **before any generation call of this
replication was made** (only API plumbing tests and the capability "smoke" calls came first; neither is
analysed). They fix what is tested, with which models, and what counts as breaking a claim, so that the
verdicts cannot be fitted to the results. Section 8 logs deviations as they happen. Section 9 (results
and verdicts) is added afterwards.

## 1. Purpose

The paper claims that, for finding top ideas, the product graph does not pay for itself, and it draws
conclusions about which model is cheapest per top idea. All of its evidence comes from Claude models
(Haiku 5.5, Opus 5.5, Fable 5.1), judged by another Claude model (Sonnet 5.5).

This replication tries to **break those claims** with models from Chinese labs. It is an attack, but an
honest one: the design, the measures and the judge are the paper's own, the breaking criteria are fixed
below, every run is reported, and a claim that survives is reported as having survived.

Scope: Experiment 2 (market need M6, 50 ideas per call, four representations, 10 calls each, medium
effort). Experiment 1 (580 calls of 5 ideas, 13 needs) is **not** replicated: the budget is one API key
with a hard limit of USD 10.

## 2. Claims under test

Quoted from the repository's README and the paper (Experiment 2 and unit economics):

| | Claim |
| --- | --- |
| **C1** | "The full graph was the least efficient condition for every model, at about half the yield of the alternatives." |
| **C2** | "The need slice and no graph were indistinguishable for every model." The slice "did no better than giving no graph at all". |
| **C3** | Headline: "the full graph never paid off"; "for finding top ideas, the knowledge graph did not pay for itself." |
| **C4** | "For Opus and Fable the full graph did not lower the share of top ideas; it only cost more tokens." (the mechanism; descriptive) |
| **C5** | Unit economics: "Stronger models found up to twice as many top ideas per token, but Haiku found 20–40 times more per dollar", and from the net-cost table: "The cheapest model is therefore the one that matches the screening: a small model when an automated judge filters the output, a larger one when people do." |

## 3. Measures and statistics (the paper's)

- **Top idea:** judge score (mean of relevance, novelty, feasibility, specificity) ≥ 4.0.
- **Yield (primary):** top ideas per 100k tokens, input + output (reasoning tokens are output), all ideas
  of all calls of an arm. **Secondary:** top ideas per US dollar at the pinned host's list price.
- **Intervals:** 2,000 bootstrap resamples of calls within representation, 95% percentile interval. A
  difference between two arms is the difference of their independently resampled yields.
- **Net cost per top idea** at a screening cost per idea of $0, the judge's measured cost, and $0.50
  (`netcost_table.py`, which reproduces the paper's table for the three Claude models).

## 4. What counts as breaking a claim

Per model. "CI" is the 95% bootstrap interval of the stated difference in yield per token.

| Claim | **Contradicted** (the paper is wrong for this model) | Not replicated (weaker) | Replicated |
| --- | --- | --- | --- |
| C1 | A's yield is above B's or above C's, with the CI of that difference entirely above 0 | A is not the lowest of the four point estimates | A is the lowest and the CI of A − C is entirely below 0 |
| C2 | the CI of B − C is entirely above 0 (the slice beats no graph) | – | otherwise (the claim is a null; a CI of B − C entirely below 0 is noted as "no graph better") |
| C3 | the CI of A − C **or** of B − C is entirely above 0 per token (a graph beats no graph) | – | otherwise |
| C3, per dollar (secondary) | the same differences per dollar | – | otherwise |
| C5 | one model is cheapest, or indistinguishable from the cheapest (cheaper than it in ≥ 2.5% of resamples), in **all three** screening columns; or a large model beats every small model at the judge's screening cost; or a small model beats every large model at $0.50 | – | otherwise |

C4 gets no verdict: the share of top ideas with the full graph and with no graph is reported per model.

Results in the same direction as the paper whose interval includes 0 are reported as "same direction,
inconclusive", not as support.

**Guard against chance.** Four or five models and several contrasts make a spurious "contradicted" likely
enough to matter. So every contradiction of C1–C3 is re-tested: 10 fresh calls (replicates 11–20) of the
arms involved, same model and settings. It stands only if the fresh calls alone point the same way **and**
the interval over all 20 calls per arm still excludes 0. If the budget cannot cover the re-test, the
result is reported as "contradicted, unconfirmed".

## 5. Models

Generators, all through OpenRouter, each pinned to one host endpoint with no fallback:

| `GEN_MODEL` | Model | Role | Host (pinned) | USD per M tokens, in / out |
| --- | --- | --- | --- | --- |
| `deepseek` | DeepSeek V4.1 Flash | small, Haiku's price tier | `deepinfra/fp8` | 0.14 / 0.42 |
| `qwen` | Qwen3.8 Flash | small, Haiku's price tier | `alibaba` (first party) | 0.15 / 0.47 |
| `deepseekpro` | DeepSeek V4 Pro (0813, the GA release) | large: DeepSeek's flagship | `deepseek` (first party) | 0.66 / 1.98 |
| `glm` | GLM-5.3 Flash | small; **reserve** | `z-ai/fp8` (first party) | 0.15 / 0.50 |

*Why these.* The two small models were chosen on 2026-11-12 before any call, as the budget models of two
labs at Haiku's price ($0.10 / $0.50), on first-party or fp8 hosts. The large model is added for C5: the
paper's cost conclusions rest on large models being 40–100 times dearer than the small one, and DeepSeek's
flagship costs 3–5 times its small model. It is the same lab as one small model, so small and large can be
compared as Haiku and Opus are. GLM-5.3 Flash is the reserve: it replaces a small model that fails the
smoke test, and otherwise runs only if budget is left after everything else in this file.

*Rules fixed in advance.* A model must pass `run_all.sh smoke` (one full-graph call: valid JSON, ≥ 44
complete ideas, not cut off, served by the pinned host) or it is replaced, not tuned. If the smoke call of
DeepSeek V4 Pro projects more than $3 for its 40 calls, MiniMax M3 (`minimax`, first party, $0.30 / $1.20)
takes its place. Everything else is as documented in `README.md`, *Chinese models*: same prompts word for
word (`check_prompts.py`), same order, `max_tokens` 48,000 including reasoning, no temperature sent, JSON
asked for by the prompt only, effort `medium` through OpenRouter's `reasoning.effort`.

## 6. Judge

The paper's judge, unchanged: `claude-sonnet-5-5`, effort medium, `max_tokens` 16,000, the main study's
prompt, 5 consecutive ideas per request, blind to model, condition and position.

*Route.* The paper called the Anthropic API directly. Here the same requests go through OpenRouter's
Batch API to Anthropic's own endpoint (provider pinned, no fallback; `judge_batch.py`), which bills about
half the list price. The request body is the same; `output_config.effort` is passed through unchanged
(tested: OpenRouter validates and forwards it). Cost per idea in the tables is still computed at list
price, as in the paper.

*Judge-route check.* Before any new idea is scored, 12 calls the paper already scored (replicate 1 of each
representation of the Haiku, Opus and Fable runs, about 600 ideas) are scored again through the new route.
The route is **accepted** if, pooled over those ideas, the mean score differs by at most 0.10 and the
share of top ideas by at most 3 percentage points from the stored scores. If it is not accepted, C1–C3
still hold as tested (they compare arms within one model, all on the same route), but comparisons across
models (C5, the net-cost table, the per-dollar chart) are flagged as not comparable with the paper's
numbers.

## 7. Budget and order of work

Hard limit USD 10. Expected: route check $0.35; smoke calls $0.15; generation about $0.5 per small model
and $2 for the large one; judging $1.25 per model at batch price. Three models: about $7.3.

1. Route check and smoke calls.
2. Generation: `deepseek`, `qwen`, `deepseekpro` (40 calls each).
3. Judging by batch, tables, charts, verdicts.
4. With what is left, in this order: (a) confirmation runs for any contradiction (Section 4); (b) a
   **second judge**: the paper's pre-registered Haiku run (2,080 ideas, all four arms) scored again with
   the paper's prompt by a Chinese model (DeepSeek V4 Pro if at least $2.50 is left, otherwise DeepSeek
   V4.1 Flash), to test whether the paper's ranking of the representations depends on its Claude judge. The
   ranking counts as judge-dependent if, under the second judge, A is not below both B and C, or the CI of
   B − C is entirely above 0; read at score ≥ 4.0 and, because judges differ in scale, also at the cut-off
   that gives the same number of top ideas as Sonnet found; (c) the reserve model.

## 8. Deviations and events

(logged as they happen)

## 9. Results

(added after the runs)
