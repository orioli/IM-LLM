## 3 Methods

The experiment holds the model, the task and the prompt fixed, and varies only how much of the product graph the prompt contains (the *representation*) and how long the model may think (the *effort*). It measures what each combination produces and what it costs.

### 3.1 Product graph

**The innovation matrix.** The innovation matrix (IM) of Leo Tchirsky [@Tchirsky], as taught in design-thinking workshops [@berengueres2014], describes a product as stacked layers: the **market needs** it serves, the **functions** that serve them, the **components** that perform the functions, the **technologies** that make the components possible, and the scientific **fields** behind those technologies (Figure 1). Reading upwards answers *why* a part exists; reading downwards answers *how* a need is met. Innovation happens by changing a link: a new technology enables a different component, a component takes over another's function, or a function is found to serve a need nobody had linked it to. In a workshop the matrix is drawn on a wall; here it is a typed graph that a model can read.

> **Figure 1.** An innovation matrix as drawn in the workshop material [@berengueres2014]. *[Figure from the Brown Book to be inserted.]*

**The microwave matrix.** The product is a countertop microwave oven, the simplest mechanical model: a timer knob, a power knob, a door button and an interior lamp. The authors built its IM by hand in a single YAML file (`microwave_base_graph.yaml`), adding two cross-cutting types the workshop matrix keeps beside it, constraints and actors. It has 123 nodes and 246 directed, typed edges (Figure 2; all nodes listed in Appendix A).

> **Figure 2.** The microwave innovation matrix used in the experiment (`0_innovation_matrix_M8.png`). Rows are the layers, bottom to top, with constraints below and actors above. Filled nodes and edges are the need slice for M8, *know when food is ready* (25 nodes, 32 edges): what the model sees in condition B for that need, against the whole graph in condition A.

**Nodes** belong to four stacked layers and four cross-cutting types:

| Type | Count | Role |
| --- | --- | --- |
| MarketNeed (M) | 17 | what users want (e.g. M4 *Defrost frozen food quickly*) |
| Function (F) | 20 | what the product does |
| Component (C) | 28 | physical parts |
| Technology (T) | 24 | the principles that enable components and functions |
| Field (D) | 10 | scientific fields the technologies are rooted in |
| Constraint (X) | 15 | limitations and conflicts (e.g. X3 *uneven heating*) |
| Actor (A) | 8 | user groups (e.g. A5 *parent with young children*) |
| Product (P) | 1 | the microwave oven |

**Edges** carry one of twelve types. Those that build the layer stack are `has_component`, `performs_function`, `enables_function`, `addresses_need`, `enabled_by` and `rooted_in`. Component-level flows are `feeds` and `actuates`. Constraint links are `causes`, `contradicts` and `partially_mitigates`. Weak associations are `relevant_to`. A thirteenth type, `resolves`, is declared in the schema for agents to use when a new node replaces or solves an existing one; it does not occur in the base graph.

Each node has an identifier, type, label and a one-line detail. The file begins with a meta block that names the layers and defines the edge types.

### 3.2 Representations

Every prompt contains a graph file produced by one serializer from the base graph. Fields, ordering and the meta block are the same in every file; only *which* nodes and edges are present differs. No file states which condition it belongs to. For each target need $M_k$ (`slicer.py`):

- **A, full graph.** All 123 nodes and 246 edges. One file shared by all needs.
- **B, need slice.** The vertical slice of $M_k$, obtained by walking down the matrix from the need:
  1. the functions that `addresses_need` $M_k$, plus every function that enables them through `enables_function`, recursively;
  2. the components that `performs_function` one of those functions;
  3. the technologies that enable those components or functions (`enabled_by`);
  4. the fields those technologies are `rooted_in`;
  5. every constraint linked to any node above by `causes`, `contradicts`, `partially_mitigates` or `relevant_to`, and every actor `relevant_to` $M_k$;
  6. the product node.

  The file contains the edges induced among the selected nodes.
- **R, random slice.** The target need and the product, plus a random draw of nodes with the same number of nodes of each type as B, with the induced edges. The draw is seeded by the need identifier (`random.Random("<need>-1")`), so it is reproducible and independent of run order. R controls for the *size* and layer composition of B while removing its *relevance* to the need.
- **C, no graph.** The meta block (layer names and edge-type definitions) and the target need node only.

Four needs (M2, M9, M10, M15) are not addressed by any function, so their vertical slice is empty. They were excluded, leaving 13 target needs: M1, M3, M4, M5, M6, M7, M8, M11, M12, M13, M14, M16, M17.

| Condition | Nodes | Share of graph | Edges | Input tokens per call (mean, incl. prompt) |
| --- | --- | --- | --- | --- |
| A | 123 | 100% | 246 | 10,912 |
| B | 10–51 (median 45) | 8–42% | 11–85 | 3,778 |
| R | 10–51, same as B for each need | 8–42% | 2–52 | 3,143 |
| C | 1 | 1% | 0 | 1,055 |

R matches B in node count and type composition but not in edges. Randomly drawn nodes are less connected to one another than the nodes of a vertical slice, so R contains fewer induced edges than B for every need. It also uses 17% fewer input tokens. R shares 3–29 nodes with B for the same need, mostly by chance among the larger slices. A manifest (`slices/manifest.csv`) records, for every file, the node identifiers, counts per type, edge count, token count and SHA-256 hash.

### 3.3 Task and prompt

All calls use one prompt template (`template_prompt.txt`, Appendix B). It asks the model to innovate the product "based on the graph given", encourages radical and wild ideas, and asks it to favour innovations that serve the target need. Placeholders are filled by literal substitution: product name, target need identifier and label, operator name and definition, the graph file, and the number of ideas.

- **Operator.** SCAMPER *Substitute* in every call: "Identify components and the functions they perform, then replace them with something cheaper or simpler that fulfils the same function equally well or better."
- **Worked example.** One example of an innovation the brief likes, taken from the authors' workshop material [@berengueres2014]. The door's mesh and the interior lamp both serve the user's need to see the food, so they can be replaced together by a webcam, or by a transparent casing that needs no lamp.
- **Output.** Exactly 5 ideas as JSON. Each idea has a title; the identifiers of existing nodes it was applied to (*anchors*); new nodes (type, label, one-line detail); new edges; and a one-sentence rationale for how it serves the target need.

The prompt is identical across conditions except for the graph file. In condition C, the "graph given" is only the schema and the target need.

### 3.4 Generation

- **Model.** `claude-haiku-5-5`, through the Anthropic Messages API, with streaming. No sampling parameters were set; the model does not accept a temperature setting, so all calls use its defaults.
- **Thinking effort.** Set per call through the API's effort parameter, at four of the five available levels: low, medium (the model's default), high and xhigh. Thinking tokens are billed and reported as output tokens.
- **Output limit.** 48,000 tokens (64,000 for xhigh). No call reached its limit.
- **Design.** Five replicates per cell, each a fresh call with the identical prompt:

| Conditions | Efforts | Needs | Calls |
| --- | --- | --- | --- |
| A, B | low, medium, high | 13 | 390 |
| A, B | xhigh | 6 (M1, M4, M6, M8, M13, M17) | 60 |
| R, C | high | 13 | 130 |
| **Total** | | | **580** |

The xhigh cells cover 6 needs, chosen to span small and large slices, to limit cost. R and C were run at high effort only.

- **Parsing.** A response is valid if it parses as JSON with an `ideas` list. 579 of 580 calls were valid with 5 ideas; one returned no parseable ideas and is kept as a failure. In total, the calls produced 2,892 ideas.
- **Logging.** The runner appends one JSON line per call to an append-only log (`runs/rq1_full.jsonl`). Each line holds the run identifier (condition, need, effort, replicate), the graph file's identifier and hash, the prompt hash, model, output limit, input and output tokens, latency, stop reason, the parsed ideas and the raw response. Runs are resumable, and cells can be added later without rerunning earlier ones.

### 3.5 Judging

Ideas were judged blind by a second, larger model, `claude-sonnet-5-5`, at medium effort, in two ways. In both, the judge saw each idea's **title, new elements (label and detail) and rationale only**. Node identifiers, anchors, edges, condition, effort and run identifiers were removed, so nothing revealed which graph the idea came from. The brief shown to the judge gave the product, target need, operator, and the instruction that radical, wild ideas serving the need were wanted.

**Pairwise set judging.** Two idea sets for the same need and replicate, differing in one factor, were shown side by side. The judge scored each set from 1 to 5 on relevance, novelty, feasibility, specificity and diversity (how different the ideas are from each other), and named the better set or a tie (prompt in Appendix C). Every pair was judged twice, once in each presentation order, and the two verdicts were combined into one result per pair: agreeing verdicts count as a win, opposite verdicts as a tie. If one side had no parsed ideas, the other won without a judge call (one pair per affected comparison). The comparisons judged were:

| Comparison | Effort | Pairs |
| --- | --- | --- |
| A vs B | low, high | 65 each |
| B vs R, B vs C, A vs C | high | 65 each |
| high vs low, within A and within B | — | 65 each |
| xhigh vs high, within A and within B | — | 30 each |
| B at high vs A at low | — | 65 |

**Individual idea scoring.** Each call's five ideas were sent to the judge in one request, with the instruction to rate each idea on its own merits, independently of the others. Each idea was scored from 1 to 5 on relevance, novelty, feasibility and specificity (prompts in Appendix D). An idea's **score** is the mean of the four ratings. All 2,892 ideas were scored; two calls whose first scoring returned the wrong number of ratings were scored again.

### 3.6 Measures

**Cost.** Input, output and total tokens per call, from the API's usage report.

**Use of the graph** (computed without model calls, from the parsed ideas):

- *anchors outside the need slice*: the share of anchors that are existing nodes outside B's slice for that need;
- *anchors not in the graph*: the share of anchors that match no node identifier in the base graph;
- *ideas echoing the worked example*: ideas whose title or new nodes mention a webcam, camera or transparency;
- *new nodes per idea*, and *words per idea* in the text the judge sees.

**Top tail.** A **top idea** is one whose individual score is at least 4.0. Scores move in steps of 0.25 (one step of a 1–5 rating, averaged over four criteria), so no exact percentile cut exists; 4.0 is the step closest to the top 10% and keeps 12.3% of all ideas (355 of 2,892). As a stricter check, 4.25 keeps the top 2.4% (68 ideas). Target needs differ widely in how easily they yield top ideas (from 3% to 29% of ideas at 4.0), and the xhigh arms cover only 6 needs, so every rate is computed per need and then averaged over the needs an arm was run on, each need weighing the same. For each arm:

- **top-idea rate**: the need-averaged share of the arm's ideas that are top ideas;
- **calls with a top idea**: the need-averaged share of calls producing at least one top idea;
- **tokens per top idea**: the arm's total tokens divided by its number of top ideas;
- **chance of a top idea for a budget** $b$: the probability of at least one top idea when $b$ tokens are spent on whole calls of that arm, averaged over needs. For need $j$, with $p_j$ the share of calls containing a top idea and $\bar t_j$ the mean tokens per call, $k = \lfloor b / \bar t_j \rfloor$ calls succeed with probability $1 - (1 - p_j)^k$. Calls are treated as independent. Because 5 calls per need often give a raw share of exactly 0 or 1, $p_j$ is the Jeffreys estimate $(h_j + \tfrac12)/(n_j + 1)$, where $h_j$ of $n_j$ calls contained a top idea.

**Mean idea score.** The need-averaged mean individual score per arm, and the mean of each criterion.

### 3.7 Statistics

**Pairwise judging.** The unit is the pair, not the verdict: the two presentation orders of a pair are not independent, so they are combined first. For each comparison:

- the *win rate* of the first-named arm, with ties counting as half a win;
- a Wilson 95% confidence interval;
- an exact two-sided sign test on wins against losses, ties excluded;
- the *order agreement*, the share of pairs that received the same verdict in both orders;
- the mean score difference per criterion.

H2, that the need slice is no worse than the full graph, is tested as non-inferiority with a margin of 45%: B is non-inferior if the lower bound of its win-rate interval against A is above 45%.

To check whether judges favour longer sets, each pairwise record stores the number of words each side showed the judge. The share of decided pairs won by the longer set is reported next to each win rate.

**Top tail.** 95% confidence intervals for the top-idea rate and the call rate come from 2,000 bootstrap resamples. Each resample redraws calls with replacement within each need, which keeps the five ideas of a call together and the need-averaged weighting fixed.

No correction for multiple comparisons was applied. Per-need results rest on 5 calls or pairs each and are reported only as patterns.

### 3.8 What was planned and what was not

- **Planned before the full run.**
  - The four conditions, including R and C as controls.
  - The A vs B comparison at low and high effort, with H1 (the full graph yields better sets) and H2 (B non-inferior to A at a 45% margin).
  - The effort comparison, high vs low.
  - H3 (B better than R) and H4 (graph better than no graph), to be tested by pairwise judging.
- **Added after the pilot.**
  - Medium and xhigh effort.
  - The B-high vs A-low comparison.
  - Judging in both orders, the length check, and individual idea scoring, which was first used to rank ideas for inspection.
- **Exploratory, defined after seeing the results.**
  - The top-tail analysis: the 4.0 threshold, top-idea rate, tokens per top idea and chance for a budget.
  - The need-averaged mean idea scores.

The top-tail measures follow from the purpose of brainstorming (Section 1), but they were chosen after the pairwise results were known and are reported as exploratory. Their conclusions about relevance (B against R) are not confirmed by the planned pairwise test (Section 4).

### 3.9 Pilot

A pilot (2 needs, M8 and M16; A and B; low, medium and high effort; 3 replicates; 36 calls) tested the pipeline. It led to five changes:

- the output limit was raised from 8,000 to 48,000 tokens, after half the high-effort calls used up their budget thinking and returned no ideas;
- calls were switched to streaming;
- effort was added to the run identifier so cells could be resumed;
- every pair was judged in both orders;
- the length check was added.

The pilot's 17-of-18 advantage for the full graph did not survive at full scale (Section 4).

### 3.10 Human validation (in progress)

To test whether the judge's individual scores, and in particular its top tier, agree with people, a stratified sample of 99 ideas is being rated by three raters with engineering or product background, working independently (`human_check.py`).

- **Sample.** Ideas are drawn by judge score band: 29 at ≥ 4.25, 30 at 4.0, 25 at 3.5–3.75 and 15 at ≤ 3.25. Within each band, the draw rotates across conditions and allows at most 3 ideas per need.
- **Rating sheet.** Raters see the need, title, new elements and rationale. Condition, effort, scores and node identifiers are removed. They rate the same four criteria and say whether they would pursue the idea.
- **Analysis.** Agreement between raters (Krippendorff's α, interval) and between raters and judge (Spearman's ρ). Also the probability that an idea the judge scores ≥ 4.0 receives a higher human score than one it scores below 4.0.

### 3.11 Reproducibility

The repository contains the base graph, the slicer and its manifest, the prompt template, the generation runner, the analysis scripts (`analyze.py`, `top_ideas.py`, `tail_charts.py`, `charts.py`, `human_check.py`), the complete call log with raw responses, all judge outputs, and the derived tables. Every number in Section 4 is regenerated by four commands: `python analyze.py stats`, `python analyze.py summary`, `python top_ideas.py report` and `python tail_charts.py`. Total generation used about 8.6 million tokens.

---

### Notes for the authors (delete before submission)

- **Appendices:** A (innovation matrix, all nodes), B (generation prompt, `template_prompt.txt`), C (pairwise judge prompt, `analyze.py`), D (individual scoring prompts, `top_ideas.py`), E (data and code). Generated by `paper/build_paper.py`.
- **Check 3.8 against your records.** I reconstructed what was planned, and when, from our working sessions: R and C were designed with A and B, while medium and xhigh, B-high vs A-low, and the tail analysis came later. Correct anything that doesn't match your notes; reviewers weigh this section.
- **The 45% non-inferiority margin** and the H1 wording come from the results document. Make sure they match the hypotheses in the introduction.
- **The total of about 8.6 million tokens** is the sum of mean tokens per call times calls per arm. Replace it with the exact sum from `results/calls.csv`, and add the dollar cost at list price if you want to report it.
- **Graph construction.** State who built the graph and how long it took, and whether it was checked by anyone else. A reviewer will ask whether the slicing rule depends on choices made when building the graph.
