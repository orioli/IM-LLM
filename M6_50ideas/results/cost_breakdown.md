# What it cost, and what a next round would cost

All numbers come from the logs in this repository (`python cost_breakdown.py`).

## 1. This round (OpenRouter key, USD 10 limit)

| Item | Size | Billed |
| --- | --- | --- |
| Generation, DeepSeek V4.1 Flash | 40 calls of 50 ideas | $0.23 |
| Generation, Qwen3.8 Flash | 40 calls of 50 ideas | $0.49 |
| Generation, DeepSeek V4 Pro | 40 calls of 50 ideas | $1.18 |
| Generation, confirmation calls (DeepSeek V4.1 Flash) | 20 calls | $0.11 |
| Test calls before each run (one per model) | 4 calls | $0.05 |
| Sonnet 5.5 judge, DeepSeek V4 Pro run | 406 requests of 5 ideas | $1.25 |
| Sonnet 5.5 judge, DeepSeek V4.1 Flash run | 412 requests of 5 ideas | $1.20 |
| Sonnet 5.5 judge, Qwen3.8 Flash run | 402 requests of 5 ideas | $1.24 |
| Sonnet 5.5 judge, confirmation calls | 204 requests of 5 ideas | $0.59 |
| Sonnet 5.5 judge, route check (12 calls the paper had scored) | 125 requests of 5 ideas | $0.37 |
| Sonnet 5.5 judge, two requests re-sent one by one | 2 requests | $0.01 |
| Second judge DeepSeek V4 Pro, on the Haiku run | 430 requests of 5 ideas | $1.87 |
| Second judge DeepSeek V4.1 Flash, sample of all six runs | 960 requests of 5 ideas | $0.48 |
| **Total** | | **$9.08** |

The Sonnet judge went through OpenRouter's Batch API, which bills half the list price. At list price, as the paper's runs are priced, the same round would have cost about $13.73: generation $2.16, Sonnet judge $9.22, second judges $2.35.

## 2. The paper's own calls, at list price

Every call logged in the repository, priced at list price with no batch or caching discount, the same basis as the paper's per-dollar figures. An actual bill can be lower if discounts or credits applied; the logs cannot show that.

| Item | Calls or requests | List price |
| --- | --- | --- |
| Experiment 1, generation (580 calls, Haiku) | 580 | $2.85 |
| Experiment 1, pilot generation | 48 | $0.18 |
| Experiment 1, judge: pairwise set comparisons | 1,159 | $9.10 |
| Experiment 1, judge: idea scores | 579 | $4.51 |
| Experiment 1, pilot judging | 925 | $7.15 |
| Persona follow-up, generation | 532 | $2.00 |
| Persona follow-up, judge (quality and patent scores) | 1,052 | $8.65 |
| Experiment 2, generation, Haiku | 40 | $0.35 |
| Experiment 2, generation, Opus | 40 | $13.32 |
| Experiment 2, generation, Fable | 40 | $30.89 |
| Experiment 2, judge (three runs) | 1,252 | $7.39 |
| Experiment 2, re-rating of the extremes (Opus) | 12 | $0.36 |
| **Total** | | **$86.76** |

Of this, generation is $49.60 (Opus and Fable alone $44.21) and judging $37.16.

## 3. A next round

Unit costs, measured in this round unless marked:

- Sonnet judge, one request of 5 ideas, by batch: $0.0030 (list price $0.0059).
- Second judge, one request: DeepSeek V4 Pro $0.0043 (mostly at the off-peak price; DeepSeek charges twice as much at peak hours), DeepSeek V4.1 Flash $0.00050.
- Generation, one 50-idea call: DeepSeek V4.1 Flash $0.0057, Qwen3.8 Flash $0.0123, DeepSeek V4 Pro $0.0296, GLM-5.3 Flash $0.0061, Haiku 5.5 $0.0088, Opus 5.5 $0.3330 (GLM from its one test call; Haiku and Opus from the paper's runs at list price).
- Generation, one 5-idea call: DeepSeek V4.1 Flash $0.0024, Qwen3.8 Flash $0.0070, DeepSeek V4 Pro $0.0142, GLM-5.3 Flash $0.0015, Haiku 5.5 $0.0033 (Haiku measured in Experiment 1; the others estimated from their 50-idea calls: same prompt and reasoning, a tenth of the answer).

The judge is the expensive part. Scoring one idea costs about $0.0006, which is more than generating it with DeepSeek V4.1 Flash ($0.00011) or Haiku ($0.00017). So the bill grows with the number of ideas judged, almost whatever model writes them.

**Full plan (FULL_EXPERIMENT_PLAN.md)**

| Item | Size | Estimate |
| --- | --- | --- |
| 5-idea part: generation | 5,200 calls (Haiku 5.5, DeepSeek V4.1 Flash, Qwen3.8 Flash, GLM-5.3 Flash, DeepSeek V4 Pro; 13 needs, 4 representations, 20 replicates) | $29.45 |
| 5-idea part: Sonnet judge | 5,200 requests | $15.64 |
| 50-idea part: generation | 1,400 calls (Haiku 5.5, DeepSeek V4.1 Flash, Qwen3.8 Flash, GLM-5.3 Flash, DeepSeek V4 Pro; 7 needs, 4 representations, 10 calls) | $17.48 |
| 50-idea part: Sonnet judge | 14,280 requests | $42.95 |
| Judge re-test (Sonnet again) | 20% of the requests | $11.72 |
| Second judge (DeepSeek V4 Pro) | 15% of the requests | $12.70 |
| Contingency | 20% | $25.99 |
| **Total** | | **$155.94** |

Judging is 64% of it before contingency.

**Lean**

| Item | Size | Estimate |
| --- | --- | --- |
| 5-idea part: generation | 1,040 calls (Haiku 5.5, DeepSeek V4.1 Flash; 13 needs, 4 representations, 10 replicates) | $2.92 |
| 5-idea part: Sonnet judge | 1,040 requests | $3.13 |
| 50-idea part: generation | 400 calls (Haiku 5.5, DeepSeek V4.1 Flash; 5 needs, 4 representations, 10 calls) | $2.90 |
| 50-idea part: Sonnet judge | 4,080 requests | $12.27 |
| Judge re-test (Sonnet again) | 20% of the requests | $3.08 |
| Second judge (DeepSeek V4.1 Flash) | 15% of the requests | $0.38 |
| Contingency | 20% | $4.93 |
| **Total** | | **$29.61** |

Judging is 76% of it before contingency.

