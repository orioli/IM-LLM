# Paper (LaTeX)

Built from the Markdown drafts in this folder by `build_paper.py` (pandoc). Edit the `.md` files, then:

```
python build_paper.py          # writes body.tex, appendix.tex, unicode_chars.tex, authors_notes.md
latexmk -pdf main.tex          # or upload the folder to Overleaf (compiler: pdfLaTeX)
```

`main.tex` holds the title, authors and abstract; `references.bib` the bibliography (Tchirsky entry is a placeholder).
`authors_notes.md` collects the "Notes for the authors" from the drafts; they are not in the paper.

Figures go in `figures/`. From the project root:

```
cp results/charts/{1_tokens_per_call,2_win_rates,3_score_diff_A_minus_B,4_cost_vs_quality,5_context_ladder,6_top_idea_rate,7_chance_vs_budget,8_top_ideas_vs_tokens,8c_yield_spread_annotated,9_slice_size_effect}.png paper/figures/
cp persona_as_factor/results/charts/11_persona_effect.png paper/figures/
```

plus the Brown Book innovation-matrix figure as `figures/brown_book_innovation_matrix.png`.
Missing figures compile as framed placeholders.
