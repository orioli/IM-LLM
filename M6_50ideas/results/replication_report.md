# Replication report: verdicts per claim

Rules: `CHINESE_REPLICATION.md`, Sections 3 and 4. Top idea: score ≥ 4. Intervals: 95%, 2,000 bootstrap resamples of calls within representation. The Claude rows are the paper's own runs, read with the same rules.

## Verdicts

| Model | C1 full graph least efficient | C2 slice no better than no graph | C3 no graph arm beats no graph | C3 per dollar | Re-test of a contradiction (10 fresh calls per arm) |
| --- | --- | --- | --- | --- | --- |
| Haiku 5.5 (paper) | replicated | replicated | replicated | replicated | – |
| Opus 5.5 (paper) | same direction, inconclusive | replicated | replicated | replicated | – |
| Fable 5.1 (paper) | replicated | replicated | replicated | replicated | – |
| DeepSeek V4.1 Flash | same direction, inconclusive | CONTRADICTED | CONTRADICTED | CONTRADICTED | B − C NOT confirmed: fresh calls -3.9, all 20 calls +2.6 [-4.4, +9.2] |
| DeepSeek V4 Pro | same direction, inconclusive | replicated | replicated | replicated | – |
| Qwen3.8 Flash | not replicated (random slice is lowest) | replicated | replicated | replicated | – |

The first four columns read the first 10 calls per arm, the paper's design. A contradiction counts only if its re-test confirms it (last column).

## Runs

| Model | Calls | Parsed | Cut off | Ideas (per call) | Scored | Top ideas | Tokens per call: in | out | of which reasoning | Cost, list price | Billed | Served by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Haiku 5.5 | 40 | 40 | 0 | 2,080 (44–60) | 2,080 | 126 (6.1%) | 4,328 | 16,793 | - | $0.35 | - | Anthropic API |
| Opus 5.5 | 40 | 40 | 0 | 1,990 (49–52) | 1,985 | 270 (13.6%) | 4,328 | 15,784 | - | $13.32 | - | Anthropic API |
| Fable 5.1 | 40 | 40 | 0 | 2,021 (50–52) | 2,001 | 295 (14.7%) | 4,328 | 14,580 | - | $30.89 | - | Anthropic API |
| DeepSeek V4.1 Flash | 40 | 40 | 0 | 2,040 (49–67) | 2,040 | 109 (5.3%) | 3,200 | 13,375 | 3,564 | $0.24 | $0.23 | DeepInfra |
| DeepSeek V4 Pro | 40 | 40 | 0 | 1,981 (45–52) | 1,981 | 126 (6.4%) | 3,174 | 14,742 | 5,173 | $1.25 | $1.18 | Baidu |
| Qwen3.8 Flash | 40 | 40 | 0 | 2,000 (50–50) | 2,000 | 82 (4.1%) | 3,440 | 25,889 | 12,397 | $0.51 | $0.49 | Alibaba |

## Yield per representation

**Haiku 5.5**

| Representation | Calls | Ideas | Top ideas | Share top [95% CI] | Tokens per call (in + out) | Top ideas per 100k tokens [95% CI] | per US dollar [95% CI] |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A · Full graph | 10 | 517 | 28 | 5.4% [3.7–7.4] | 10,910 + 18,884 | **9.4** [6.2–13.2] | 265.8 [173.6–372.8] |
| B · Need slice | 10 | 525 | 42 | 8.0% [5.7–10.7] | 2,915 + 17,703 | **20.4** [14.5–27.7] | 459.4 [327.2–624.5] |
| R · Random slice | 10 | 513 | 19 | 3.7% [2.2–5.6] | 2,437 + 14,978 | **10.9** [6.7–16.7] | 245.7 [151.7–374.2] |
| C · No graph | 10 | 525 | 37 | 7.0% [5.5–8.6] | 1,050 + 15,606 | **22.2** [17.3–28.4] | 467.9 [363.7–601.1] |

| Contrast | Yield per 100k tokens: difference [95% CI] | ratio | first arm ahead | Per dollar: difference [95% CI] | Share of top ideas: difference [95% CI] |
| --- | --- | --- | --- | --- | --- |
| A − B | -11.0 [-19.0, -3.9] ✱ | 0.46× | 0% | -193.5 [-385.0, -22.7] ✱ | -2.6 pts [-5.8, +0.4] |
| A − C | -12.8 [-19.6, -6.7] ✱ | 0.42× | 0% | -202.0 [-356.3, -54.2] ✱ | -1.6 pts [-4.0, +0.8] |
| B − C | -1.8 [-10.4, +6.8] | 0.92× | 33% | -8.5 [-196.4, +183.8] | +1.0 pts [-1.9, +4.0] |
| R − C | -11.3 [-18.8, -4.2] ✱ | 0.49× | 0% | -222.2 [-387.8, -66.5] ✱ | -3.3 pts [-5.6, -1.0] ✱ |
| A − R | -1.5 [-7.8, +4.1] | 0.86× | 33% | +20.1 [-131.2, +160.9] | +1.7 pts [-0.7, +4.1] |

**Opus 5.5**

| Representation | Calls | Ideas | Top ideas | Share top [95% CI] | Tokens per call (in + out) | Top ideas per 100k tokens [95% CI] | per US dollar [95% CI] |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A · Full graph | 10 | 506 | 72 | 14.2% [11.6–17.1] | 10,910 + 16,423 | **26.3** [21.9–31.0] | 19.3 [16.1–22.6] |
| B · Need slice | 10 | 495 | 73 | 14.7% [11.7–17.9] | 2,915 + 15,368 | **39.9** [31.8–48.7] | 22.9 [18.2–28.0] |
| R · Random slice | 10 | 487 | 60 | 12.3% [9.8–14.9] | 2,437 + 13,698 | **37.2** [29.7–44.9] | 21.1 [16.8–25.5] |
| C · No graph | 10 | 497 | 65 | 13.1% [10.6–15.4] | 1,050 + 17,646 | **34.8** [26.9–43.5] | 18.2 [14.1–22.8] |

| Contrast | Yield per 100k tokens: difference [95% CI] | ratio | first arm ahead | Per dollar: difference [95% CI] | Share of top ideas: difference [95% CI] |
| --- | --- | --- | --- | --- | --- |
| A − B | -13.6 [-23.8, -4.2] ✱ | 0.66× | 0% | -3.5 [-9.6, +2.2] | -0.5 pts [-4.8, +3.7] |
| A − C | -8.4 [-18.1, +0.7] | 0.76× | 4% | +1.1 [-4.4, +6.6] | +1.2 pts [-2.3, +4.9] |
| B − C | +5.2 [-6.4, +17.0] | 1.15× | 80% | +4.7 [-1.7, +11.3] | +1.7 pts [-2.1, +5.7] |
| R − C | +2.4 [-9.3, +13.9] | 1.07× | 67% | +2.9 [-3.5, +9.2] | -0.8 pts [-4.3, +2.9] |
| A − R | -10.8 [-19.9, -2.0] ✱ | 0.71× | 1% | -1.8 [-7.3, +3.7] | +1.9 pts [-1.8, +5.7] |

**Fable 5.1**

| Representation | Calls | Ideas | Top ideas | Share top [95% CI] | Tokens per call (in + out) | Top ideas per 100k tokens [95% CI] | per US dollar [95% CI] |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A · Full graph | 10 | 501 | 78 | 15.6% [13.2–17.9] | 10,910 + 18,678 | **26.4** [22.0–30.4] | 7.5 [6.2–8.7] |
| B · Need slice | 10 | 507 | 87 | 17.2% [14.7–19.4] | 2,915 + 14,028 | **51.3** [44.6–58.1] | 11.9 [10.4–13.5] |
| R · Random slice | 10 | 498 | 58 | 11.6% [8.7–14.7] | 2,437 + 13,221 | **37.0** [27.4–46.1] | 8.5 [6.3–10.6] |
| C · No graph | 10 | 495 | 72 | 14.5% [12.6–16.7] | 1,050 + 12,393 | **53.6** [44.8–63.3] | 11.4 [9.5–13.6] |

| Contrast | Yield per 100k tokens: difference [95% CI] | ratio | first arm ahead | Per dollar: difference [95% CI] | Share of top ideas: difference [95% CI] |
| --- | --- | --- | --- | --- | --- |
| A − B | -25.0 [-32.6, -17.1] ✱ | 0.51× | 0% | -4.4 [-6.4, -2.4] ✱ | -1.6 pts [-4.8, +1.8] |
| A − C | -27.2 [-37.7, -17.6] ✱ | 0.49× | 0% | -3.9 [-6.3, -1.6] ✱ | +1.0 pts [-2.2, +4.2] |
| B − C | -2.2 [-13.9, +9.0] | 0.96× | 35% | +0.5 [-2.1, +3.0] | +2.6 pts [-0.6, +5.7] |
| R − C | -16.5 [-30.4, -3.7] ✱ | 0.69× | 1% | -3.0 [-6.1, -0.1] ✱ | -2.9 pts [-6.4, +0.7] |
| A − R | -10.7 [-20.9, -0.8] ✱ | 0.71× | 2% | -1.0 [-3.5, +1.5] | +3.9 pts [+0.0, +7.4] ✱ |

**DeepSeek V4.1 Flash**

| Representation | Calls | Ideas | Top ideas | Share top [95% CI] | Tokens per call (in + out) | Top ideas per 100k tokens [95% CI] | per US dollar [95% CI] |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A · Full graph | 10 | 501 | 27 | 5.4% [4.2–6.6] | 8,284 + 14,424 | **11.9** [9.2–14.9] | 374.1 [288.3–473.2] |
| B · Need slice | 10 | 511 | 37 | 7.2% [5.3–9.3] | 2,109 + 13,897 | **23.1** [16.9–30.9] | 603.4 [439.9–809.1] |
| R · Random slice | 10 | 528 | 28 | 5.3% [4.0–6.6] | 1,709 + 13,781 | **18.1** [13.3–23.5] | 464.5 [341.7–603.2] |
| C · No graph | 10 | 500 | 17 | 3.4% [2.4–4.6] | 699 + 11,398 | **14.1** [9.7–19.1] | 348.0 [239.9–473.2] |

| Contrast | Yield per 100k tokens: difference [95% CI] | ratio | first arm ahead | Per dollar: difference [95% CI] | Share of top ideas: difference [95% CI] |
| --- | --- | --- | --- | --- | --- |
| A − B | -11.2 [-19.3, -4.2] ✱ | 0.51× | 0% | -229.3 [-450.8, -40.2] ✱ | -1.9 pts [-4.2, +0.4] |
| A − C | -2.2 [-8.1, +3.3] | 0.85× | 23% | +26.1 [-131.5, +175.3] | +2.0 pts [+0.2, +3.6] ✱ |
| B − C | +9.1 [+1.0, +17.4] ✱ | 1.64× | 99% | +255.4 [+47.4, +473.1] ✱ | +3.8 pts [+1.6, +6.1] ✱ |
| R − C | +4.0 [-2.9, +11.0] | 1.29× | 87% | +116.5 [-59.1, +294.6] | +1.9 pts [+0.2, +3.6] ✱ |
| A − R | -6.2 [-12.2, -0.8] ✱ | 0.66× | 1% | -90.5 [-254.2, +60.9] | +0.1 pts [-1.7, +1.8] |

**DeepSeek V4 Pro**

| Representation | Calls | Ideas | Top ideas | Share top [95% CI] | Tokens per call (in + out) | Top ideas per 100k tokens [95% CI] | per US dollar [95% CI] |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A · Full graph | 10 | 499 | 31 | 6.2% [4.4–8.2] | 8,258 + 16,504 | **12.5** [8.3–17.7] | 81.5 [53.1–118.8] |
| B · Need slice | 10 | 500 | 38 | 7.6% [6.2–9.4] | 2,083 + 16,765 | **20.2** [15.8–25.8] | 110.1 [86.2–142.2] |
| R · Random slice | 10 | 483 | 31 | 6.4% [4.1–8.8] | 1,683 + 13,135 | **20.9** [12.5–30.9] | 114.5 [68.3–170.3] |
| C · No graph | 10 | 499 | 26 | 5.2% [3.4–6.9] | 673 + 12,561 | **19.6** [11.2–28.4] | 102.9 [58.6–149.2] |

| Contrast | Yield per 100k tokens: difference [95% CI] | ratio | first arm ahead | Per dollar: difference [95% CI] | Share of top ideas: difference [95% CI] |
| --- | --- | --- | --- | --- | --- |
| A − B | -7.6 [-14.6, -0.7] ✱ | 0.62× | 2% | -28.7 [-70.1, +15.6] | -1.4 pts [-3.8, +1.2] |
| A − C | -7.1 [-16.7, +2.7] | 0.64× | 7% | -21.4 [-75.2, +35.6] | +1.0 pts [-1.5, +3.7] |
| B − C | +0.5 [-9.4, +10.4] | 1.03× | 54% | +7.2 [-45.8, +59.6] | +2.4 pts [+0.2, +5.0] ✱ |
| R − C | +1.3 [-11.1, +13.8] | 1.06× | 58% | +11.6 [-55.6, +80.5] | +1.2 pts [-1.7, +4.2] |
| A − R | -8.4 [-18.7, +1.2] | 0.60× | 5% | -33.1 [-91.3, +25.4] | -0.2 pts [-3.1, +2.8] |

**Qwen3.8 Flash**

| Representation | Calls | Ideas | Top ideas | Share top [95% CI] | Tokens per call (in + out) | Top ideas per 100k tokens [95% CI] | per US dollar [95% CI] |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A · Full graph | 10 | 500 | 24 | 4.8% [3.6–6.6] | 8,922 + 29,966 | **6.2** [4.7–7.9] | 155.6 [120.8–197.4] |
| B · Need slice | 10 | 500 | 24 | 4.8% [2.2–7.8] | 2,259 + 28,779 | **7.7** [3.7–12.9] | 173.1 [82.7–288.3] |
| R · Random slice | 10 | 500 | 12 | 2.4% [1.0–4.0] | 1,823 + 25,646 | **4.4** [1.8–7.6] | 97.3 [39.8–169.9] |
| C · No graph | 10 | 500 | 22 | 4.4% [3.0–6.0] | 757 + 19,166 | **11.0** [7.7–14.4] | 241.2 [168.0–314.5] |

| Contrast | Yield per 100k tokens: difference [95% CI] | ratio | first arm ahead | Per dollar: difference [95% CI] | Share of top ideas: difference [95% CI] |
| --- | --- | --- | --- | --- | --- |
| A − B | -1.6 [-6.8, +2.9] | 0.80× | 28% | -17.5 [-135.9, +82.4] | +0.0 pts [-3.2, +3.0] |
| A − C | -4.9 [-8.7, -1.2] ✱ | 0.56× | 1% | -85.6 [-169.7, -2.2] ✱ | +0.4 pts [-1.8, +2.6] |
| B − C | -3.3 [-8.5, +2.4] | 0.70× | 13% | -68.1 [-183.3, +59.4] | +0.4 pts [-2.6, +3.6] |
| R − C | -6.7 [-11.0, -2.0] ✱ | 0.40× | 0% | -143.8 [-237.9, -41.6] ✱ | -2.0 pts [-4.2, +0.2] |
| A − R | +1.8 [-1.8, +4.8] | 1.41× | 85% | +58.3 [-23.8, +127.1] | +2.4 pts [+0.4, +4.6] ✱ |

✱ = the interval excludes 0.

## C4: does the full graph lower the share of top ideas?

| Model | Share top, full graph | no graph | Difference A − C [95% CI] |
| --- | --- | --- | --- |
| Haiku 5.5 | 5.4% | 7.0% | -1.6 pts [-4.0, +0.8] |
| Opus 5.5 | 14.2% | 13.1% | +1.2 pts [-2.3, +4.9] |
| Fable 5.1 | 15.6% | 14.5% | +1.0 pts [-2.2, +4.2] |
| DeepSeek V4.1 Flash | 5.4% | 3.4% | +2.0 pts [+0.2, +3.6] |
| DeepSeek V4 Pro | 6.2% | 5.2% | +1.0 pts [-1.5, +3.7] |
| Qwen3.8 Flash | 4.8% | 4.4% | +0.4 pts [-1.8, +2.6] |

## Confirmation runs

Every contradiction is re-tested with 10 fresh calls per arm (`CHINESE_REPLICATION.md`, Section 4). The verdict table above reads the first 10 calls only, as the paper's design does.

**DeepSeek V4.1 Flash**: arms re-tested: need slice, no graph.

| Calls | B · Need slice: top ideas / ideas, yield per 100k tokens [95% CI] | C · No graph: top ideas / ideas, yield per 100k tokens [95% CI] | B − C per 100k tokens [95% CI] | B − C per dollar [95% CI] |
| --- | --- | --- | --- | --- |
| first 10 calls (the run above) | 37 / 511, **23.1** [16.9–31.0] | 17 / 500, **14.1** [9.7–19.3] | +9.1 [+0.6, +18.4] ✱ | +255.4 [+38.1, +497.1] ✱ |
| fresh 10 calls (replicates 11–20) | 33 / 506, **20.4** [16.5–23.9] | 29 / 505, **24.3** [17.0–32.2] | -3.9 [-12.5, +3.9] | -69.8 [-285.3, +125.8] |
| all 20 calls | 70 / 1017, **21.8** [18.2–25.8] | 46 / 1005, **19.2** [14.2–24.8] | +2.6 [-4.4, +9.2] | +93.6 [-84.1, +260.6] |

B − C: the fresh calls point the OPPOSITE way (-3.9); over all 20 calls the interval includes 0 (+2.6 [-4.4, +9.2]). **The contradiction does NOT stand (not confirmed).**


## C5: net cost per top idea

- **generation only ($0):** cheapest is DeepSeek V4.1 Flash at $0.002 per top idea. Order: DeepSeek V4.1 Flash 0.002, Haiku 5.5 0.003, Qwen3.8 Flash 0.006, DeepSeek V4 Pro 0.010, Opus 5.5 0.049, Fable 5.1 0.105.
- **AI judge ($0.0012 per idea):** cheapest is Haiku 5.5 at $0.023 per top idea; indistinguishable from it: DeepSeek V4.1 Flash. Order: Haiku 5.5 0.023, DeepSeek V4.1 Flash 0.025, DeepSeek V4 Pro 0.029, Qwen3.8 Flash 0.035, Opus 5.5 0.058, Fable 5.1 0.113.
- **human ($0.50 per idea):** cheapest is Fable 5.1 at $3.50 per top idea; indistinguishable from it: Opus 5.5. Order: Fable 5.1 3.50, Opus 5.5 3.73, DeepSeek V4 Pro 7.87, Haiku 5.5 8.26, DeepSeek V4.1 Flash 9.36, Qwen3.8 Flash 12.20.

**C5: replicated.** No model is cheapest in every column, no large model beats every small one under AI screening, and no small model beats every large one under human screening.
