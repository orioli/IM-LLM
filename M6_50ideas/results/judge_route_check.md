# Judge-route check

The same ideas, scored twice by `claude-sonnet-5-5` with the same prompt, effort and `max_tokens`: *old* = the paper's scores (Anthropic API, October 2026), *new* = OpenRouter Batch API pinned to Anthropic (the route used for the Chinese models). Replicate 1 of each representation of each run.

| Ideas written by | Requests | Ideas | Mean score old | new | Difference [95% CI] | Top ideas old | new | Agree on top | kappa | r | Mean abs. difference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Haiku 5.5 | 43 | 206 | 3.18 | 3.16 | -0.013 [-0.047, +0.022] | 4.9% | 3.9% | 93.2% | 0.19 | 0.88 | 0.13 |
| Opus 5.5 | 39 | 189 | 3.39 | 3.42 | +0.030 [-0.007, +0.068] | 16.9% | 16.4% | 91.0% | 0.68 | 0.85 | 0.16 |
| Fable 5.1 | 41 | 201 | 3.48 | 3.45 | -0.032 [-0.067, +0.001] | 16.9% | 15.4% | 92.5% | 0.72 | 0.87 | 0.14 |
| All | 123 | 596 | 3.35 | 3.34 | -0.006 [-0.026, +0.015] | 12.8% | 11.7% | 92.3% | 0.64 | 0.88 | 0.14 |

Mean difference per criterion, new − old, all ideas: relevance -0.003, novelty +0.008, feasibility -0.030, specificity +0.003.

**Verdict: route accepted.** Pooled mean shift -0.006 (limit ±0.1); pooled top-idea share 12.8% → 11.7% (limit ±3 points). The two ratings of an idea differ by 0.14 points on average: that is the judge's own run-to-run noise, present in the paper's scores as well.
