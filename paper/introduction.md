# Is less more?

*Narrow context is more efficient than full context for generative ideation with product graphs*

## 1 Introduction

Most research on AI for innovation asks about outcomes. Are LLM ideas as good as human ones [@Si2024; @Terwiesch2026]? Do people generate better ideas with AI than without it [@Doshi2024; @Anderson2024]? Does an agentic pipeline beat a single prompt, or a human team [@Liu2026; @Massoudi2026]? These comparisons expire. Every model generation raises the outcome and lowers its price, so a finding that a model does or does not reach human level says more about the model of the day than about how to innovate with AI.

A question that lasts longer is how to **present the problem** to the model. The same task can be shown as a full structured model of the product, as the part of it that bears on the problem, or not at all. Whichever model is current, a team still has to decide what goes into the prompt and how much to pay for it. The measure that matters is therefore **outcome per token**: how efficiently a way of presenting the problem turns compute into useful ideas. Cost-aware evaluation is becoming standard for LLM reasoning and agents [@Chen2024d; @Wang2024; @Kapoor2025], but not yet for design ideation.

The outcome itself needs care. Brainstorming is a search for the few excellent ideas among many, so what matters is the best ideas, not the average [@Dahan2001; @Girotra2010]. We measure **yield**: top ideas (the top ~12% of all ideas) per 100k tokens. Counted against tokens spent, top ideas accumulate in a straight line, so representations can be compared by slope.

We study this with an established structured product description, the *innovation matrix* (IM) of Leo Tchirsky [@Tchirsky]: a typed graph linking **market needs → functions → components → enabling technologies**, with constraints and actors attached. The microwave-oven IM used here has 123 nodes and 246 edges. More context is not free even when it fits: long inputs can lower LLM performance [@Liu2024; @Levy2024], and retrieving the relevant part can match the whole at a fraction of the cost [@Li2024]. One model applies one innovation operator (SUBSTITUTE) for 13 market needs, with the prompt fixed and only the representation varied:

- **A, full graph:** the whole IM;
- **B, need slice:** the target need's vertical slice;
- **R, random slice:** a size-matched random selection of nodes, separating relevance from size;
- **C, no graph:** the product and the need only.

These are crossed with four levels of thinking effort, the other main way to spend tokens: 580 calls and 2,892 ideas, judged blind by a second model, as whole sets and idea by idea. We ask:

- **RQ1.** Which representation yields the most top ideas per token?
- **RQ2.** Does the amount or the relevance of the graph matter?
- **RQ3.** How does spending tokens on context compare with spending them on thinking effort?

An exploratory follow-up asks whether the answer depends on the persona the model adopts [@Lu2024]: innovation engineer, lateral thinker [@Bono1970] or patent-focused inventor.

**Findings in brief.** The need slice at medium effort yields 8.8 top ideas per 100k tokens, about three times the full graph at any effort (2.6–3.2), and beats it on 10 of 13 needs. The full graph wins whole-set comparisons, mainly through specificity, but no more of its ideas reach the top, and at twice the cost per call it is less efficient than no graph at all (3.1 against 6.4 at high effort). Relevance, not size, drives the gain: the need slice out-yields the size-matched random slice in 99% of bootstrap draws, and the random slice is the least efficient graph form. More thinking effort raises quality but not yield. No persona beat the plain engineer per token.

**Contributions.**

- A framing of AI-ideation research around representation efficiency, outcome per token, instead of outcome benchmarks against humans or against no AI.
- Yield, top ideas per token, as a top-tail measure that does not saturate and leads to different conclusions from mean scores.
- A controlled comparison of four representations of one product graph, crossed with thinking effort and, exploratorily, persona, with all prompts, calls and judgements released.

---

### Notes for the authors (delete before submission)

- **Two references still to add** to `references.bib` (from memory; check the DOIs):

```bibtex
@article{Girotra2010,
  author  = {Girotra, Karan and Terwiesch, Christian and Ulrich, Karl T.},
  title   = {{Idea Generation and the Quality of the Best Idea}},
  journal = {Management Science},
  volume  = {56}, number = {4}, pages = {591--605},
  year    = {2010},
  doi     = {10.1287/mnsc.1090.1144}
}

@article{Dahan2001,
  author  = {Dahan, Ely and Mendelson, Haim},
  title   = {{An Extreme-Value Model of Concept Testing}},
  journal = {Management Science},
  volume  = {47}, number = {1}, pages = {102--116},
  year    = {2001},
  doi     = {10.1287/mnsc.47.1.102.10666}
}
```

- **`Tchirsky`**: the innovation matrix is Leo Tchirsky's. Add his entry to `references.bib` under this key (or rename the key in the text).
- All other keys are in `references.bib`. `Girotra2023` (the SSRN working paper) was replaced by its published successor `Terwiesch2026`.
- `Kyffin2009` uses "innovation matrix" for a different, Philips design-led framework. If a reviewer may confuse the two, add one clause: "(not to be confused with the design-led innovation matrix of [@Kyffin2009])".
- The earlier manipulation-check paper (typed vs untyped graph) fits as one more example of representation research; one sentence after the second paragraph would link the two papers.
