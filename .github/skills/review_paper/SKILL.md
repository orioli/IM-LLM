---
name: review_paper
description: "Review scientific paper content — from a single paragraph or section up to the entire manuscript, appendices, and LaTeX sources — for structure, academic style, scientific validity, methodology, statistical rigor, mathematical notation, citations/BibTeX, reproducibility, and LaTeX source hygiene. Use when: reviewing, auditing, or proofreading scientific papers, conference/journal submissions, or LaTeX manuscripts."
---

# Scientific Paper Review

Paper-agnostic review procedure, scalable from a single paragraph to the entire manuscript (main text, appendices, and LaTeX source files).

## Setup

Two independent choices define what gets reviewed. **If either is ambiguous from the user's request, ask before proceeding** — do not guess.

1. **Unit** — the content boundary:
   - **Paragraph / subsection** — the specific passage the user points to (or the surrounding section if they only point at a line).
   - **Section** — one paper section (e.g., Abstract, Introduction, Related Work, Method, Results, Discussion, Appendix) plus its associated tables, figures, code, and LaTeX sources.
   - **Whole paper** — the entire manuscript, including supplementary materials, appendices, references, and build pipeline.
2. **Range** — how much of that unit to check:
   - **Latest saved changes** — uncommitted working-tree edits: `git diff -- <paths>` (add `--staged` too if anything is staged). Review only the changed hunks plus surrounding context.
   - **Last commit(s)** — `git log -1` or `git diff HEAD~<n>..HEAD -- <paths>`; ask how many commits if not stated. Review only the changed hunks plus surrounding context.
   - **Since a given date/commit/tag** — `git diff <ref>..HEAD -- <paths>`. Review only the changed hunks plus surrounding context.
   - **Full** — the entire current content of the unit, ignoring history.

For any range narrower than "full", still read enough surrounding context to judge flow and argumentation, and still run the full build/compilation step (§13) — changes can introduce dangling cross-references or compilation warnings even when the diff is small.

Also establish, from the paper template, venue guidelines (e.g., NeurIPS, ICML, ACL, IEEE, ACM, Nature/Science formats), or project instructions:

3. **Target venue & skeleton** — expected section structure, page limits, double-blind anonymity requirements, and supplementary material format.
4. **Style & conventions** — target audience, scholarly tone, language/locale (e.g., US vs UK English), and notation standard.

Read the full unit under review (not just isolated diff hunks) before commenting, so feedback accounts for surrounding context. Apply only uncontroversial fixes (typos, notation errors, unambiguous BibTeX/LaTeX formatting); ask before anything touching author voice, empirical claims, structural reorganization, or methodology interpretation. For a paragraph/section-level review, skip checks that don't apply at that granularity and note which ones were skipped.

## Checks

### 1. Structure & Argumentation Flow
- Standard paper anatomy present and coherent: Abstract, Introduction, Related Work / Background, Method / Experimental Design, Results, Discussion, Limitations / Ethics, Conclusion, Appendices.
- Abstract is self-contained: covers background/motivation, research gap, proposed approach, key quantitative results with metrics, and main takeaways.
- Introduction clearly establishes: (a) real-world / theoretical problem, (b) why existing solutions fall short, (c) specific contributions explicitly listed (e.g., bulleted list of contributions), and (d) paper organization roadmap.
- Logical transitions between sections and paragraphs; every section opens with purpose and closes with a synthesis or bridge to the next section.
- Flag deviations or missing sections per the venue skeleton; never restructure without author consent.

### 2. Style & Academic Tone
- Objective, precise, and concise scholarly register; eliminate promotional fluff and hyperbole ("revolutionary", "groundbreaking", "vastly superior", "game-changing").
- Appropriate epistemic calibration: balanced hedging vs confident claims. Empirical findings must match the strength of the evidence (e.g., do not claim causal superiority when only observational correlation or exploratory yield was tested).
- Active vs passive voice: use active voice for author choices ("We design...", "We evaluate...") and passive voice where the object is the primary focus.
- Preserve authorial voice while streamlining verbose constructions.

### 3. Grammar, Usage & Scientific Typography
- Fix grammar, syntax, and typos without altering scientific meaning.
- **Tense conventions**:
  - Past tense for specific completed experiments, data collection, and author procedures ("We evaluated...", "Model X achieved...").
  - Present tense for general scientific facts, persistent truths, and manuscript navigation ("Equation 3 defines...", "Table 2 summarizes...").
- Terminology consistency: ensure terms, variable names, and condition labels (e.g., condition names, model variants) do not drift across sections.
- Scientific typography:
  - Correct dashes: hyphen (`-`) for compound words, en-dash (`--`) for ranges (`pp.~12--18`, `10--20~tokens`), em-dash (`---`) for parenthetical thoughts.
  - Proper quotation marks in LaTeX (``` ``quote'' ``` instead of `""`).
  - Non-breaking ties (`~`) before citations and references (`Section~\ref{sec:methods}`, `Table~\ref{tab:results}`, `\cite{smith2024}`).
  - Numbers and units formatted consistently with appropriate spacing (e.g., `$100\text{k}$ tokens`, `$50\,\text{ms}$` or `\SI{50}{\milli\second}`).

### 4. Cross-References & Floats
- Every reference to sections, subsections, figures, tables, equations, theorems, algorithms, and appendices resolves to an existing label.
- Consistent capitalization and formatting (`Section~\ref{...}`, `Figure~\ref{...}`, `Table~\ref{...}`, `Equation~\eqref{...}`).
- Floats (tables and figures) referenced in the text before or near their visual placement.
- Appendix references clearly indicate whether material is in the main paper appendix or external supplementary file.

### 5. Figures, Plots & Tables
- **Captions**: self-contained and descriptive; reader can understand the takeaway, metrics, axes, and error bars without jumping back and forth to body text.
- **Plots & Figures**:
  - Readable font sizes (comparable to body text when scaled).
  - Clear axes, units, legends, and aspect ratios.
  - High resolution / vector graphics (PDF/SVG/EPS preferred over raster PNG/JPEG).
  - Colorblind-friendly palettes and distinguishable line styles/markers.
  - Error bars and uncertainty clearly specified in caption and legend (e.g., $95\%$ bootstrap CI, $\pm 1$ SD, IQR).
- **Tables**:
  - Clean professional typesetting (use `booktabs`: `\toprule`, `\midrule`, `\bottomrule`; avoid vertical rules and double horizontal lines).
  - Consistent decimal alignment and significant figures across comparison rows.
  - Best/runner-up results clearly indicated (e.g., **bold** for best, *italic* / underlined for second best) with notes defining what bolding indicates.

### 6. Citations, Related Work & BibTeX
- Every external empirical claim, dataset, tool, model, or baseline is properly cited.
- Proper citation commands: parenthetical citations (`\citep{...}` or `\cite{...}`) vs textual/narrative citations (`\citet{...}`).
- BibTeX integrity:
  - Clean keys, complete entries (authors, title, venue/journal, year, pages/volume or arXiv identifier).
  - Proper noun protection with curly braces in titles (e.g., `{GPT-4}`, `{BERT}`, `{Monte Carlo}`).
  - No duplicate BibTeX entries or hallucinated citation keys.
- Related work is balanced, gives fair credit to prior art, and clearly distinguishes current contribution from baseline approaches.

### 7. Scientific Methodology, Hypotheses & Statistical Rigor
- **Hypotheses & RQs**: clearly formulated research questions ($RQ_1, RQ_2, \dots$) or pre-registered hypotheses ($H_1, H_2, \dots$).
- **Confirmatory vs Exploratory distinction**: explicit separation between pre-planned confirmatory statistical tests and post-hoc / exploratory metrics discovered during analysis.
- **Statistical reporting standards**:
  - Report effect sizes, confidence intervals, sample sizes ($N$), test statistics, degrees of freedom, and exact $p$-values (avoid bare $p < 0.05$ or $p = 0.000$).
  - Correct for multiple comparisons where applicable (e.g., Bonferroni, FDR/Benjamini-Hochberg).
- **Baselines & Fair Comparison**:
  - Controlled confounding variables (e.g., compute budget, prompt length, token effort, context window size).
  - Identical tuning / evaluation protocols across all tested conditions.
- **Construct Validity & Human Evaluation**:
  - For LLM-as-a-judge or human evaluations: report inter-rater reliability metrics (Fleiss' $\kappa$, Krippendorff's $\alpha$, Spearman's $\rho$).
  - Evaluate and control for known evaluation biases (e.g., position bias, length/verbosity bias, self-enhancement bias).
  - Transparent rubrics and rater qualifications.

### 8. Mathematical Notation & Quantitative Precision
- Strict mathematical notation consistency: every symbol and variable defined upon first use.
- Notation convention maintained across main text, equations, tables, and appendices (e.g., vectors bold lowercase $\mathbf{x}$, matrices bold uppercase $\mathbf{X}$, sets calligraphic $\mathcal{S}$).
- Equations numbered only if referenced in text (or use unnumbered `equation*` / `\[ ... \]`).
- Quantitative consistency: verify numbers in text match numbers in tables, figures, abstract, and codebase outputs exactly. Check rounding and significant figures.

### 9. Code, Data & Reproducibility
- All referenced scripts, configuration files, and data paths exist in the workspace/repository.
- Code snippets in text match the real execution scripts and actual APIs.
- Execution commands described in Section/Appendix (e.g., CLI reproduction steps) work end-to-end with documented default arguments.
- Document random seeds, environment dependencies, model checkpoints/versions, and prompt templates.

### 10. Acronyms & Nomenclature
- Defined on first appearance in Abstract and re-defined on first appearance in the main body: *Full Name (ACR)*.
- Standard domain nomenclature maintained; avoid unnecessary bespoke acronyms that hinder readability.
- Consistent capitalization of technical names throughout.

### 11. Ethical Considerations, Limitations & Broader Impact
- Limitations section clearly delineates boundary conditions, failure modes, potential biases, and threats to internal/external validity.
- Broader impact, safety, data privacy, and ethical considerations addressed where required by venue guidelines.

### 12. LaTeX Source & Document Hygiene
Review LaTeX source files (`.tex`, `.bib`, `.sty`, `.cls`) for code quality, formatting standards, and compilation cleanliness:
- **Modular Structure**: Clean file splitting (e.g., `main.tex`, `sections/01_intro.tex`, `references.bib`, `figures/`) without redundant preamble re-definitions.
- **Math Markup**:
  - Use `amsmath`/`mathtools` standard environments (`equation`, `align`, `gather`, `multline`) instead of deprecated TeX primitives (`$$...$$`, `eqnarray`).
  - Standard mathematical operators formatted with `\DeclareMathOperator` or `\operatorname{...}` (e.g., `\operatorname{argmax}`, `\log`, `\exp` instead of italicized $argmax$, $log$).
  - Proper delimiter sizing using `\left( ... \right)` or explicit `\bigl( ... \bigr)` to prevent mismatched parenthetical heights.
- **Floats & Layout**:
  - Avoid hardcoded formatting hacks (`\vspace{-10pt}`, `\newpage`, `\clearpage`) unless adjusting final camera-ready spacing.
  - Proper float placement specifiers (`[t]`, `[tb]`, `[!t]`), avoiding excessive `[h]` or `[H]` that disrupt document flow.
  - Table environments built with `booktabs` (`\toprule`, `\midrule`, `\bottomrule`) and `\resizebox` / `tabularx` used appropriately without distorting font size relative to body text.
- **Package & Macro Hygiene**:
  - Check for conflicting, redundant, or obsolete packages (e.g., `times`, `epsfig`, `a4wide`, `subcaption` vs `subfig`).
  - Verify all custom macros (`\newcommand`, `\def`) are documented and do not override standard LaTeX/AMS primitives.
- **Draft Comments & Anonymity**:
  - Search for and flag lingering draft comments, notes, and placeholders (`TODO`, `FIXME`, `\todo{}`, `\xxx{}`, `\authornote{}`).
  - For double-blind submissions: ensure no de-anonymizing author names, affiliations, grant numbers, GitHub URLs, or self-revealing citations ("In our previous paper [1]...").
- **Compilation Warnings & Errors**:
  - No fatal compilation errors.
  - Zero unresolved references (`LaTeX Warning: Reference ... undefined` -> `??`).
  - Zero unresolved citations (`LaTeX Warning: Citation ... undefined` -> `[?]`).
  - Inspect log for severe `Overfull \hbox` (text or math spilling into margins) and `Underfull \hbox` (bad whitespace stretching).

### 13. Build, Compilation & Verification
Run the exact build pipeline used for the paper:
```bash
latexmk -pdf main.tex   # or pdflatex / xelatex / bibtex pipeline
```
- Compilation completes with return code 0.
- Verify generated PDF: check page count against venue limit, inspect margin alignments, and verify vector graphics render properly without font embedding issues.

## Output

Structure findings as a comprehensive Scientific Paper Review Report:

1. **Executive Summary & Scope**: Overview of review unit, range, and high-level assessment of paper readiness and contribution clarity.
2. **Major Issues (Methodology, Statistical Rigor & Scientific Validity)**:
   - Experimental design, baseline fairness, hypothesis support vs post-hoc claims.
   - Construct validity, measurement biases, reproducibility gaps.
   - Severity, impact, and concrete recommendations.
3. **Minor Issues (Style, Typography, Citations & Nomenclature)**:
   - Citations / BibTeX corrections, cross-reference fixes, mathematical notation consistency, terminology alignment.
4. **LaTeX & Source Hygiene**:
   - Overfull boxes, float placement, package conflicts, draft comment cleanup, compilation warnings.
5. **Section-by-Section Line Notes**:
   - File and line references (`[file.tex](file.tex#L12)`), exact quoted text, severity (`blocker` / `should-fix` / `suggestion`), and proposed fix.
6. **Action Items & Author Decisions**:
   - Distinguish applied uncontroversial edits from substantive decisions requiring author input.
