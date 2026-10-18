---
name: review
description: "Review book content — from a single paragraph up to the whole book — for structure, style, grammar, cross-references, citations, factual accuracy, question/solution completeness, code consistency, and translation sync. Use when: reviewing, auditing, or proofreading text, or checking consistency between language versions."
---

# Book Review

Book-agnostic review procedure, scalable from a paragraph to the whole book.

## Setup

Two independent choices define what gets reviewed. **If either is ambiguous from the user's request, ask before proceeding** — do not guess.

1. **Unit** — the content boundary:
   - **Paragraph / section** — the specific passage the user points to (or the surrounding section if they only point at a line).
   - **Chapter** — one chapter file (plus its code/tests/translation counterparts).
   - **Whole book** — every chapter.
2. **Range** — how much of that unit to check:
   - **Latest saved changes** — uncommitted working-tree edits: `git diff -- <paths>` (add `--staged` too if anything is staged). Review only the changed hunks plus surrounding context.
   - **Last commit(s)** — `git log -1` or `git diff HEAD~<n>..HEAD -- <paths>`; ask how many commits if not stated. Review only the changed hunks plus surrounding context.
   - **Since a given date/commit/tag** — `git diff <ref>..HEAD -- <paths>`. Review only the changed hunks plus surrounding context.
   - **Full** — the entire current content of the unit, ignoring history.

For any range narrower than "full", still read enough surrounding context to judge flow, and still run the full build/test step (§14) — changes can break things non-locally even when the diff is small.

Also establish, from `AGENTS.md`, the style guide, or an already-finished chapter:

3. **Canonical chapter skeleton** — expected section structure.
4. **Style guide** — audience, tone, language and locale.

Read the full unit under review (not just isolated diff hunks) before commenting, so feedback accounts for surrounding context. Apply only uncontroversial fixes; ask before anything touching voice, structure, or claims. For a paragraph/section-level review, skip checks that don't apply at that granularity (e.g. whole-chapter structure, index terms) and note which ones were skipped and why.

## Checks

### 1. Structure
Sections present, ordered, and labelled per the book's skeleton. Flag deviations; never restructure silently.

### 2. Style
- Tone, register, and difficulty consistent with the rest of the book.
- No uninterrupted stretch of text longer than ~2 pages without a break.
- Each subsection opens by linking to the previous one and closes with a bridge to the next.
- Preserve existing anecdotes, humour, and authorial voice.

### 3. Grammar and usage
- Fix grammar and typos without altering style.
- Consistent terminology within the chapter and across chapters.
- Consistent number and decimal-separator formatting in text, math, and figures.
- Idiomatic phrasing: flag correct-but-unnatural wording, calques, wrong prepositions.
- Punctuation: parentheticals closed on both sides, correct dashes, ellipses, and locale-appropriate quotation marks.
- Dialogue and internal monologue match the character's voice and the scene's register.
- Suggest (don't apply) rewrites that would make the text more engaging.

### 4. Cross-references
- Every section/figure/table reference resolves to an existing target.
- Forward references in future tense, backward references in past tense.
- A reference to a distant figure or table also names its section, so the reader knows where to look.

### 5. Figures and diagrams
Every image path exists; every generated diagram has its source file; captions are meaningful and in the chapter's language.

### 6. Citations
Every citation key exists in the bibliography; every empirical claim is sourced; keep inline citations minimal and prefer the further-reading section.

### 7. Questions and solutions
- Every question has exactly one matching solution, in the same order and the same file.
- Use plain ordered lists in the source and let the build tooling generate numbering; never hardcode chapter numbers.
- Solutions concise (1–4 sentences); hints or pseudocode for coding tasks.

### 8. Technical explanations and factual accuracy
- Concepts explained before use, or carrying an explicit forward reference.
- Theory sections: strict ordering — only prior concepts, assumed background (with a short refresher), or inline definitions.
- Practical/introductory sections: early mentions are acceptable with an intuitive gloss or a forward reference, ideally both.
- Verify dates, attributions, mathematical and algorithmic properties, quantitative claims, and API/version statements against sources.
- Invoke the `ground-truth-review` skill when auditing factual, mathematical, or empirical assertions against `references/`.
- Both **Contradicted** and **Not found** findings from ground-truth review are classified as **`blocker`** severity in the review output.
- Report factual errors with the corrected value and source; never fix them silently.

### 9. Markup
Correct use of the book's callout/admonition environments. Collect all `TODO`/`FIXME` comments into the report.

### 10. Acronyms
- Defined on first appearance as *Full Name (ACR)* or *ACR (Full Name)*, never used before definition — including in summary boxes and headings.
- Never redefined with a different expansion.
- Flag as **forced** (propose spelling it out) when two or more hold: used fewer than ~4–5 times; all uses clustered in one section; the abbreviation saves nothing over the plain term; not standard vocabulary for the target audience.

### 11. Code consistency
- Every script referenced in the text exists, and the prose matches what it actually does.
- Inline snippets may be excerpted or simplified but must not contradict the full script's logic or API.
- **Inline snippets are usually not executed by CI.** A passing build does not mean a snippet runs. Trace each snippet's calls against the tested source, or run it. Watch for "readable" simplifications the real API does not support (e.g. an operator the library doesn't implement) — verify method-level compatibility, not just mathematical equivalence.
- Comments in embedded samples must be in the chapter's language, even if the source scripts use another.
- If code is mirrored to another repo or package, confirm the mirrored copy matches the current tested version.

### 12. Index
Add terms introduced by the chapter; drop terms whose content was removed.

### 13. Translation parity
If another language version exists:
- **Structure** — same headings in the same order with the same anchors; same count of questions, figures, tables, code blocks, cross-references, and citations.
- **Content** — every paragraph has a counterpart, nothing silently added or dropped; if the source changed after translation, list the sections needing re-translation. Solutions must match.
- **Assets** — translated diagram sources and localized user-facing strings in code output exist.
- **Quality** — established target-language technical vocabulary, natural prose (not translationese), anecdotes and humour preserved or adapted.

### 14. Build and test
Run exactly what CI runs (check the CI workflow and `Makefile`): typically a full render plus the test suite. The review is not complete until these pass cleanly.

## Output

Group findings by check. For each: file and line reference, severity (blocker / should-fix / suggestion), and a proposed correction. List applied fixes separately from items awaiting the author's decision. For a whole-book review, group by chapter first, then by check, and add a short cross-chapter summary (recurring issues, terminology drift, index/translation gaps spanning multiple chapters).
