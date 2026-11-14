# Second judge: deepseek/deepseek-v4-pro-0813 on the haiku run

2,073 of the run's 2,080 ideas rated by both judges, with the same prompt. First judge: `claude-sonnet-5-5` (the paper's scores). Second judge: `deepseek/deepseek-v4-pro-0813`.

## Agreement

- Mean score: first judge 3.13, second judge 3.69. Correlation of the two scores: r = 0.65.
- Mean per criterion (first / second): relevance 2.97 / 3.84, novelty 2.87 / 3.16, feasibility 3.53 / 3.81, specificity 3.17 / 3.97.
- Second judge, score ≥ 4.0: 830 top ideas (40.0%; first judge 126, 6.1%); 105 are top for both; agreement 64.0%, kappa 0.13.
- Second judge, matched cut-off (score ≥ 4.5): 167 top ideas (8.1%; first judge 126, 6.1%); 34 are top for both; agreement 89.1%, kappa 0.17.

## Yield per representation under each judge

Top ideas per 100k tokens [95% CI], and contrasts (difference [95% CI]; ✱ = interval excludes 0).

| Top ideas counted by | A full graph | B slice | R random | C no graph | A − B | A − C | B − C |
| --- | --- | --- | --- | --- | --- | --- | --- |
| First judge (Sonnet 5.5), score ≥ 4.0 | 9.4 [6.1–13.2] (n=28) | 20.4 [14.7–27.7] (n=42) | 10.9 [6.7–16.8] (n=19) | 22.2 [17.0–28.1] (n=37) | -11.0 [-18.8, -4.4] ✱ | -12.8 [-19.5, -6.3] ✱ | -1.8 [-10.1, +6.7] |
| Second judge, score ≥ 4.0 | 66.5 [58.4–74.4] (n=198) | 112.0 [103.8–120.5] (n=231) | 102.2 [85.5–118.7] (n=178) | 133.9 [121.4–148.4] (n=223) | -45.6 [-57.6, -34.3] ✱ | -67.4 [-84.1, -52.3] ✱ | -21.8 [-38.2, -6.5] ✱ |
| Second judge, matched cut-off (score ≥ 4.5) | 17.8 [13.7–22.8] (n=53) | 20.9 [16.0–26.3] (n=43) | 19.5 [12.6–28.5] (n=34) | 22.2 [16.3–29.4] (n=37) | -3.1 [-10.1, +4.0] | -4.4 [-12.7, +3.7] | -1.4 [-10.1, +7.1] |

## Verdict

- Second judge, score ≥ 4.0: the ranking is **the same as under the first judge** (the full graph is below both the slice and no graph, and the slice does not beat no graph).
- Second judge, matched cut-off (score ≥ 4.5): the ranking is **the same as under the first judge** (the full graph is below both the slice and no graph, and the slice does not beat no graph).
