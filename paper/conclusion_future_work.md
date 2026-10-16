# Conclusion and future work

## Conclusion

This study asked how much of a product's knowledge graph an LLM needs to see in order to brainstorm well, measured not by the quality of its output alone but by how efficiently it turns tokens into good ideas. An innovation matrix [@Tchirsky] of a microwave oven (123 nodes, 246 edges) was given to `claude-haiku-5-5` in four forms: the full graph (A), the vertical slice for the target market need (B), a random slice of the same size (R), or no graph at all (C). The model applied the SUBSTITUTE operator to 13 market needs, with 5 replicates per cell and four levels of thinking effort. The 2,892 resulting ideas were judged blind by `claude-sonnet-5-5`, both as whole sets side by side and one idea at a time.

Brainstorming is a search for the rare great idea, so the main measure was the **yield**: top ideas (the top ~12% of all ideas) found per 100k tokens spent. Counted against tokens, top ideas accumulate in a straight line for every arm, so arms can be compared by slope. Five conclusions follow.

1. **A relevant slice of the graph finds top ideas fastest.** The need slice at medium effort yields 8.8 top ideas per 100k tokens, about three times the full graph at any effort (2.6–3.2). The advantage over the full graph holds need by need: the slice is more efficient on 10 of 13 market needs (sign test p = 0.039), and its lead looks largest where the slice is small (exploratory).

2. **More context buys better average sets, not more great ideas.** Judged as whole sets, the full graph beats the slice (64%) and no graph (74%), mainly by being more specific. But its top-idea rate is no higher than the slice's, and its calls cost about twice as much, so per token it finds fewer top ideas than giving the model no graph at all (3.1 against 6.4 at high effort).

3. **Relevance matters, size does not.** A random slice of the same size as the need slice is the least efficient graph form: the need slice's slope is higher in 99% of paired bootstrap draws (5.9 against 4.1 at high effort), and no graph beats the random slice on 10 of 12 needs (p = 0.039). Irrelevant structure is worse per token than none. Judged as whole sets, need slice and random slice cannot be told apart: relevance shows up in the best ideas, not in the average set.

4. **Thinking effort raises quality, not efficiency.** High effort beats low in about 93% of set comparisons, and extra-high effort gives the highest top-idea rates (19–21%). But each call costs proportionally more, so yield does not rise with effort: the full graph stays at about 3 top ideas per 100k tokens from low to extra-high, and the slice peaks at medium effort.

5. **A persona prompt is no substitute for the right context (exploratory).** In a follow-up on three needs, neither a lateral-thinker persona nor a patent-focused persona beat the plain innovation engineer per token (6.3 top ideas per 100k tokens against 5.5 and 4.3), and the hypotheses that they would change which representation works best were not supported. The lateral thinker was the least efficient, especially without a graph; given the need slice, its top-idea rate nearly doubled. The judge rated almost no idea from any persona as clearly patentable.

Taken together: **to find great ideas efficiently, show the model the part of the product that bears on the problem, let it think moderately, and run it many times**, rather than giving it everything and asking it to think hard once. Which representation to use is a more durable decision than which model to use, because it keeps paying off as models change.

**Parsimony versus holism.** The results read as a contest between Ockham's razor and holistic thinking, with a twist. The razor says not to multiply entities *beyond necessity*, and here the target need defines what is necessary: the need slice, the graph cut to what the problem requires, is the most efficient form. Less context is not better as such: a random slice of the same size is the least efficient graph form, and no graph at all only matches the slice on some needs. The full graph is the holistic bet, that distant parts of the product interact, and it does buy more specific ideas and better sets, but in calls aimed at one need it pays for the whole product to reach the same need from further away. Which principle wins depends on whether the problem has been framed [@Dorst2011]: *once the problem is framed, parsimony beats holism per token; before it is framed, holism may be what finds the frame.* The open brainstorm proposed below tests the second half of that sentence.

## Implications for design thinkers and practitioners

- **Frame before you generate.** The need slice is a machine version of a familiar design move: narrowing the problem to the functions, components and technologies that serve one user need before ideating. In this study that framing was worth more than exhaustive context, and more than asking the model to think harder. A well-built product graph lets a team cut that frame automatically, for any need.

- **Budget LLM brainstorming by yield.** The useful question is not "how good is the average idea?" but "how many great ideas does a given spend buy?" Many cheap, focused calls beat a few expensive, all-knowing ones. A team can plan an ideation session like a test campaign: pick the representation with the best yield, set a budget, run the calls, filter the tail.

- **Don't give the model everything just because you can.** Long contexts are easy to assemble and feel thorough. Here the full graph made top-idea generation about three times less efficient than the right slice, and an irrelevant slice was worse than nothing. What goes into the prompt should be chosen as deliberately as who is in the workshop.

- **Don't expect a persona to do the work of the context.** Asking the model to think like a lateral thinker or a patent-minded inventor did not make it more efficient, and did not make its ideas more novel or more patentable in the judge's eyes. The representation of the problem mattered more than the role the model was asked to play.

- **Curation becomes the human's main job.** Every arm produced strong and weak ideas side by side; even the best arm's top ideas are about one in seven. The value of the human shifts from generating ideas to recognising and developing the few good ones. Tools should make that triage fast: score, cluster, surface the tail.

- **The product graph is a reusable, auditable design asset.** Building the innovation matrix once pays off across every need, operator and session, and each idea anchors to named nodes and proposes new nodes and edges, so a team can see where in the product an idea intervenes and what it would change.

- **Recurring themes are a signal.** The best ideas from many arms converged on the same moves (solid-state RF replacing the magnetron; low-frequency RF thawing). When independent runs keep arriving at one idea, it is a strong candidate for development, and the convergence itself is a cheap form of validation.

## New research directions

- **Graph-guided search instead of single prompts.** Use the graph to steer a sequence of calls: pick a need, slice, generate, score, then expand the slice around the anchors of the best ideas and generate again. Brainstorming becomes an explicit search over the product structure, with yield as its objective.

- **Learning which slice to show.** The vertical slice was fixed by rule. Slices could instead be selected by retrieval or graph centrality, or learned from which nodes appear in top ideas. The slice-size pattern suggests that smaller, more focused slices may be more efficient still.

- **Open brainstorming without a target need.** Every call here targeted one market need, so the full graph's extra context could only reach for the same need from further away. In an open brainstorm, where the model chooses where in the product to innovate, the full graph may play a role no slice can.

- **Operators as graph transformations.** SUBSTITUTE, TRIZ principles and SCAMPER moves can each be defined as operations on the graph (replace a component node, merge two functions, remove a constraint edge), so ideas can be checked for whether they perform the operation they claim, and operators compared by the changes they produce.

- **Ideas written back into the graph.** Accepted ideas could be merged into the graph, so the product model grows with every session and later runs build on earlier ones: a living design knowledge base.

- **Yield as a standard measure.** Top ideas per token is simple, transferable and does not saturate. It could become a standard way to report LLM ideation, alongside or instead of mean scores that hide the differences that matter.

## What should be tested next

In order of priority.

1. **Human validation of the judge (planned).** Three raters with engineering or product background rate a blind, stratified sample of 99 ideas (`human_check.py`), and the persona study's ideas are added to the sample. Report agreement between raters and with the judge, and above all whether ideas the judge places in the top tail are also rated highest by people. This also tests whether the quality rubric is unfair to perception-changing ideas such as the lateral thinker's.

2. **Extend the persona study.** Add the full graph as a third representation for each persona, and a persona-specific rubric (for example a perception-change criterion for the lateral thinker), to separate a weaker persona from a rubric that does not see what it is good at. Patentability needs a prior-art-aware judge: without one, the judge's ratings stayed near 2 of 5 for every persona.

3. **A second product and a second operator.** Repeat the core arms (B and C at medium effort, A at high effort) on a different product graph, ideally from another domain, and with at least one TRIZ principle and one more SCAMPER operator, to move the claim from "one microwave, one operator" towards a general result.

4. **Close the open comparisons.** Judge R against C on whole sets, and run R and C at medium effort, where the need slice was most efficient.

5. **Test the slice-size effect directly.** Vary the size of the slice for the same need (for example by depth of the walk down the matrix) and measure yield, to confirm that smaller, more focused context is more efficient and to find where it stops helping.

6. **Replace the 5-ideas-per-call format.** Test 1, 5 and 10 ideas per call at equal total budget; if one idea per call yields more top ideas per token, the format itself has been holding the tail back.

7. **More replicates for the tail.** Twenty calls per need for the leading arms would tighten the per-need estimates and allow the stricter top-idea threshold (≥ 4.25) to separate arms.

8. **Other judges and other generators.** Re-score a subset with a second judge model, and run the generation with a larger model, to test whether a stronger model needs less, or makes better use of more, context.

9. **Remove or swap the prompt's worked example.** The example came from the M8 branch of the graph; a run without it, or with an example from another branch, would show how much it steers the ideas.

10. **From ideas to outcomes.** Take the top ideas from each arm into an expert review or concept-development exercise, and record which ones practitioners would actually pursue: the final test of whether the judge's top tail is the one that matters in practice.
