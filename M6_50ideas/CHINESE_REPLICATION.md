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

## 8. What happened, and where we deviated

Times are UTC, 12 November unless noted. Sections 1 to 7 were written before any of this and haven't been
touched since. The file as it stood then is `prereg/2026-11-12_before_the_runs.md` (SHA-256
`1fe57207c4f5826ca639d8b528b37b28eab4149e2ba1fbda8d8f8df980fa98f3`).

1. Judge route check, accepted (17:03 to 17:12). We re-scored the 12 calls listed in Section 6 through the
   new route. 124 of 125 requests came back usable (one answer had the wrong number of ratings), for $0.37.
   Over 596 ideas the mean score went from 3.35 to 3.34 (difference -0.006, 95% CI -0.026 to +0.015, limit
   ±0.10) and the share of top ideas from 12.8% to 11.7% (limit ±3 points). The two scores correlate at 0.88.
   Details in `results/judge_route_check.md`.
2. Deviation: in batch requests the judge's output cap is 2,000 tokens instead of 16,000. While a batch
   runs, OpenRouter holds back its worst case on the key (requests × max_tokens at the output price). The
   125 check requests with the paper's cap held $10.07, the whole key, for nine minutes, and one model's 430
   requests would have needed $34. With a cap of 2,000 a model's batch holds about $4.65. The model doesn't
   see the cap, and the judge's longest answer was 530 tokens in the paper's 1,252 requests and 509 in our
   check. A request that hits the cap is logged as failed and scored again without it. We decided this
   before scoring any new idea.
3. Deviation: DeepSeek V4 Pro ran on Baidu's endpoint (`baidu/fp8`) and not on DeepSeek's. The account's
   privacy setting refuses DeepSeek's own endpoint because it trains on prompts. Five other hosts answered
   a one-word test and we pinned the cheapest fp8 one ($0.659 / $1.976 per million tokens), before any V4
   Pro call.
4. Test calls (one full-graph call per model, not analysed). All four models passed.

   | Model | Ideas | Input tokens | Output tokens (reasoning) | Seconds | Billed | Projected 40 calls |
   | --- | --- | --- | --- | --- | --- | --- |
   | DeepSeek V4.1 Flash | 49 | 8,284 | 11,306 (2,409) | 74 | $0.0059 | $0.24 |
   | Qwen3.8 Flash | 50 | 8,922 | 24,198 (10,108) | 205 | $0.0127 | $0.51 |
   | DeepSeek V4 Pro | 50 | 8,258 | 11,743 (2,054) | 184 | $0.0286 | $1.15 |
   | GLM-5.3 Flash (reserve) | 50 | 8,224 | 9,791 (24) | 200 | $0.0061 | $0.25 |

   V4 Pro projected $1.15, under the $3 limit in Section 5, so it stayed in. Medium effort meant very
   different amounts of reasoning: about 10,000 tokens for Qwen, 2,000 for the DeepSeek models and 24 for GLM.
5. One V4 Pro call hit the host's rate limit and went through when we retried it. All three runs ended
   with 40 of 40 calls and none was cut off. Qwen numbered its idea titles in 18 of its 40 calls, spread
   evenly over the representations and with no difference in score (mean 3.14 against 3.16).
6. Confirmation run for DeepSeek V4.1 Flash, slice against no graph (17:44 to 17:58), as Section 4 requires.
7. Second judge (Section 7, step 4b): DeepSeek V4 Pro on the paper's Haiku run, started at 18:02 with $3.16
   left on the key. The host refused most requests above about four a minute, so 371 of the 430 were done
   by 20:27 and the last 59 on 13 November (07:10 to 07:23) with three requests at a time. $1.87 in all.
8. GLM-5.3 Flash, the reserve, wasn't run. It would have needed about $1.45 with $1.42 left, and its judge
   batch alone would have held $4.30 on the key.
9. DeepSeek V4 Pro's price depends on the time of day. On 13 November at 07:00 the same host charged $1.32 /
   $3.96, twice what we paid on 12 November between 17:00 and 18:00. Peak hours are 01:00 to 04:00 and
   06:00 to 10:00 on weekdays. Our calls and tables use the off-peak price they were billed at. At peak, V4
   Pro's generation cost per top idea would be $0.020 instead of $0.010.
10. Added on 13 November and not pre-registered: `power_analysis.py` (all six runs pooled, and how many
    calls a bigger experiment needs) and `FULL_EXPERIMENT_PLAN.md`.
11. Added on 14 November before any call: the judge check in Section 10, frozen as
    `prereg/2026-11-14_before_the_judge_check.md` (SHA-256
    `0248fc3745d53bb02dbd6c0031f0166a2daa542297947f3c475e12072869fe95`). Its results are in Section 11.

## 9. Results

Tables: `results/replication_report.md`, `results/netcost_table.md`, `results/judge_route_check.md`. Figure:
`results/charts/compare_stack_all_bootstrap_dollars__M6_calls_tokens__opus_fable_deepseek_deepseekpro_qwen.png`.

None of the five claims broke on these three models. Top ideas per 100k tokens over the first 10 calls per
representation were:

| Model | A full graph | B slice | R random | C no graph | Top ideas |
| --- | --- | --- | --- | --- | --- |
| DeepSeek V4.1 Flash | 11.9 | 23.1 | 18.1 | 14.1 | 109 of 2,040 (5.3%) |
| DeepSeek V4 Pro | 12.5 | 20.2 | 20.9 | 19.6 | 126 of 1,981 (6.4%) |
| Qwen3.8 Flash | 6.2 | 7.7 | 4.4 | 11.0 | 82 of 2,000 (4.1%) |

C1 (the full graph is the least efficient) wasn't contradicted, but the data are weaker than the wording.
The full graph is lowest for both DeepSeek models, though its difference from no graph has an interval
that includes 0. For Qwen the random slice is lowest (4.4 against 6.2, not distinguishable) and the full
graph is clearly below no graph (-4.9, CI -8.7 to -1.2). The weaker wording, that the full graph is never
better than no graph, held for all three.

C2 and C3 (the slice does no better than no graph, and no representation beats no graph) held. DeepSeek
V4.1 Flash went against them on its first 10 calls, with the slice ahead of no graph by +9.1 (CI +1.0 to
+17.4), but the re-test didn't confirm it. On 10 fresh calls no graph came out ahead (-3.9), and over all
20 calls the difference is +2.6 (CI -4.4 to +9.2). V4 Pro shows no difference (+0.5) and Qwen has no graph
ahead (-3.3).

C4 held: the full graph didn't lower the share of top ideas for any of the three models. C5 (net cost)
held as well, since no model is cheapest in every column. With the AI judge screening, Haiku ($0.023 per top
idea) and DeepSeek V4.1 Flash ($0.025) are tied, and with a person screening, Fable and Opus ($3.50 and
$3.73) cost less than half of any Chinese model ($7.87 to $12.20).

Other things the runs showed (points 3 to 5 weren't pre-registered):

1. A 10-call arm can give a "significant" difference by chance, which is what happened with DeepSeek V4.1
   Flash. The paper's intervals come from the same design, on one need with 10 calls per representation.
2. The judge doesn't agree with itself on which ideas are top. Of 76 ideas it had scored 4.0 or more, 50
   were top again on a second pass (66%). For Haiku's ideas it was 2 of 10 (kappa 0.19). Counts per
   representation stay stable, but which ideas are the top ones doesn't.
3. The finding that stronger models get more top ideas per token didn't carry over. DeepSeek's flagship
   found top ideas at 6.4% against 5.3% for its small model, at five times the cost per top idea, and no
   Chinese model got near Opus or Fable (13.6% and 14.7%). On generation cost alone DeepSeek V4.1 Flash
   ($0.002 per top idea) is cheaper than Haiku ($0.003).
4. In the paper's own Opus run the slice beats no graph per dollar once the cut-off is lowered: +10.0 top
   ideas per dollar at 3.75 (CI +2.3 to +17.6), +13.5 at 3.5 (+3.0 to +22.1) and +4.7 at the paper's 4.0
   (-1.7 to +11.3). We found this by trying several cut-offs, so it needs a fresh Opus run before it counts.
5. Medium effort isn't the same setting across labs. Qwen reasoned for about 12,400 tokens a call and the
   DeepSeek models for 3,600 to 5,200. With Qwen the full graph also doubles the reasoning, so more than
   half of its extra tokens are output and not input.

The second judge, DeepSeek V4 Pro, scored the paper's Haiku run with the paper's prompt (2,073 ideas rated
by both judges, `results/second_judge/deepseek_deepseek-v4-pro-0813/report.md`):

| Top ideas per 100k tokens, Haiku run | A full graph | B slice | R random | C no graph |
| --- | --- | --- | --- | --- |
| Sonnet 5.5 (the paper), score ≥ 4.0 | 9.4 | 20.4 | 10.9 | 22.2 |
| DeepSeek V4 Pro, score ≥ 4.0 | 66.5 | 112.0 | 102.2 | 133.9 |
| DeepSeek V4 Pro, score ≥ 4.5 (as many top ideas as Sonnet found) | 17.8 | 20.9 | 19.5 | 22.2 |

By the rule in Section 7 the ranking of the representations doesn't depend on the judge. Under DeepSeek V4
Pro the full graph is below both the slice and no graph, and the slice doesn't beat no graph, at either
cut-off. At 4.0 no graph is even ahead of the slice (-21.8, CI -38.2 to -6.5).

The two judges don't agree on individual ideas, though. DeepSeek V4 Pro is much more generous (mean 3.69
against 3.13, and 40% of ideas at 4.0 or more against 6%). Their scores correlate at 0.65, and on which
ideas are top they agree barely above chance: kappa 0.13 at 4.0 and 0.17 at the matched cut-off, where only
34 of Sonnet's 126 top ideas are top for both. How much the full graph costs depends on the judge as well.
At the matched cut-off DeepSeek V4 Pro rates more full-graph ideas top than no-graph ideas (53 against 37),
so the full graph only loses through its tokens, at 0.80 of no graph's yield (the interval of the
difference includes 0) against 0.42 under Sonnet. And the random slice, as poor as the full graph under
Sonnet, is level with the slice under DeepSeek V4 Pro.

All six runs together (`results/power_analysis.md`, added later): pooled over models with random effects,
the full graph's yield is 0.57 of no graph's [0.48-0.68] (Claude 0.55, Chinese 0.60) and the slice's is 1.01
[0.88-1.16] (Claude 1.00, Chinese 1.04). On M6 the Chinese models reproduce both effects at about the size
the paper reports.

The limits are the ones of the design. It covers one need, M6, which the paper picked because it already
showed the pattern, and 10 calls per representation, which in a single model only detect a ratio of about
1.9. We had three models from two labs, didn't replicate Experiment 1 and had no human ratings.
`FULL_EXPERIMENT_PLAN.md` sets out what a full experiment would need. The spend is broken down in
`results/cost_breakdown.md`.

## 10. Addendum, 14 November: does the judge prefer its own family?

Written before any call of this test. Sections 1–9 above are unchanged by it.

**Question.** Under Sonnet the Claude models look better than the Chinese ones: 13.6% and 14.7% top ideas
for Opus and Fable, 4.1–6.4% for the three Chinese models, and DeepSeek's flagship barely ahead of its
small model. The paper's unit economics rest on this ranking ("a larger model when people screen"). But
every model in the paper was rated by a Claude judge, and its robustness check (`rerank_extremes.py`) used
another Claude model. Is the ranking quality, or a Claude judge preferring Claude-written ideas?

**Design.** A judge from another family re-scores a sample of the ideas Sonnet already scored, in all six
50-idea runs (Haiku, Opus, Fable, DeepSeek V4.1 Flash, DeepSeek V4 Pro, Qwen3.8 Flash). Judge: DeepSeek V4.1
Flash, pinned to `deepinfra/fp8`, effort medium, the paper's judge prompt unchanged (`second_judge.py`).
Sample: 25 judge requests (125 ideas) per representation and run, drawn at random with a fixed seed, so
100 requests and about 500 ideas per run. If at least $0.60 is left on the key when this wave is done, a
second wave adds 15 requests per representation and run; the analysis uses everything scored. Budget: the
$1.37 left on the key, which cannot be exceeded.

**Primary measure.** For each judge, the gap between the families: mean score of the three Claude runs
minus mean score of the three Chinese runs (runs weighted equally), divided by that judge's standard
deviation of scores over the sampled ideas. The *family preference index* is Sonnet's gap minus the
DeepSeek judge's gap. 95% interval: 2,000 bootstrap resamples of requests within run, the same requests for
both judges.

**Guard against a weaker judge.** A judge that tells ideas apart less well shrinks every gap, not only the
one between families. So the same is computed for a gap inside one family, Opus and Fable against Haiku.

**Decision rule.**

- *Sonnet prefers Claude-written ideas* if the interval of the family preference index lies above 0 **and**
  the share of the within-Claude gap that the DeepSeek judge keeps is larger than the share of the
  between-family gap it keeps, with the interval of the difference above 0.
- *No evidence of a family preference* if the index's interval includes 0.
- *Ambiguous* otherwise (both gaps shrink alike: the second judge may just separate ideas less).

**Secondary.** Share of top ideas per run under each judge: Sonnet at 4.0; the DeepSeek judge at the
cut-off that gives the same overall share of top ideas as Sonnet on the sampled ideas. The ratio of
Claude to Chinese top-idea shares under each judge. The same comparison for DeepSeek-written ideas against
Qwen's, to see whether the DeepSeek judge prefers its own family. Ranking of the six runs under each
judge.

## 11. Results of the judge check

Run on 14 November between 20:34 and 20:51 UTC. The first wave (25 requests per representation and run)
cost $0.30 and left $1.08 on the key, so the second wave ran as Section 10 says. 4,695 ideas were rated by
both judges, about 780 per run, for $0.48. Details are in `results/judge_family_check.md`.

| Run | Mean score, Sonnet | Mean score, DeepSeek judge | Top ideas, Sonnet (≥ 4.0) | Top ideas, DeepSeek (≥ 4.5, same overall share) |
| --- | --- | --- | --- | --- |
| Haiku 5.5 | 3.13 | 3.64 | 6.2% | 4.0% |
| Opus 5.5 | 3.39 | 3.89 | 12.6% | 9.9% |
| Fable 5.1 | 3.43 | 3.91 | 16.0% | 12.2% |
| DeepSeek V4.1 Flash | 3.20 | 3.80 | 5.3% | 6.0% |
| DeepSeek V4 Pro | 3.04 | 3.54 | 6.5% | 4.6% |
| Qwen3.8 Flash | 3.14 | 3.69 | 4.9% | 5.4% |

By the pre-registered rule the result is ambiguous. Sonnet's gap between the families is 0.39 standard
deviations and the DeepSeek judge's is 0.29, which makes the family preference index +0.10 (CI +0.05 to
+0.15). The DeepSeek judge keeps 93% of the gap between Opus and Fable on one side and Haiku on the other,
but only 74% of the gap between the families. That difference (+0.18) has an interval from -0.02 to +0.38,
though, so a judge that just separates ideas less well can't be ruled out.

The ranking itself doesn't depend on the judge's family. The DeepSeek judge puts the six runs in the same
order as Sonnet (Spearman 1.00), with Fable and Opus on top and DeepSeek V4 Pro last, and relative to
Qwen's it doesn't rate DeepSeek-written ideas any higher than Sonnet does (difference -0.01, CI -0.10 to
+0.07). At the matched cut-off the Claude runs get 1.6 times the Chinese runs' share of top ideas, against
2.1 times under Sonnet. How big the Claude models' lead is depends on the judge, and only human ratings can
say which judge is closer.

The whole round, this check included, cost $9.08 of the $10 key (`results/cost_breakdown.md`).
