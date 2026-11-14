# Does the judge prefer its own family?

Ideas from the six 50-idea runs, scored by Sonnet 5.5 (the paper's judge) and again by `deepseek/deepseek-v4.1-flash` with the paper's judge prompt. Design and decision rule: `CHINESE_REPLICATION.md`, Section 10. 4,695 ideas rated by both judges. Gaps are in standard deviations of each judge's scores (Sonnet 0.48, DeepSeek 0.47 points). Intervals: 95%, 2,000 bootstrap resamples of requests within run.

| Run | Family | Ideas | Mean score, Sonnet | Mean score, DeepSeek | Top ideas, Sonnet (score ≥ 4.0) | Top ideas, DeepSeek (score ≥ 4.5, same overall share) |
| --- | --- | --- | --- | --- | --- | --- |
| Haiku 5.5 | Claude | 772 | 3.13 | 3.64 | 6.2% | 4.0% |
| Opus 5.5 | Claude | 788 | 3.39 | 3.89 | 12.6% | 9.9% |
| Fable 5.1 | Claude | 764 | 3.43 | 3.91 | 16.0% | 12.2% |
| DeepSeek V4.1 Flash | Chinese | 786 | 3.20 | 3.80 | 5.3% | 6.0% |
| DeepSeek V4 Pro | Chinese | 785 | 3.04 | 3.54 | 6.5% | 4.6% |
| Qwen3.8 Flash | Chinese | 800 | 3.14 | 3.69 | 4.9% | 5.4% |

| Gap (standard deviations) | Sonnet | DeepSeek judge | Share the DeepSeek judge keeps |
| --- | --- | --- | --- |
| Claude runs minus Chinese runs | +0.39 [+0.33, +0.45] | +0.29 [+0.23, +0.35] | 0.74 |
| Opus and Fable minus Haiku (inside Claude) | +0.58 [+0.50, +0.67] | +0.54 [+0.44, +0.64] | 0.93 |
| DeepSeek runs minus Qwen (inside Chinese) | -0.03 | -0.05 | |

- Family preference index (Sonnet's between-family gap minus the DeepSeek judge's): **+0.10** [+0.05, +0.15].
- Guard (share kept of the within-Claude gap minus share kept of the between-family gap): +0.18 [-0.02, +0.38].
- Does the DeepSeek judge favour DeepSeek-written ideas over Qwen's more than Sonnet does? Difference -0.01 [-0.10, +0.07].
- Claude-to-Chinese ratio of top-idea shares: 2.08 under Sonnet, 1.64 under the DeepSeek judge.
- Ranking of the six runs by mean score, Spearman correlation between the judges: 1.00.

**Verdict (pre-registered rule): ambiguous. The DeepSeek judge keeps 93% of the gap inside Claude and 74% of the gap between the families, but the difference has an interval that includes 0, so a judge that separates ideas less well in general can't be ruled out.**
