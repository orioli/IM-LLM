# What a full experiment would need

Written after the pilot (12 to 14 November 2026). The numbers come from `results/power_analysis.md`,
`results/judge_family_check.md` and `results/cost_breakdown.md`, and the scripts behind them can be re-run
without any API calls.

## Where the pilot leaves us

The pilot repeated Experiment 2 on M6 with three Chinese models, 10 calls per representation, on a $10 key.
Next to the paper's three Claude runs, all six give the same picture:

| Yield ratio (1.00 means no difference) | Claude (paper) | Chinese (pilot) | All six |
| --- | --- | --- | --- |
| Full graph / no graph | 0.55 [0.40-0.77] | 0.60 [0.47-0.77] | 0.57 [0.48-0.68] |
| Slice / no graph | 1.00 [0.85-1.18] | 1.04 [0.81-1.34] | 1.01 [0.88-1.16] |
| Full graph / slice | 0.55 [0.46-0.66] | 0.59 [0.47-0.75] | 0.56 [0.49-0.64] |

So on M6 the Chinese models reproduce both effects at about the same size. That is a replication on the
paper's own test case. It doesn't show that the paper holds in general, because M6 was picked for already
showing the pattern, and nothing in it suggests the paper fails for Chinese models either.

## What's still missing

1. Needs that weren't picked for their result. The paper chose M6 with a rule that only kept needs where
   the representations already ranked as in the pooled result, and that rule dropped five needs (M3, M4,
   M7, M12, M17). The 50-idea design has never been run on any of them, and if the paper fails anywhere we
   would expect it there.
2. Experiment 1. The headline numbers (the slice at about three times the full graph, ahead on 10 of 13
   needs) come from Experiment 1, which only used Haiku. A statement about the paper as a whole needs it.
3. More calls. With 10 calls per representation, one model only detects a ratio of about 1.9. Seeing a 25%
   difference, or showing that two representations are equal within 25%, takes 85 to 90 calls per
   representation and model. In Experiment 1 the paper's 5 replicates per need detect about 1.5, and around
   20 would be needed for 25%.
4. The judge. Sonnet agrees with itself on which ideas are top 66% of the time, and a DeepSeek judge agrees
   with it barely above chance on the same ideas, even though both rank the representations, and the six
   models, in the same order. A DeepSeek judge also shrinks the Claude models' lead by about a quarter, and
   with the data we have we can't tell whether that's Sonnet favouring its own family or the DeepSeek judge
   separating ideas less well (`results/judge_family_check.md`). Only people can settle which judge to trust.
5. More labs. Three models from two labs is a thin basis for saying anything about "Chinese models".
6. The random slice. It's the least stable result in both families (its yield runs from 0.40 to 1.07 of no
   graph's), and with one draw per need there's no telling "random context hurts" apart from "this draw
   hurt".

## The design we'd propose

Everything stays as in the paper (prompts, graph files, operator, judge prompt and model, a top idea at 4.0
and yield per token as the main measure), so that each part can sit next to the paper's own tables.

**Part A, Experiment 1 with Chinese models.** All 13 needs and all four representations at the same effort
(medium), with 20 replicates per need and representation where the paper had 5. That's 1,040 calls per
model. The paper ran no graph and the random slice at high effort only, so they can't be compared with the
slice and the full graph at medium, which is where its headline number comes from; running everything at
medium fixes that. Models: DeepSeek V4.1 Flash, Qwen3.8 Flash, GLM-5.3 Flash and DeepSeek V4 Pro, plus Haiku
again with all four representations at medium as the Claude reference.

**Part B, Experiment 2 on needs that weren't picked for their result.** The 8 needs that pass the paper's
first two rules (M3, M4, M6, M7, M12, M13, M14, M17), without the third. M6 is done, so 7 are new. 10 calls
per need and representation as in the paper, which is 280 new calls per model, and pooled over 8 needs
that's 80 calls per representation and model, enough to see a 25% difference. Three random-slice draws per
need (`slicer.py` seeds 1 to 3) instead of one. Same models as Part A. Opus could be added here for about
$100, since the paper's case is weakest on its run (see `CHINESE_REPLICATION.md`, Section 9, point 4).

**Part C, the measure.** A second Sonnet pass on a random 20% of requests, to see how reliable "top idea" is
for each model's ideas. A judge from the other family on 15%, with its cut-off set to give the same share of
top ideas as Sonnet. And two people rating 240 ideas blind with `../human_check.py`, stratified by model and
representation.

**Part D, rules fixed before the first call** and agreed with the paper's authors. We'd say the paper
generalises if, per model and pooled, the full graph's yield is below no graph's with its interval below 1
and the slice's is within 0.80 to 1.25 of no graph's (equivalence, two one-sided tests at 5%). We'd say it
fails for a model or a need if either ratio has its interval above 1 and fresh calls confirm it. Anything
else is inconclusive and gets reported that way. The main analysis uses log yield ratios, resamples calls
within need and representation and pools over needs and models with random effects. Results per need are
descriptive only, since 10 calls per need detect only a factor of two. The analysis code is committed before
the first call, so the timestamp is on record.

## Cost

`results/cost_breakdown.md` has every item. The plan above comes to about $156, and a lean version that keeps
the most informative parts comes to about $30:

| | Full plan | Lean |
| --- | --- | --- |
| Models | Haiku and four Chinese models | Haiku and DeepSeek V4.1 Flash |
| Part A | 13 needs, 20 replicates | 13 needs, 10 replicates |
| Part B | the 7 new needs | the 5 needs the paper dropped |
| Second judge | DeepSeek V4 Pro on 15% | DeepSeek V4.1 Flash on 15% |
| Estimate | about $156 | about $30 |

Most of the money goes on judging: 64% of the full plan and 76% of the lean one. Sonnet costs about $0.0006
per idea even at batch price, which is more than DeepSeek V4.1 Flash or Haiku spend writing the idea ($0.0001
to $0.0002). The full plan scores about 98,000 ideas, a bit over six times the 15,560 the paper scored one by one, so the bill
follows the number of ideas judged much more than the choice of models. For comparison, the calls logged in
the repository for the paper come to $86.76 at list price, $44 of it the Opus and Fable runs.

The ways to bring it down, roughly in order of how much they save, are fewer models, 10 replicates instead
of 20 in Part A (which detects about 1.35 to 1.4 instead of 1.25), judging only part of each 50-idea list,
and a cheaper judge. The last one changes the measure. DeepSeek V4.1 Flash costs a sixth of Sonnet per
request and ranked the six runs in the same order, but it agrees with Sonnet on individual ideas only
loosely, so we'd only use it for a share of the requests and next to Sonnet.

## What each outcome would let us say

If both rules hold in Parts A and B, the claim becomes that the paper's findings generalise to four models
from three Chinese labs, over 13 needs at 5 ideas and 8 needs at 50 ideas, at about the size reported for
Claude. That's a replication and an extension, and still worth having.

If they fail on some needs or models, the claim is that the result depends on the need or the model, for
example that the slice pays for itself on particular needs. The five needs the paper dropped are where we'd
look first.

## Order of work

1. Agree on Part D and the model list, then commit the code.
2. A test call for every model on its pinned host (`run_all.sh smoke`), as in the pilot.
3. Part A, since it's cheap and quick and it's the paper's main experiment, judged by batch.
4. Part B.
5. Part C alongside 3 and 4, with the human ratings last.
6. Fresh calls for anything that contradicts the paper, before writing it up.

The scripts for all of this exist and ran end to end in the pilot. Part A still needs a run script for the
5-idea design with the model switch (the generator already takes any model), and Part B needs two more
random-slice draws per need from `slicer.py`.
