### Explore the product graph

![Microwave innovation matrix demo](demoAB.gif)
![Microwave innovation matrix demo](innovation_matrix_demo.gif)


# Is less more? Narrow context in LLM ideation with product graphs

Code, data and paper for **"Is less more? Narrow context is more efficient than full context for generative ideation with product graphs"**.

A hand-built innovation matrix of a microwave oven (123 nodes, 246 typed edges) is given to `claude-haiku-5-5` in four forms:

| Condition | What the prompt contains |
| --- | --- |
| **A**, full graph | the whole innovation matrix |
| **B**, market-need slice | the vertical slice for the target market need |
| **R**, random slice | a random slice of the same size as B |
| **C**, no graph | the product and the market need only |

The model applies the SUBSTITUTE operator to 13 market needs at four levels of thinking effort (580 calls, 2,892 ideas). `claude-sonnet-5-5` judges the ideas blind, both as whole sets (pairwise) and one by one. The main measure is **yield**: top ideas (score ≥ 4.0, the top 12%) per 100k tokens.

**Main result.** The market-need slice at medium effort yields 8.8 top ideas per 100k tokens, about three times the full graph at any effort, and beats it on 10 of 13 market needs. Per token, the full graph is less efficient than no graph at all.

![Yield per arm: top ideas per 100k tokens, with the no-graph control as a dashed line](results/charts/8c_yield_spread_annotated.png)

*Top ideas per 100k tokens for each arm (box = middle 50% of 2,000 bootstrap slopes). Arms left of the dashed line, including every full-graph arm, find top ideas less efficiently than giving the model no graph at all.*



## Repository layout

| Path | Contents |
| --- | --- |
| `microwave_base_graph.yaml` | the innovation matrix (product graph) |
| `slicer.py`, `slices/` | market-need slices (B) and size-matched random slices (R), with `manifest.csv` |
| `template_prompt.txt` | the generation prompt |
| `KG_informed_brainstorm_AB_Test.py` | runs the generation calls |
| `analyze.py` | pairwise set judging and summaries |
| `top_ideas.py` | individual idea scoring (quality; `--rubric patent` for patentability) and the ranked idea list |
| `charts.py`, `tail_charts.py`, `figure_innovation_matrix.py` | figures |
| `human_check.py` | stratified sample for human raters, and agreement statistics |
| `runs/` | every generation call (prompt metadata, raw response, token counts) |
| `results/` | judge outputs, tables, charts, results write-up |
| `persona_as_factor/` | exploratory follow-up: three personas × B, C × 3 market needs × 2 efforts |
| `paper/` | LaTeX source of the paper (`main.tex`; built from Markdown drafts by `build_paper.py`) |

## Reproducing

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...          # never commit this

# 1. inspect the prompts without calling the API
python KG_informed_brainstorm_AB_Test.py --dry-run

# 2. generate (example: the high-effort arms)
python KG_informed_brainstorm_AB_Test.py --conditions A B R C --effort high --reps 5 \
       --max-tokens 48000 --out runs/rq1_full.jsonl

# 3. judge, score and summarise
python analyze.py judge  ...           # see python analyze.py --help
python analyze.py stats
python top_ideas.py score
python top_ideas.py report

# 4. figures
python charts.py
python tail_charts.py
python figure_innovation_matrix.py
```

Every number in the paper's results is regenerated from `runs/` and `results/` by steps 3 and 4. Re-running the generation produces new samples, so individual ideas will differ.

## Citation

Paper under submission; preprint link to follow.

## License

[To be chosen: for example MIT for the code, and CC BY 4.0 for the data and paper.]
