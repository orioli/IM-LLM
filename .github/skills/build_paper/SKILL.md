---
name: build_paper
description: "Build the scientific paper PDF from LaTeX source files, regenerating analysis tables, figures/charts via Python virtual environment (.venv), syncing figures, and compiling with Tectonic or PDFLaTeX, validating style and PDF integrity against Overleaf/canonical builds."
---

# Paper Build Skill

Standardized workflow to build, compile, verify, and validate the scientific paper manuscript and its associated data tables and visual figures.

## Overview & Architecture

The paper build pipeline consists of four modular stages:
1. **Python Virtual Environment (`.venv`)**: Executes data analysis, metrics aggregation, and figure generation scripts.
2. **Analysis & Figure Generation**: Produces all summary CSVs, ranked tables, and visualization charts in `results/charts/` and `persona_as_factor/results/charts/`.
3. **Figure Syncing**: Copies the latest vector/raster figures into `paper/figures/`.
4. **LaTeX Compilation & Verification**: Compiles `paper/main.tex` using `tectonic` (or `pdflatex` + `bibtex`) to generate `paper/main.pdf`, followed by automated visual and structural validation.

---

## Quick Start (Automated Build)

To execute the entire end-to-end pipeline in a single step from workspace root:

```bash
python3 .github/skills/build_paper/build_paper.py
```

### Build Options
- **Fast compile (LaTeX only, skip data/charts)**:
  ```bash
  python3 .github/skills/build_paper/build_paper.py --skip-stats --skip-charts
  ```
- **Sync PDF directly to `tmp/paper_latex.pdf`**:
  ```bash
  python3 .github/skills/build_paper/build_paper.py --copy-to-tmp
  ```
- **Use PDFLaTeX engine instead of Tectonic**:
  ```bash
  python3 .github/skills/build_paper/build_paper.py --engine pdflatex
  ```

---

## Detailed Step-by-Step Procedure

### 1. Environment Setup

Ensure the Python virtual environment is set up with all project dependencies:

```bash
# In workspace root:
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

*Required packages:* `anthropic`, `pyyaml`, `matplotlib`, `numpy`, `pydantic`.

### 2. Data Processing & Result Aggregation (Optional / when run logs change)

When new experimental logs are added to `runs/`:

```bash
# Aggregate cost, validity, and cell statistics:
.venv/bin/python analyze.py stats --logs runs/rq1_full.jsonl

# Compute pairwise win rates and sign test summaries:
.venv/bin/python analyze.py summary --logs runs/rq1_full.jsonl

# Score individual ideas and generate ranking reports:
.venv/bin/python top_ideas.py report --logs runs/rq1_full.jsonl
```

### 3. Chart & Figure Generation

Regenerate all publication-quality figures:

```bash
# Main study charts and innovation matrix diagrams:
.venv/bin/python figure_innovation_matrix.py
.venv/bin/python charts.py
.venv/bin/python tail_charts.py

# Persona follow-up analysis charts:
(cd persona_as_factor && ../.venv/bin/python persona_analysis.py)
```

Generated outputs:
- `results/charts/0_innovation_matrix_M8.{png,pdf}`
- `results/charts/1_tokens_per_call.png`
- `results/charts/2_win_rates.png`
- `results/charts/3_score_diff_A_minus_B.png`
- `results/charts/4_cost_vs_quality.png`
- `results/charts/5_context_ladder.png`
- `results/charts/6_top_idea_rate.png`
- `results/charts/7_chance_vs_budget.png`
- `results/charts/8_top_ideas_vs_tokens.png`
- `results/charts/8b_yield_spread.png`
- `results/charts/8c_yield_spread_annotated.png`
- `results/charts/9_slice_size_effect.png`
- `persona_as_factor/results/charts/10_persona_yield.png`
- `persona_as_factor/results/charts/11_persona_effect.png`
- `persona_as_factor/results/charts/11b_persona_by_representation.png`

### 4. Sync Figures to LaTeX Source Directory

Copy all freshly rendered charts into `paper/figures/`:

```bash
cp results/charts/* paper/figures/ 2>/dev/null || true
cp persona_as_factor/results/charts/* paper/figures/ 2>/dev/null || true
```

### 5. Compile LaTeX Document

Compile using `tectonic` (self-contained, handles BibTeX and multi-pass convergence automatically):

```bash
cd paper
tectonic main.tex
cd ..
```

*Alternative (Traditional TeX Live toolchain):*
```bash
cd paper
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
cd ..
```

---

## Quality & Integrity Verification

Always verify the compiled `paper/main.pdf`:

### 1. Document Structure & Page Count
```bash
pdfinfo paper/main.pdf
```
Check that page count, A4 dimensions ($595.28 \times 841.89\text{ pt}$), and metadata are intact (expected page count: 44 pages).

### 2. Missing Figure Placeholders Check
LaTeX code in `body.tex` and `appendix.tex` includes conditional fallbacks rendering `missing: <path>` boxes if an asset is not found. Ensure zero missing assets:
```bash
pdftotext paper/main.pdf - | grep "missing:"
```
*Expected result:* Empty (no occurrences).

### 3. Broken Citations & Cross-References Check
Check for unresolved `??` citation markers or section references:
```bash
pdftotext paper/main.pdf - | grep -E '\?\?'
```
*Expected result:* Empty (no occurrences).

### 4. Style & Typography Match Check
The canonical reference build is located at `tmp/paper_latex.pdf` (built with Overleaf). Verify that the style matches:
- **Fonts**: Latin Modern (`\usepackage{lmodern}` with T1 encoding and `microtype`).
- **Margins**: 2.5 cm on all edges (`\usepackage[margin=2.5cm]{geometry}`).
- **Document Class**: `\documentclass[11pt,a4paper]{article}`.
- **Tables**: Booktabs formatting with `longtable` and `calc`.
- **Bibliography**: Natbib author-year format (`\bibliographystyle{plainnat}`).

To visually compare rendered pages against `tmp/paper_latex.pdf`:
```bash
pdftoppm -png -r 150 -f 1 -l 2 tmp/paper_latex.pdf /tmp/ref_page
pdftoppm -png -r 150 -f 1 -l 2 paper/main.pdf /tmp/build_page
```
