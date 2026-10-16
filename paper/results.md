# RQ1 results: how much graph context does LLM brainstorming need?

Full run, 2026-10-15. Generation model `claude-haiku-5-5`, judge model `claude-sonnet-5-5`.

**Headline.** The aim of brainstorming is the rare great idea, not a good average, so the main measure here is the **top tail**: how often an arm produces an idea in the top ~12% of all ideas, and what each such idea costs.

- **A relevant slice of the graph finds top ideas fastest per token.** Counted against tokens spent, top ideas accumulate in a straight line for every arm, so each arm has a yield: top ideas per 100k tokens. The need slice (B) at medium effort yields 8.8, about three times the full graph (A) at any effort (2.6–3.2). B's top-idea rate is also the highest at equal effort (15% at medium and high, against 10% for no graph and for a random slice of the same size).
- **The full graph (A) writes the best idea *sets* but does not find more top ideas.** Judged as whole sets, A beats B 64% of the time and no graph 74% of the time. But its top-idea rate is no higher than B's, and its yield is about 3 top ideas per 100k tokens at every effort, half or less of B's: its advantage is the specificity of an average set, not more standout ideas.
- **A graph helps, clearly so when it is the full graph.** A beats C on whole sets (74%, p < 0.001); B beats C less clearly (62%, p = 0.053) but has a higher top-idea rate (14.7% vs 10.2%).
- **Relevance vs size is only partly settled.** In the top tail, the need slice beats the size-matched random slice (top-idea rate 14.7% vs 9.8%; yield 5.9 vs 4.1 per 100k tokens; the slice's slope is higher in 99% of paired bootstrap draws). Judged as whole sets, the two cannot be told apart (B over R 54%, p = 0.55). What a relevant slice adds shows up in the best ideas, not in the average set.
- **The efficiency gain holds need by need, and is largest for small slices.** The slice is more efficient than the full graph on 10 of 13 market needs (sign test p = 0.039), and no graph beats a random slice on 10 of 12. The slice's lead is 3–5× for needs whose slice has 15–28 nodes, and 1–2× for those with 45–51 nodes (exploratory).
- **Persona prompting did not raise efficiency (exploratory follow-up).** On three needs, neither a lateral-thinker nor a patent-focused persona beat the plain innovation engineer per token (6.3 top ideas per 100k tokens; patent persona 5.5, lateral thinker 4.3, lower than the engineer's in > 99.9% of bootstrap draws); the lateral thinker was the least efficient, especially without a graph. The need slice helped every persona; whether it helps some personas more than others could not be resolved.
- **Thinking effort is the strongest lever on quality, but not on yield.** High beats low in about 93% of set comparisons, and xhigh produces the highest top-idea rates of all (19–21%). But each call costs proportionally more, so yield does not rise with effort: for the full graph it stays at about 3 per 100k tokens from low to xhigh, and for the slice it peaks at medium (8.8) and falls at high (5.9) and xhigh (3.1).
- **No graph is surprisingly efficient.** Its calls are the cheapest, so despite a low top-idea rate its yield (6.4) beats the random slice (4.1) and the full graph (3.1), and is close to the slice at high effort (5.9).

## Setup

| Item | Value |
| --- | --- |
| Product graph | `microwave_base_graph.yaml`: 123 nodes, 246 edges |
| Target needs | 13: M1, M3, M4, M5, M6, M7, M8, M11, M12, M13, M14, M16, M17 (M2, M9, M10, M15 excluded: no functions address them, so their slice is empty) |
| Conditions | **A** = full graph · **B** = vertical slice of the target need (functions, components, technologies, fields, linked constraints and actors) · **R** = random slice with the same number of nodes per layer as B · **C** = no graph (product description and target need only) |
| Thinking effort | A and B: low, medium, high on all 13 needs, xhigh on 6 needs (M1, M4, M6, M8, M13, M17) · R and C: high on all 13 needs |
| Replicates | 5 per cell |
| Generation calls | 580: A and B 450 (13 needs × 2 conditions × 3 efforts × 5 reps, plus 6 needs × 2 × 5 at xhigh); R and C 130 (13 × 2 × 5) |
| Prompt | `template_prompt.txt`: 5 radical ideas for the target need, operator SUBSTITUTE, worked example (door holes + lamp → webcam / transparent casing), JSON output |
| `max_tokens` | 48,000 (64,000 for xhigh); no call was truncated |
| Sampling | model defaults (Haiku 5.5 accepts no temperature setting) |
| Pairwise judging | A vs B at low and high effort; B vs R, B vs C, A vs C at high effort; effort steps within A and B; B-high vs A-low. Blind comparison of two idea sets for the same need and replicate; no condition labels or node IDs shown; each pair judged in both presentation orders and the two verdicts combined (agreeing verdicts = a win, split = a tie); scores 1–5 on relevance, novelty, feasibility, specificity, diversity |
| Individual scoring | every idea scored on its own, blind, 1–5 on relevance, novelty, feasibility, specificity; idea score = mean of the four (all 2,892 ideas) |
| Statistics | pairwise: per pair (65 pairs per comparison, 30 for xhigh), ties count half, Wilson 95% CI, exact sign test · tail: rates averaged over needs (each need weighs the same), 95% CI by resampling calls within each need (2,000 resamples) |

## Cost and validity

Chart 1 (`1_tokens_per_call.png`) shows tokens per call by condition and effort; chart 5 (`5_context_ladder.png`) sets the four representations side by side at high effort, input tokens against mean idea score.

Means per call.

| Condition | Effort | Calls | Parse rate | Input tokens | Output tokens | Total tokens | Words per idea |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | low | 65 | 100% | 10,912 | 3,331 | 14,243 | 91 |
| A | medium | 65 | 100% | 10,912 | 5,295 | 16,208 | 99 |
| A | high | 65 | 100% | 10,912 | 11,163 | 22,076 | 108 |
| A | xhigh | 30 | 100% | 10,912 | 28,346 | 39,258 | 117 |
| B | low | 65 | 100% | 3,778 | 2,849 | 6,627 | 89 |
| B | medium | 65 | 100% | 3,778 | 4,772 | 8,550 | 98 |
| B | high | 65 | 98.5% | 3,778 | 8,628 | 12,407 | 100 |
| B | xhigh | 30 | 100% | 4,135 | 25,885 | 30,020 | 117 |
| R | high | 65 | 100% | 3,143 | 8,778 | 11,921 | 98 |
| C | high | 65 | 100% | 1,055 | 6,939 | 7,994 | 106 |

xhigh was run on 6 of the 13 needs; those needs have larger slices on average, which is why B's xhigh input is higher.

- **Input:** the slice cuts input tokens by 65% on average (slices range from 10 to 51 nodes, 8–42% of the graph). R matches B's node counts per layer but uses 17% fewer input tokens, because random nodes have shorter labels and fewer linking edges; the size match is close but not exact.
- **Total:** the slice saves 53% of total tokens at low effort, 47% at medium, 44% at high and 24% at xhigh. Output grows steeply with effort and soon dominates the bill, so the input saving matters less and less.
- **Output grows with context:** at high effort, output is 6.9k tokens with no graph, 8.6–8.8k with a slice (B or R) and 11.2k with the full graph. More context makes the model think and write more, a cost beyond the prompt itself.
- **Output by effort:** each step up costs more than the last: +1,900–2,000 tokens from low to medium, +3,900–5,900 from medium to high, about +17,000 from high to xhigh.
- **Validity:** 579 of 580 calls returned valid JSON with 5 ideas; none hit the token limit.

## How the ideas use the graph

| Condition | Effort | Anchors outside the need's own slice | Anchors to nodes not in the graph | Ideas repeating the worked example (of 5) | New nodes per idea |
| --- | --- | --- | --- | --- | --- |
| A | low | 53% | 0% | 0.95 | 2.8 |
| A | medium | 49% | 0% | 0.69 | 3.1 |
| A | high | 48% | 0% | 0.54 | 3.4 |
| A | xhigh | 40% | 0% | 0.33 | 3.6 |
| B | low | 0% | 0% | 0.86 | 2.9 |
| B | medium | 0% | 0% | 0.48 | 3.1 |
| B | high | 0% | 0% | 0.55 | 3.3 |
| B | xhigh | 0% | 0% | 0.40 | 3.9 |
| R | high | 42% | 0% | 0.51 | 3.3 |
| C | high | — | 48% | 0.37 | 4.4 |

- With the full graph, about half of all anchors lie outside the target need's slice: A uses its extra context to reach across the product.
- With a random slice, 42% of anchors fall outside the need's slice, because most of what R shows is unrelated to the need.
- With no graph, the model invents node IDs for half of its anchors and adds more new nodes per idea (4.4): it builds its own picture of the product instead of working on the given one.
- Repetition of the worked example falls with effort, and is lowest with no graph.

## The top tail: which arm finds the great ideas?

A **top idea** scores ≥ 4.0 on the individual blind scoring. Scores move in 0.25 steps, so an exact top 10% does not exist: ≥ 4.0 keeps the top 12.3% of all ideas (355 of 2,892), ≥ 4.25 the top 2.4% (68). Needs differ a lot in how easy a top idea is (29% of M14's ideas reach 4.0, 3% of M11's), so every rate is the mean of per-need rates.

### Top-idea rate (score ≥ 4.0)

Chart 6 (`6_top_idea_rate.png`).

| Arm | Needs | Top ideas / ideas | Top-idea rate | 95% CI | Calls with ≥ 1 top idea | Tokens per call | Tokens per top idea |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C · high | 13 | 33 / 325 | 10.2% | 8.3–12.3% | 48% | 7,994 | 15,746 |
| R · high | 13 | 32 / 325 | 9.8% | 7.7–12.3% | 45% | 11,921 | 24,215 |
| B · low | 13 | 30 / 323 | 9.3% | 7.4–11.4% | 37% | 6,627 | 14,359 |
| B · medium | 13 | 49 / 325 | 15.1% | 11.7–18.5% | 52% | 8,550 | **11,342** |
| B · high | 13 | 47 / 320 | 14.7% | 11.9–17.5% | 56% | 12,384 | 16,838 |
| B · xhigh | 6 | 28 / 150 | 18.7% | 14.0–23.3% | 73% | 30,020 | 32,164 |
| A · low | 13 | 27 / 324 | 8.3% | 6.2–10.5% | 37% | 14,243 | 34,289 |
| A · medium | 13 | 34 / 325 | 10.5% | 8.0–13.2% | 45% | 16,208 | 30,985 |
| A · high | 13 | 44 / 325 | 13.5% | 10.5–16.3% | 57% | 22,076 | 32,612 |
| A · xhigh | 6 | 31 / 150 | 20.7% | 16.7–24.7% | 80% | 39,258 | 37,991 |

- **Relevance vs size (H3):** at the same effort and nearly the same size, the need slice yields top ideas at 14.7% against 9.8% for the random slice; the confidence intervals just touch. The whole-set judging does not confirm this (see below).
- **Graph vs none (H4):** a relevant slice yields more top ideas than no graph (14.7% vs 10.2%); a random slice does not (9.8%). The full graph is in between (13.5%).
- **Full graph vs slice:** at every effort, B's top-idea rate is equal to or higher than A's, at about half the tokens per top idea.
- **Effort:** top-idea rates rise with effort for both A and B, with the largest rates at xhigh. But xhigh costs 2–3× the tokens per top idea of medium or high.
- **Cheapest top ideas:** B at medium effort (11k tokens each), then B at low (14k), C (16k) and B at high (17k). A costs 31–38k at every effort.

### Yield: top ideas per 100k tokens

The top-idea rate says how good an arm's ideas are; the yield says how fast it finds top ideas for the money. Counting top ideas against the tokens spent on an arm's calls (taken in replicate order, cycling through the needs) gives a running count that grows in a straight line for every arm (chart 8). The **yield** is the slope of that line: all of the arm's top ideas divided by all its tokens, per 100k tokens, with a 95% CI from 2,000 resamples of calls within each need. Unlike a probability, a count does not level off, so arms are compared directly by slope.

| Arm | Top ideas | Tokens spent | Yield (top ideas per 100k tokens) | 95% CI |
| --- | --- | --- | --- | --- |
| B · medium | 49 | 0.56M | **8.8** | 7.0–10.7 |
| B · low | 30 | 0.43M | 7.0 | 5.4–8.4 |
| C · high | 33 | 0.52M | 6.4 | 5.1–7.7 |
| B · high | 47 | 0.79M | 5.9 | 4.9–7.0 |
| R · high | 32 | 0.77M | 4.1 | 3.1–5.2 |
| A · medium | 34 | 1.05M | 3.2 | 2.5–4.1 |
| B · xhigh (6 needs) | 28 | 0.90M | 3.1 | 2.4–3.9 |
| A · high | 44 | 1.43M | 3.1 | 2.4–3.7 |
| A · low | 27 | 0.93M | 2.9 | 2.2–3.7 |
| A · xhigh (6 needs) | 31 | 1.18M | 2.6 | 2.1–3.1 |

- **The need slice is the most efficient representation at every effort up to high.** B at medium yields 8.8 top ideas per 100k tokens, 2.8 times A at medium (3.2); at high, 5.9 against 3.1. The intervals do not overlap.
- **The full graph's yield is flat across effort** (2.6–3.2). More thinking raises A's top-idea rate from 8% to 21%, but the cost per call rises in step, so the full graph buys better calls, not more top ideas per token.
- **The slice's yield peaks at medium effort.** From medium to high, B's top-idea rate barely changes (15.1% to 14.7%) while the tokens per call rise by 45%; xhigh raises the rate to 18.7% but at 3.5 times the tokens.
- **Relevance vs size:** at high effort, B yields 5.9 and R 4.1; the 95% intervals just touch (4.9–7.0 against 3.1–5.2), but pairing the two arms' bootstrap draws, B's slope is the higher in 99% of them (chart 8b; chart 8c, `8c_yield_spread_annotated.png`, marks the no-graph slope as a reference line), equivalent to a one-sided bootstrap p ≈ 0.01. R costs about as much per call as B, so the difference is in what the calls find.
- **How far apart the slopes are** (chart 8b, chance that each arm's slope beats the next lower arm's): B·medium over B·low 0.93; B·low over C 0.74; C over B·high 0.69; B·high over R 0.99; R over A·medium 0.91; among the full-graph arms and B·xhigh 0.53–0.73. Four tiers: B at medium (8.8); B at low and high with C (5.9–7.0); R (4.1); all full-graph arms and B·xhigh (2.6–3.2).
- **No graph:** C's low top-idea rate (10.2%) is offset by its cheap calls (8.0k tokens), giving a yield of 6.4, above R and A and within the interval of B at high effort. Its weakness is coverage: with no graph, M1 produced no top idea in 5 calls (A and B: 2–3).
- **At the stricter threshold (≥ 4.25)** the order is similar but the counts are small (2–11 per arm): B·medium 1.8 per 100k tokens (1.1–2.7), A·medium 1.0, B·low 0.9, B·high 0.9, A·xhigh 0.85, B·xhigh 0.8, C 0.8, A·high 0.7, R 0.4, A·low 0.2.
- **On the 6 xhigh needs only:** B·medium 9.0, B·low 7.4, B·high 6.4, C 6.1, R 4.2, A·low 3.3, B·xhigh 3.1, A·medium 2.9, A·high 2.8, A·xhigh 2.6. The ranking is the same as on all needs.

### Yield per market need

To check that the yield ranking is not driven by a few easy needs, yields were computed for each market need separately (5 calls per arm and need), and arms were compared by the number of needs on which each is more efficient (exact two-sided sign test, ties excluded; `yield_per_market_need.xlsx`).

Yield per need at high effort (top ideas per 100k tokens; B's slice size in nodes):

| Need | Slice nodes | B need slice | C no graph | R random slice | A full graph | B ÷ A |
| --- | --- | --- | --- | --- | --- | --- |
| M11 | 10 | 2.1 | 0.0 | 2.1 | 1.7 | 1.2× |
| M14 | 15 | 17.9 | 15.5 | 10.6 | 8.2 | 2.2× |
| M16 | 15 | 9.2 | 5.1 | 2.5 | 3.0 | 3.1× |
| M8 | 25 | 13.4 | 10.1 | 7.6 | 2.9 | 4.7× |
| M6 | 28 | 11.8 | 7.4 | 5.8 | 3.4 | 3.5× |
| M7 | 45 | 5.5 | 12.8 | 5.8 | 2.8 | 2.0× |
| M13 | 45 | 6.0 | 5.0 | 3.1 | 2.7 | 2.2× |
| M3 | 47 | 4.1 | 10.0 | 4.8 | 4.5 | 0.9× |
| M12 | 47 | 3.1 | 2.6 | 1.6 | 2.8 | 1.1× |
| M1 | 48 | 2.6 | 0.0 | 0.0 | 3.2 | 0.8× |
| M4 | 51 | 4.3 | 6.8 | 4.1 | 1.9 | 2.3× |
| M5 | 51 | 0.0 | 0.0 | 1.5 | 0.0 | — |
| M17 | 51 | 2.9 | 7.9 | 6.1 | 2.8 | 1.0× |

| Comparison | First arm more efficient | Second more efficient | Equal | Sign test p |
| --- | --- | --- | --- | --- |
| B vs A, high effort | 10 needs | 2 | 1 | **0.039** |
| B vs A, medium effort | 10 | 3 | 0 | 0.092 |
| C vs R (no graph vs random slice) | 10 | 2 | 1 | **0.039** |
| R vs A | 10 | 3 | 0 | 0.092 |
| C vs A | 9 | 3 | 1 | 0.146 |
| B vs R | 9 | 4 | 0 | 0.267 |
| B vs C | 8 | 4 | 1 | 0.388 |

- **The slice's efficiency advantage over the full graph holds need by need:** B is more efficient on 10 of 13 needs at high effort (p = 0.039) and at medium effort (p = 0.09). The full graph is ahead only on M1 and M3, by small margins.
- **No graph is more efficient than a random slice on 10 of 12 decided needs (p = 0.039).** Showing the model structure that is not about the problem costs more per top idea than showing it nothing.
- **Relevance vs size (B vs R) is not robust need by need** (9 of 13, p = 0.27), in line with the pooled yield (intervals touching) and the set judging (no difference).
- **The advantage depends on slice size (exploratory).** B's lead over A is largest where the slice is small: 3–5× for M6, M8 and M16 (15–28 nodes), against 0.8–2.3× for the needs with 45–51 nodes (chart 9). Across needs, the log of B's yield ratio over A correlates with slice size at r = −0.46 at high effort (n = 12, p ≈ 0.13) and r = −0.61 at medium effort (n = 12, p ≈ 0.04). M11, the smallest slice (10 nodes), is an exception at 1.2×; it is also one of the two hardest needs for every arm. A smaller slice saves more tokens and is more focused; with 13 needs and 5 calls each this is a pattern to test, not an established result.
- **Single needs are noisy:** each value rests on 5 calls and 0–10 top ideas.

### Chance of at least one top idea for a given budget (secondary)

Chart 7 (`7_chance_vs_budget.png`).

This measure answers a practical question, how likely one budget is to produce at least one top idea, but every arm's chance approaches 100% as the budget grows, so it compresses differences at large budgets and can suggest that spending alone guarantees a top idea. The yield above is the better basis for comparing arms. For a token budget spent on whole calls of one arm, the chance that at least one idea scores ≥ 4.0, averaged over needs. Within a need, calls are treated as independent: k calls succeed with 1 − (1 − p)^k, where p is the need's share of calls with a top idea, estimated as (hits + ½) / (calls + 1) because 5 calls per need often give exactly 0 or 1.

| Arm | 25k tokens | 50k tokens | 100k tokens |
| --- | --- | --- | --- |
| C · high | 74% (3 calls) | 84% (6) | 92% (12) |
| R · high | 65% (2) | 82% (4) | 93% (8) |
| B · low | 64% (3) | 81% (7) | 91% (15) |
| B · medium | 70% (2) | **89%** (5) | **96%** (11) |
| B · high | 74% (2) | 88% (4) | 95% (8) |
| B · xhigh (6 needs) | — (0) | 69% (1) | 94% (3) |
| A · low | 39% (1) | 67% (3) | 86% (7) |
| A · medium | 46% (1) | 79% (3) | 94% (6) |
| A · high | 56% (1) | 76% (2) | 90% (4) |
| A · xhigh (6 needs) | — (0) | 75% (1) | 93% (2) |

- **B at medium and high effort lead at 50k and 100k tokens,** and B-medium is at or near the top at every budget.
- **No graph is a good choice for small budgets** because its calls are cheapest, but it rises more slowly at large budgets because of the needs where it finds nothing (M1); M5 and M11 are hard for every arm.
- **The full graph trails at every budget:** its calls are expensive and its top-idea rate is no higher than B's.

### Stricter threshold and matched needs

- **Score ≥ 4.25 (top 2.4%):** same direction, too few hits per arm (2–11) to separate arms. A·xhigh 6.7% and B·xhigh 4.7% (6 needs), A·medium 3.4%, B·medium 3.1%, A·high 3.1%, B·high 2.2%, C 1.2%, B·low 1.2%, R 1.0%, A·low 0.6%. Tokens per top idea are lowest for B·medium (56k) and highest for R (about 260k) and A·low (463k); yields are listed in the yield section above.
- **Only the 6 xhigh needs** (`--match-needs`): B·medium and B·high 16.7%, B·xhigh 18.7%, A·high 12.7%, A·xhigh 20.7%, R 10.7%, C 10.0%. On equal needs, B gains little from xhigh over medium or high, while A gains a lot; A needs the extra thinking to make use of its larger context.

## Mean idea quality (individual scoring)

Chart 4 (`4_cost_vs_quality.png`) plots tokens per call against mean idea score for the full-graph and need-slice arms.

Need-balanced mean idea score (1–5) and mean criterion scores:

| Arm | Mean score | Relevance | Novelty | Feasibility | Specificity |
| --- | --- | --- | --- | --- | --- |
| C · high | 3.44 | 3.49 | 3.29 | 3.21 | 3.78 |
| R · high | 3.46 | 3.44 | 3.16 | 3.37 | 3.88 |
| B · low | 3.28 | 3.38 | 3.01 | 3.26 | 3.50 |
| B · medium | 3.47 | 3.53 | 3.20 | 3.36 | 3.82 |
| B · high | 3.53 | 3.60 | 3.25 | 3.37 | 3.92 |
| B · xhigh (6 needs) | 3.54 | 3.47 | 3.38 | 3.29 | 4.03 |
| A · low | 3.30 | 3.39 | 3.04 | 3.27 | 3.52 |
| A · medium | 3.44 | 3.42 | 3.10 | 3.42 | 3.83 |
| A · high | 3.50 | 3.46 | 3.20 | 3.45 | 3.89 |
| A · xhigh (6 needs) | 3.52 | 3.42 | 3.33 | 3.29 | 4.03 |

- Mean differences between arms are small (0.1–0.25 points) and hide the differences in the tail; this is why the tail is the main measure.
- At high effort, mean scores order C 3.44 < R 3.46 < A 3.50 < B 3.53, the same ranking as the top-idea rates except that C and R, nearly tied on both measures, swap places.
- **No graph gives the most novel but least feasible single ideas** at high effort: novelty 3.29 (highest at high effort) and feasibility 3.21 (lowest). Without the graph, ideas are less constrained by the actual product. Judged as sets, though, A and B are rated more novel than C (below): the individual novelty advantage of C does not survive a side-by-side comparison.
- **Individual ideas vs whole sets:** B's ideas score at least as well as A's individually, yet A wins 64% of set comparisons. A's advantage is at the level of the set (specificity, diversity), not in better single ideas.

## Pairwise set judging: full graph vs need slice (equal effort)

Chart 2 (`2_win_rates.png`) shows every pairwise comparison in this and the next three sections; chart 3 (`3_score_diff_A_minus_B.png`) shows how A and B differ on each criterion.

| Effort | Pairs | A wins | B wins | Ties | A win rate | 95% CI | Sign test p | Order agreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| low | 65 | 37 | 18 | 10 | 65% | 53–75% | 0.015 | 85% |
| high | 65 | 34 | 16 | 15 | 64% | 52–74% | 0.015 | 77% |

Mean score difference, A minus B (1–5 scale):

| Effort | Relevance | Novelty | Feasibility | Specificity | Diversity |
| --- | --- | --- | --- | --- | --- |
| low | +0.13 | −0.01 | +0.33 | +0.27 | +0.17 |
| high | −0.01 | +0.06 | +0.09 | +0.34 | +0.16 |

- The full graph's advantage on whole sets is real but modest, mainly in specificity; novelty and relevance are about equal.
- **H2 (B no worse than A on sets) is rejected:** B's win rate is 35–36%, with the lower confidence bound (25–26%) well below the 45% non-inferiority margin. On the tail measure, however, B is not worse than A at any effort.
- **The effect varies by need:** A swept 5–0 for M17 and M6 at high effort and M11 at low; B led for M1 at low effort, M3 at both levels and M8 at high. With 5 pairs per need, no single need is significant.

## Pairwise set judging: the controls (high effort)

| Comparison | Pairs | First wins | Second wins | Ties | First-arm win rate | 95% CI | Sign test p | Order agreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A vs C (full graph vs no graph) | 65 | 44 | 13 | 8 | 74% | 62–83% | < 0.001 | 88% |
| B vs C (need slice vs no graph) | 65 | 34 | 19 | 12 | 62% | 49–72% | 0.053 | 82% |
| B vs R (need slice vs random slice) | 65 | 25 | 20 | 20 | 54% | 42–65% | 0.55 | 68% |
| A vs B (for reference) | 65 | 34 | 16 | 15 | 64% | 52–74% | 0.015 | 77% |

Mean score difference, first minus second arm (1–5 scale):

| Comparison | Relevance | Novelty | Feasibility | Specificity | Diversity |
| --- | --- | --- | --- | --- | --- |
| A − C | +0.21 | +0.24 | +0.29 | +0.88 | −0.11 |
| B − C | +0.16 | +0.20 | +0.14 | +0.52 | −0.30 |
| B − R | +0.14 | −0.08 | +0.20 | −0.03 | −0.20 |

- **Full graph vs no graph:** a clear win for A on every criterion except diversity, above all specificity (+0.88). R vs C was not judged.
- **Need slice vs no graph:** B wins 62%, just short of significance (p = 0.053), again mainly through specificity. C's sets are judged the more diverse (−0.30): without a graph, the five ideas range more widely.
- **Need slice vs random slice:** no detectable difference. B's sets are slightly more relevant and feasible, R's slightly more diverse; 20 of 65 pairs are ties and the judge agreed with itself across orders for only 68% of pairs, the lowest of any comparison, so the two kinds of set are hard to tell apart.
- **Together with the tail:** the graph's set-level benefit grows with the amount of real product structure in the prompt (C < B < A). Relevance shows up mainly in the top tail (B 14.7% vs R 9.8% top ideas), not in the average set. This matters for the claim: a relevant slice helps find the best ideas, but the evidence that it beats a random slice of the same size comes from the tail measure alone.
- **Length does not explain the wins over no graph:** C's sets are longer than B's (529 vs 492 words), yet B wins; in A vs C the longer set won 68% of decided pairs, below A's 74%.

## Pairwise set judging: effort levels (equal condition)

| Comparison | Condition | Pairs | Higher wins | Lower wins | Ties | Higher-effort win rate | 95% CI | Sign test p | Order agreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| high vs low | A | 65 | 58 | 3 | 4 | 92% | 83–97% | < 0.001 | 94% |
| high vs low | B | 65 | 59 | 2 | 4 | 94% | 85–98% | < 0.001 | 94% |
| xhigh vs high | A | 30 | 19 | 5 | 6 | 73% | 56–86% | 0.007 | 80% |
| xhigh vs high | B | 30 | 25 | 4 | 1 | 85% | 68–94% | < 0.001 | 97% |

Mean score difference, higher minus lower effort:

| Comparison | Condition | Relevance | Novelty | Feasibility | Specificity | Diversity |
| --- | --- | --- | --- | --- | --- | --- |
| high − low | A | +0.48 | +0.71 | +0.52 | +1.14 | +0.63 |
| high − low | B | +0.71 | +0.69 | +0.70 | +1.23 | +0.71 |
| xhigh − high | A | +0.25 | +0.34 | +0.02 | +0.46 | +0.33 |
| xhigh − high | B | +0.19 | +0.47 | +0.03 | +0.61 | +0.45 |

- High beats low on every criterion and on all 13 needs.
- xhigh beats high again, mainly through specificity, novelty and diversity, not feasibility, at 1.8× (A) to 2.4× (B) the tokens. Effort had not saturated at the highest level tested.

## Pairwise set judging: slice with high effort vs full graph with low effort

| Comparison | Pairs | B-high wins | A-low wins | Ties | B-high win rate | 95% CI | Sign test p | Order agreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B-high vs A-low | 65 | 56 | 3 | 6 | 91% | 81–96% | < 0.001 | 91% |

B-high was ahead on every criterion and for all 13 needs, at 12,407 vs 14,243 tokens per call (13% fewer). For a similar budget, a relevant slice with more thinking clearly beats the full graph with little thinking.

## Length and judge reliability

| Comparison | Mean words per set (first / second arm) | Longer set won | Win rate of the winning arm |
| --- | --- | --- | --- |
| A vs B, low effort | 452 / 443 | 65% | 65% (A) |
| A vs B, high effort | 542 / 492 | 71% | 64% (A) |
| High vs low effort, A | 542 / 452 | 90% | 92% (high) |
| High vs low effort, B | 492 / 443 | 85% | 94% (high) |
| xhigh vs high effort, A | 587 / 530 | 88% | 73% (xhigh) |
| xhigh vs high effort, B | 587 / 499 | 83% | 85% (xhigh) |
| B-high vs A-low | 492 / 452 | 74% | 91% (B-high) |
| A vs C, high effort | 542 / 529 | 68% | 74% (A) |
| B vs C, high effort | 492 / 529 | 60% | 62% (B) |
| B vs R, high effort | 492 / 492 | 59% | 54% (B) |

- **A vs B at low effort:** sets are nearly the same length, so A's set-level advantage is not explained by length.
- **Effort:** each step up produces longer sets, so part of the effort effect may be detail bias in the judge.
- **B-high vs A-low:** B-high wins 91% but the longer set wins only 74%, so B-high also wins pairs where its ideas are shorter.
- **B vs C:** B wins although its sets are shorter, so the graph's advantage over no graph is not a length effect.
- **Order agreement:** 68–97% of pairs got the same verdict in both orders (85% overall); split verdicts count as ties. The lowest is B vs R (68%), where the sets are hardest to tell apart.
- **Individual scores** do not depend on length comparisons between arms, which makes the tail measure less exposed to detail bias than the pairwise judging.

## Top ideas

The 10 highest-scoring of all 2,892 ideas (`results/top_ideas.md`), all scoring 4.50: 5 from A (high ×2, medium ×2, xhigh), 4 from B (high ×2, low, xhigh) and 1 from R (high). The bottom 10 are dominated by B at low effort (6 of 10).

- **The best ideas converge on two themes from many arms:** replacing the magnetron and high-voltage chain with a solid-state GaN RF source (for M13 energy efficiency, and from R for M7 safety), and solid-state 27 MHz or 915 MHz RF thawing for M4. Arms differ in how often they reach these ideas, not in whether they can.
- **The same technical theme scores low when it does not serve the target need** (e.g. a GaN power stage proposed for M12, healthy diet): the judge rewards fit to the need, not technical appeal alone.
- Many ideas tie at the top, so the ranked list identifies top-scoring ideas rather than a strict order.

## Follow-up: persona as a factor (exploratory)

Does the best representation depend on who is thinking? A follow-up (`persona_as_factor/`, hypotheses H5–H7 written down before the run) crossed three personas with the need slice (B) and no graph (C), on three needs (M4, M8, M13), at medium and high effort, 15 calls per cell (540 planned, 532 logged, 525 parsed and scored; the 8 missing calls did not complete on re-runs and are spread over five cells, 1–2 each, so they cannot change the picture). The innovation engineer is the main study's persona, verbatim; the 45 matching main-study calls were reused. The two new personas replace the first sentence of the system prompt with a description of a way of thinking and one credited exemplar:

- **Lateral thinker:** behavioural economics, changing perception rather than performance; exemplar Rory Sutherland's Eurostar observation (make the journey more enjoyable, e.g. with Wi-Fi, rather than the train faster).
- **Patent-focused inventor:** new, non-obvious, industrially applicable, precise enough to be claimed; exemplar James Dyson's bagless cyclone vacuum.

Ideas were scored with the main study's quality prompt, unchanged, and in a separate call for patentability (new, non-obvious, applicable, overall 1–5).

**Yield (top ideas per 100k tokens), pooled over the three needs and both efforts** (per effort: chart 10, `10_persona_yield.png`; bootstrap spread per persona and representation: chart 11b, `11b_persona_by_representation.png`):

| Persona | B · need slice | C · no graph | B ÷ C [95% CI] | Top-idea rate B / C |
| --- | --- | --- | --- | --- |
| Innovation engineer | 5.9 [4.8–7.2] | 7.0 [5.1–9.1] | 0.84 [0.60–1.22] | 13.4% / 9.3% |
| Lateral thinker | 4.6 [3.6–5.6] | 3.9 [2.7–5.2] | 1.16 [0.80–1.76] | 11.0% / 5.8% |
| Patent-focused | 5.8 [4.8–6.8] | 4.9 [3.6–6.4] | 1.17 [0.86–1.66] | 14.8% / 7.7% |

**One yield per persona** (all its calls: both representations, both efforts; chart 11, `11_persona_effect.png`):

| Persona | Yield [95% CI] | P(beats engineer) | Mean patentability [95% CI] |
| --- | --- | --- | --- |
| Innovation engineer | 6.3 [5.3–7.4] | – | 2.19 [2.15–2.22] |
| Patent-focused | 5.5 [4.6–6.3] | 0.10 | 2.23 [2.19–2.27] |
| Lateral thinker | 4.3 [3.5–5.2] | < 0.001 | 2.17 [2.13–2.21] |

P = share of 2,000 paired bootstrap draws (calls resampled within need) in which the persona's yield is higher than the engineer's. The patent persona's yield is higher than the lateral thinker's in 97% of draws.

- **No persona beat the plain engineer per token.** The engineer is the most efficient overall (the patent persona is behind but not clearly worse); the lateral thinker the least, most of all without a graph (5.8% top ideas, against 9.3% for the engineer). The new personas also cost slightly more per call: their descriptions add about 150 input tokens, and the patent persona thinks longer (about 11.7k output tokens per high-effort slice call, against 9.6k for the engineer).
- **The slice helped every persona's top-idea rate,** and the lateral thinker most: its rate nearly doubles with the slice (5.8% to 11.0%). A persona that works by reframing seems to need concrete product structure to anchor on.
- **The best single cell** is the patent persona with the slice at high effort: 18.0% top ideas, and the only B ÷ C ratio whose interval clears 1 (1.55 [1.03–2.61]). It is one cell of twelve and is reported as a pattern.
- **On these three needs, the engineer's slice does not beat no graph** (B ÷ C 0.84 [0.60–1.22] pooled; at medium effort no graph is even ahead, 10.0 against 6.4, intervals overlapping). In the main study, too, no graph's yield at high effort (6.4) was close to the slice's (5.9); the slice's clear lead there came at medium effort on all 13 needs (8.8), and on M4, one of the three needs here, no graph did well. The slice's efficiency advantage over no graph is therefore need-dependent; its advantage over the full graph and the random slice is the robust result.
- **The exemplars were not copied:** at most 1.8% of ideas mention Wi-Fi, the Eurostar or entertainment (engineer baseline 0.7%), and none mention Dyson, cyclones or bagless designs.

**Against the hypotheses written down before the run:**

- **H5 (the lateral thinker needs the graph less): not supported.** The B ÷ C ratio points the other way (1.16 against the engineer's 0.84), and the intervals overlap.
- **H6 (the patent persona needs the graph more, for patentable ideas): not testable.** The judge rated almost every idea 2 out of 5 for patentability (means 2.13–2.31 in every cell); only about 1% of ideas reach the pre-set threshold of 4, 0–2 per cell, so patentable yields are noise.
- **H7 (personas do what they are told): not supported.** The lateral thinker's ideas are not rated more novel (mean novelty 3.23, against 3.30–3.34 for the engineer), and the patent persona's mean patentability is barely higher (2.23 [2.19–2.27] against 2.19 [2.15–2.22]; a difference of 0.04 on a 1–5 scale, intervals overlapping).

**Reading these results.** The quality rubric (relevance, novelty, feasibility, specificity) rewards concrete engineering, and the operator is SUBSTITUTE; a persona that proposes changes of perception rather than of parts may be marked down by the rubric rather than be worse. Patentability is the judge's estimate without a prior-art search; that it rates nearly all ideas as weakly patentable is consistent with many top ideas reusing known moves (solid-state RF, RF thawing), but it is not a legal assessment. Both are planned for the human check.

## Change from the pilot

The pilot (2 needs × 3 replicates) found the full graph winning 17 of 18 set comparisons. At full scale (13 needs, 65 pairs) A's set-level advantage shrinks to about 64%, and on the tail measure it disappears. The pilot's "more novel but less feasible" pattern for A did not replicate (it now describes no graph, C). The effort effect and the B-high vs A-low result held. Contrary to the pilot's expectation, quality kept rising from high to xhigh.

## Caveats

- **Single judge model,** with no human calibration yet; a "top idea" is one the judge rates highly on relevance, novelty, feasibility and specificity together, a grounded strong idea rather than necessarily the wildest one.
- **Coarse scores:** individual scores move in 0.25 steps, so the threshold (4.0, top 12.3%) is the nearest available cut, and the 4.25 tail has too few ideas to separate arms.
- **Yield assumes a constant rate per token.** The observed running counts are close to straight lines (chart 8), but they depend on the order in which calls are taken; the slope itself does not.
- **Budget curves assume independent calls** within a need and use a small-sample estimate of each need's success rate; they are a model, not observed sequences.
- **R and C were run only at high effort;** R vs C was not judged pairwise, so whether a random slice beats no graph on whole sets is unknown.
- **Relevance vs size rests on the tail measure:** the pairwise judging found no difference between B and R.
- **R is size-matched to B in nodes, not tokens** (17% fewer input tokens).
- **Length and effort are intertwined;** the pairwise effort effects may be partly inflated by detail bias.
- **xhigh covers 6 of 13 needs,** which are slightly easier than average for top ideas; see the matched-needs results.
- **One product, one operator, one prompt.** The worked example comes from the M8 branch of the graph, which may favour ideas in that area.
- **Per-need results** rest on 5 calls or pairs each and should be read as patterns; the slice-size effect is exploratory (13 needs, p ≈ 0.04–0.13).

## Files

| File | Contents |
| --- | --- |
| `runs/rq1_full.jsonl` | all 580 generation calls |
| `results/calls.csv` | one row per call: tokens, length and structure measures |
| `results/summary_condition_effort.csv`, `results/summary_cells.csv` | cost and validity, per arm and per need |
| `results/judgments.jsonl`, `results/pairwise_summary.csv` | pairwise set verdicts; win rates, confidence intervals, sign tests, length check |
| `results/idea_scores.jsonl`, `results/ideas_ranked.csv`, `results/top_ideas.md` | individual idea scores, ranked |
| `persona_as_factor/` | persona follow-up: design and hypotheses (`README.md`), runs, scores, `results/persona_summary.md`, charts 10, 11, 11b |
| `yield_per_market_need.xlsx` | per-need top ideas and tokens per arm, yields, B ÷ A ratios and need-level sign tests (live formulas) |
| `results/tail_summary.csv` (+ `_ge4.25`, `_matched`) | top-idea rates, yields (top ideas per 100k tokens), confidence intervals, tokens per top idea |
| `results/charts/` | 0 the innovation matrix (full, and with the M8 slice; `figure_innovation_matrix.py`) · 1 tokens per call · 2 win rates · 3 score differences · 4 cost vs quality · 5 context ladder · 6 top-idea rate · 7 chance of a top idea vs budget · 8 top ideas vs tokens spent (yield) · 8b/8c spread of the slopes (8c annotated) · 9 slice-size effect per need |
