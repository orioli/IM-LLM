# What the runs can say, and what a full experiment needs

No API calls. Yield = top ideas (score ≥ 4.0) per token. Ratios are of yields; 1.00 = no difference. Intervals: 95%, 2,000 bootstrap resamples of calls within arm.

## 1. The six 50-idea runs together (M6)

**Slice / no graph** (B / C)

| Model | Calls per arm | Ratio [95% CI] | SE of log ratio |
| --- | --- | --- | --- |
| Haiku 5.5 | 10, 10 | 0.92 [0.59–1.37] | 0.21 |
| Opus 5.5 | 10, 10 | 1.15 [0.83–1.57] | 0.16 |
| Fable 5.1 | 10, 10 | 0.96 [0.77–1.20] | 0.11 |
| DeepSeek V4.1 Flash | 20, 20 | 1.14 [0.84–1.59] | 0.16 |
| DeepSeek V4 Pro | 10, 10 | 1.03 [0.65–1.84] | 0.27 |
| Qwen3.8 Flash | 10, 10 | 0.70 [0.32–1.27] | 0.35 |
| **All models, pooled** | 6 models | **1.01 [0.88–1.16]** | heterogeneity I² = 0% |
| **Claude models (the paper), pooled** | 3 models | **1.00 [0.85–1.18]** | heterogeneity I² = 0% |
| **Chinese models, pooled** | 3 models | **1.04 [0.81–1.34]** | heterogeneity I² = 0% |

**Full graph / no graph** (A / C)

| Model | Calls per arm | Ratio [95% CI] | SE of log ratio |
| --- | --- | --- | --- |
| Haiku 5.5 | 10, 10 | 0.42 [0.26–0.65] | 0.23 |
| Opus 5.5 | 10, 10 | 0.76 [0.55–1.02] | 0.15 |
| Fable 5.1 | 10, 10 | 0.49 [0.38–0.62] | 0.12 |
| DeepSeek V4.1 Flash | 10, 20 | 0.62 [0.42–0.90] | 0.19 |
| DeepSeek V4 Pro | 10, 10 | 0.64 [0.35–1.23] | 0.31 |
| Qwen3.8 Flash | 10, 10 | 0.56 [0.38–0.85] | 0.21 |
| **All models, pooled** | 6 models | **0.57 [0.48–0.68]** | heterogeneity I² = 27% |
| **Claude models (the paper), pooled** | 3 models | **0.55 [0.40–0.77]** | heterogeneity I² = 69% |
| **Chinese models, pooled** | 3 models | **0.60 [0.47–0.77]** | heterogeneity I² = 0% |

**Full graph / slice** (A / B)

| Model | Calls per arm | Ratio [95% CI] | SE of log ratio |
| --- | --- | --- | --- |
| Haiku 5.5 | 10, 10 | 0.46 [0.28–0.76] | 0.25 |
| Opus 5.5 | 10, 10 | 0.66 [0.49–0.88] | 0.15 |
| Fable 5.1 | 10, 10 | 0.51 [0.41–0.63] | 0.11 |
| DeepSeek V4.1 Flash | 10, 20 | 0.55 [0.39–0.74] | 0.16 |
| DeepSeek V4 Pro | 10, 10 | 0.62 [0.39–0.98] | 0.23 |
| Qwen3.8 Flash | 10, 10 | 0.80 [0.44–1.65] | 0.34 |
| **All models, pooled** | 6 models | **0.56 [0.49–0.64]** | heterogeneity I² = 0% |
| **Claude models (the paper), pooled** | 3 models | **0.55 [0.46–0.66]** | heterogeneity I² = 18% |
| **Chinese models, pooled** | 3 models | **0.59 [0.47–0.75]** | heterogeneity I² = 0% |

**Random slice / no graph** (R / C)

| Model | Calls per arm | Ratio [95% CI] | SE of log ratio |
| --- | --- | --- | --- |
| Haiku 5.5 | 10, 10 | 0.49 [0.28–0.82] | 0.27 |
| Opus 5.5 | 10, 10 | 1.07 [0.77–1.47] | 0.17 |
| Fable 5.1 | 10, 10 | 0.69 [0.49–0.94] | 0.16 |
| DeepSeek V4.1 Flash | 10, 20 | 0.94 [0.65–1.42] | 0.20 |
| DeepSeek V4 Pro | 10, 10 | 1.06 [0.53–1.98] | 0.33 |
| Qwen3.8 Flash | 10, 10 | 0.40 [0.15–0.75] | 0.40 |
| **All models, pooled** | 6 models | **0.77 [0.58–1.02]** | heterogeneity I² = 57% |
| **Claude models (the paper), pooled** | 3 models | **0.74 [0.49–1.12]** | heterogeneity I² = 72% |
| **Chinese models, pooled** | 3 models | **0.79 [0.47–1.31]** | heterogeneity I² = 55% |

## 2. Power of the 50-idea design (M6)

Slice against no graph (B / C), the comparison the paper's "no better than no graph" rests on. "Smallest detectable ratio" is what a 10-call arm finds with 80% power; a true difference smaller than that will usually come out as "indistinguishable".

| Model | SE of log ratio at 10 calls per arm | Smallest detectable ratio at 10 calls | Calls per arm to detect 1.5× | to detect 1.25× | to show equivalence within ±25% | within ±20% |
| --- | --- | --- | --- | --- | --- | --- |
| Haiku 5.5 | 0.21 | 1.82× | 22 | 72 | 78 | 117 |
| Opus 5.5 | 0.16 | 1.57× | 12 | 41 | 45 | 67 |
| Fable 5.1 | 0.11 | 1.37× | 6 | 20 | 21 | 32 |
| DeepSeek V4.1 Flash | 0.23 | 1.90× | 25 | 83 | 91 | 136 |
| DeepSeek V4 Pro | 0.27 | 2.13× | 35 | 115 | 126 | 188 |
| Qwen3.8 Flash | 0.35 | 2.70× | 60 | 198 | 216 | 324 |
| **Typical (median SE 0.23)** | 0.23 | **1.90×** | **25** | **83** | **91** | **136** |

Calls needed fall in proportion when several needs or models are pooled: with *m* needs (or models) analysed together, divide by *m*, provided the effect is the same in each.

## 3. Power of the 5-idea design (Experiment 1, the paper's calls, high effort)

| Comparison | Calls per arm | Ratio [95% CI] | Smallest detectable ratio now | Replicates per need (13 needs) to detect 1.5× | 1.25× | equivalence within ±25% |
| --- | --- | --- | --- | --- | --- | --- |
| slice / no graph (B / C) | 64, 65 | 0.94 [0.71–1.23] | 1.48× | 5 | 16 | 17 |
| full graph / no graph (A / C) | 65, 65 | 0.48 [0.36–0.65] | 1.53× | 6 | 18 | 20 |
| full graph / slice (A / B) | 65, 64 | 0.52 [0.39–0.68] | 1.50× | 5 | 17 | 18 |
| random slice / no graph (R / C) | 65, 65 | 0.65 [0.47–0.88] | 1.57× | 7 | 21 | 23 |

The paper ran 5 replicates per need. Replicates above are per need and arm, with all 13 needs.

## 4. Judge noise

From 596 ideas scored twice by the same judge (`results/judge_route_check.md`): the two scores correlate at r = 0.88, so one pass has a reliability of about 0.88; the mean of two passes would have 0.93, of three 0.96. An idea scored top once is top again 66% of the time. 27% of ideas score 3.75 or 4.0, one step from the cut-off on either side, which is where a single pass flips. The intervals in Parts 1 to 3 already contain this noise (it is part of the spread between calls), but they do not show how much of the spread a second judge pass would remove.

