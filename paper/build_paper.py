"""Merge the Markdown drafts into one paper and convert it to LaTeX.

  python build_paper.py        # writes paper.md, body.tex, authors_notes.md; then run latexmk -pdf main.tex

Inputs (next to this script or one level up): introduction.md, methods.md, results.md,
conclusion_future_work.md, appendix_innovation_matrix.md, template_prompt.txt, analyze.py, top_ideas.py.
Citations [@key] become \\citep{key} (pandoc --natbib) against references.bib.
"""
import ast
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent


def read(name):
    for d in (HERE, SRC):
        if (d / name).exists():
            return (d / name).read_text(encoding="utf-8")
    raise FileNotFoundError(name)


NOTES = []


def strip_notes(text, source):
    """Move 'Notes for the authors' blocks out of the paper into authors_notes.md."""
    m = re.search(r"\n---\s*\n+### Notes for the authors.*", text, flags=re.S)
    if m:
        NOTES.append(f"## From {source}\n" + m.group(0).split("\n", 3)[-1].strip() + "\n")
        text = text[: m.start()]
    return text.rstrip() + "\n"


def headings(text, shift=0, drop_numbers=True):
    out = []
    for line in text.splitlines():
        m = re.match(r"^(#+)\s+(.*)$", line)
        if m:
            level = max(1, len(m.group(1)) + shift)
            title = m.group(2)
            if drop_numbers:
                title = re.sub(r"^\d+(\.\d+)*\s+", "", title)
            line = "#" * level + " " + title
        out.append(line)
    return "\n".join(out) + "\n"


def figure(path, label, caption, width="\\textwidth"):
    """Raw LaTeX figure; draws a framed placeholder if the image file is not there yet."""
    return (f"\n```{{=latex}}\n\\begin{{figure}}[tbp]\n\\centering\n"
            f"\\IfFileExists{{{path}}}{{\\includegraphics[width={width}]{{{path}}}}}"
            f"{{\\fbox{{\\parbox[c][5cm][c]{{0.9\\textwidth}}{{\\centering\\small missing: \\texttt{{\\detokenize{{{path}}}}}}}}}}}\n"
            f"\\caption{{{caption}}}\n\\label{{{label}}}\n\\end{{figure}}\n```\n")


# figures shown in the paper; other charts stay in the repository as supplementary charts
MAIN_FIGS = {
    "1": "fig:tokens", "2": "fig:winrates", "3": "fig:scorediff", "4": "fig:costquality", "5": "fig:ladder",
    "6": "fig:toprate", "7": "fig:budget",
    "8": "fig:yield", "8b": "fig:spread", "8c": "fig:spread", "9": "fig:slicesize", "11": "fig:persona",
}


def chart_refs(text):
    def rep(m):
        word, num = m.group(1), m.group(2)
        if num in MAIN_FIGS:
            return ("Figure" if word[0].isupper() else "Figure") + f" \\ref{{{MAIN_FIGS[num]}}}"
        return ("Supplementary chart" if word[0].isupper() else "supplementary chart") + f" {num}"
    text = re.sub(r"\b([Cc]hart)s? (\d+[a-c]?)\b", rep, text)
    text = re.sub(r"(Figure \\ref\{[^}]+\}) \(`[^`]+\.png`\)", r"\1", text)
    text = re.sub(r"(Figure \\ref\{[^}]+\}; )Figure \\ref\{fig:spread\}, `[^`]+`, marks", r"\1the annotated version marks", text)
    return text


MARKET = [
    (r"(?<!market )(?<!market-)\bneed slice", "market-need slice"),
    (r"(?<!market )\bneed's", "market need's"),
    (r"\b(per|within|each|every|one|single|target|that|this|the) need\b(?! slice)", r"\1 market need"),
    (r"\b(\d+|two|three|six|all|the|these|those|other|easy|easier|small|large|13) needs\b", r"\1 market needs"),
    (r"\bneed by need\b", "market need by market need"),
    (r"\bNeeds differ\b", "Market needs differ"),
    (r"\bneeds\b(?= (differ|whose|with|here))", "market needs"),
    (r"\b(same|a|that|pick a|for) need\b(?![- ]slice)", r"\1 market need"),
    (r"\b(over|some|decided|hardest|target|xhigh) needs\b", r"\1 market needs"),
    (r"(?<!market-)\bneed-slice\b", "market-need-slice"),
    (r"(?<!market-)\bneed-dependent\b", "market-need-dependent"),
    (r"\bFor need \\\(", r"For market need \\("),
    (r"(?<!market-)\bneed-averaged\b", "market-need-averaged"),
    (r"\b([Pp])er-need\b", r"\1er-market-need"),
    (r"\b(and|by|condition,) need\b", r"\1 market need"),
    (r"\b(Across|matched|equal) needs\b", r"\1 market needs"),
]


def market_need(text):
    """Say 'market need' wherever the paper means one; skip fenced code and raw LaTeX blocks."""
    def fix(t):
        for pat, rep in MARKET:
            t = re.sub(pat, rep, t)
        return t.replace("market market-need", "market-need").replace("market market need", "market need").replace("target market market", "target market")
    out, pos = [], 0
    for m in re.finditer(r"```(\{=latex\})?\n.*?\n```", text, flags=re.S):
        out.append(fix(text[pos:m.start()]))
        out.append(fix(m.group(0)) if m.group(1) else m.group(0))   # captions yes, prompts no
        pos = m.end()
    out.append(fix(text[pos:]))
    return "".join(out)


def size_tables(text):
    """Set each pipe table's separator dashes in proportion to its columns' content, so that pandoc gives
    wide tables proportional column widths (narrow tables keep natural widths)."""
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|(\s*:?-+:?\s*\|)+\s*$", lines[i + 1]):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            rows = [[c.strip() for c in l.strip().strip("|").split("|")] for k, l in enumerate(lines[i:j]) if k != 1]
            n = len(rows[0])
            def vis(c):
                return len(re.sub(r"[*`\\]", "", c))
            w = [max(3, min(45, max([int(vis(rows[0][c]) * 0.6)] + [vis(r[c]) for r in rows[1:] if c < len(r)]))) for c in range(n)]
            seps = [c.strip() for c in lines[i + 1].strip().strip("|").split("|")]
            new = []
            for c in range(n):
                left = seps[c].startswith(":") if c < len(seps) else False
                right = seps[c].endswith(":") if c < len(seps) else False
                new.append((":" if left else "") + "-" * w[c] + (":" if right else ""))
            out += [lines[i], "|" + "|".join(new) + "|"] + lines[i + 2:j]
            i = j
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def build():
    intro = strip_notes(read("introduction.md"), "introduction.md")
    intro = re.sub(r"^# .*?\n\n\*.*?\*\n\n", "", intro, flags=re.S)        # title and subtitle go to main.tex
    intro = headings(intro, shift=-1)

    methods = strip_notes(read("methods.md"), "methods.md")
    methods = headings(methods, shift=-1)
    methods = re.sub(r"> \*\*Figure 1\.\*\*.*?\n", lambda _m, _f=figure(
        "figures/brown_book_innovation_matrix.png", "fig:im_brownbook",
        "An innovation matrix as drawn in the workshop material \\citep{berengueres2014}.", "0.8\\textwidth"): _f, methods)
    methods = re.sub(r"> \*\*Figure 2\.\*\*.*?\n", lambda _m, _f=figure(
        "figures/0_innovation_matrix_M8.pdf", "fig:im_microwave",
        "The microwave innovation matrix used in the experiment. Rows are the layers, bottom to top, with "
        "constraints below and actors above. Filled nodes and edges are the need slice for M8, \\emph{know when "
        "food is ready} (25 nodes, 32 edges): what the model sees in condition B for that need, against the whole "
        "graph in condition A."): _f, methods)
    methods = methods.replace("(Figure 1)", "(Figure \\ref{fig:im_brownbook})").replace(
        "(Figure 2;", "(Figure \\ref{fig:im_microwave};")

    res = read("results.md")
    res = re.sub(r"^# .*?\n\nFull run.*?\n\n", "", res, flags=re.S)
    res = res.replace("**Headline.**", "## Summary\n\n", 1)
    files = ""
    m = re.search(r"\n## Files\n.*", res, flags=re.S)
    if m:
        files, res = m.group(0), res[: m.start()]
    res = chart_refs(res)
    res = res.replace("Figure \\ref{fig:toprate}.\n", "Figure \\ref{fig:toprate} shows the rates with their intervals.\n")
    res = res.replace("Figure \\ref{fig:budget}.\n", "Figure \\ref{fig:budget} shows the curves.\n")
    res = res.replace("(Figure \\ref{fig:spread}; the annotated version marks the no-graph slope as a reference line)",
                      "(Figure \\ref{fig:spread})")
    res = "# Results\n\n" + res
    res = res.replace("### Yield: top ideas per 100k tokens\n", "### Yield: top ideas per 100k tokens\n" + figure(
        "figures/8_top_ideas_vs_tokens.png", "fig:yield",
        "Top ideas (score $\\geq$ 4.0) found against tokens spent, per arm, with calls taken in replicate order. "
        "Each arm accumulates top ideas at a near-constant rate, so its slope is its yield (top ideas per 100k "
        "tokens): the steeper the line, the more efficient the arm. The need slice at medium effort climbs "
        "fastest; the full-graph arms are the flattest at every effort.") + figure(
        "figures/8c_yield_spread_annotated.png", "fig:spread",
        "How certain the yields are: for each arm, a box plot of 2,000 bootstrap slopes (calls resampled within "
        "market need; box = middle 50\\%, whiskers = 95\\% interval). The dashed line marks the control, no "
        "knowledge graph in the prompt (C, high effort). Arms whose boxes lie to the left of the line find top "
        "ideas less efficiently than giving the model no graph at all; this includes every full-graph arm, the "
        "random slice, and the need slice at high and extra-high effort (high only marginally). Only the need "
        "slice at low and medium effort lies to the right, more efficient than no graph."), 1)
    res = res.replace("## Cost and validity\n", "## Cost and validity\n" + figure(
        "figures/1_tokens_per_call.png", "fig:tokens",
        "Mean tokens per call by representation and effort, split into input (the prompt, most of it the graph "
        "file) and output (thinking and answer). The full graph pays for its context on every call; thinking "
        "effort drives the output for every representation.") + figure(
        "figures/5_context_ladder.png", "fig:ladder",
        "The context ladder at high effort: no graph (C), random slice (R), need slice (B) and full graph (A), "
        "in order of input size, against mean idea score, with the head-to-head set win rates between rungs."), 1)
    res = res.replace("### Top-idea rate (score ≥ 4.0)\n", "### Top-idea rate (score ≥ 4.0)\n" + figure(
        "figures/6_top_idea_rate.png", "fig:toprate",
        "Share of each arm's ideas that are top ideas (score $\\geq$ 4.0, the top 12\\% of all ideas), averaged "
        "over market needs, with 95\\% intervals from resampling calls within market need. This is quality "
        "only; cost per call is not taken into account here."), 1)
    res = res.replace("### Chance of at least one top idea for a given budget (secondary)\n",
                      "### Chance of at least one top idea for a given budget (secondary)\n" + figure(
        "figures/7_chance_vs_budget.png", "fig:budget",
        "Chance of at least one top idea for a given token budget, per arm, from whole calls and a Jeffreys "
        "estimate of each market need's success rate. Every curve rises towards 1 as the budget grows, so this "
        "view compresses differences at large budgets; yield (Figure \\ref{fig:yield}) is the main measure."), 1)
    res = res.replace("## Mean idea quality (individual scoring)\n", "## Mean idea quality (individual scoring)\n" + figure(
        "figures/4_cost_vs_quality.png", "fig:costquality",
        "Tokens per call against mean idea score for the full-graph (A) and need-slice (B) arms at each effort. "
        "Moving right costs tokens; moving up raises the average idea, not necessarily the number of top ideas."), 1)
    res = res.replace("## Pairwise set judging: full graph vs need slice (equal effort)\n",
                      "## Pairwise set judging: full graph vs need slice (equal effort)\n" + figure(
        "figures/2_win_rates.png", "fig:winrates",
        "Every pairwise set comparison: the first arm's win rate with a 95\\% Wilson interval (each pair judged "
        "in both presentation orders, ties excluded). Values above 50\\% favour the first arm.") + figure(
        "figures/3_score_diff_A_minus_B.png", "fig:scorediff",
        "Full graph minus need slice (A $-$ B) on each set-judging criterion, by effort. The full graph's "
        "advantage is mainly specificity."), 1)
    res = res.replace("### Yield per market need\n", "### Yield per market need\n" + figure(
        "figures/9_slice_size_effect.png", "fig:slicesize",
        "Per market need: the need slice's yield divided by the full graph's, against the number of nodes in "
        "the slice (log scale; needs with zero yield omitted)."), 1)
    res = res.replace("**One yield per persona**", figure(
        "figures/11_persona_effect.png", "fig:persona",
        "Persona follow-up: yield per persona over all of its calls (need slice and no graph, medium and high "
        "effort). Box = middle 50\\% of 2,000 bootstrap yields, whiskers = 95\\% CI, dot = observed.",
        "0.7\\textwidth") + "\n**One yield per persona**", 1)

    concl = read("conclusion_future_work.md")
    concl = concl.replace("# Conclusion and future work", "# Discussion and conclusion", 1)
    concl = concl.replace("## Conclusion\n", "## Conclusions\n", 1)

    appA = read("appendix_innovation_matrix.md").replace("## Appendix A: The microwave innovation matrix",
                                                          "# The microwave innovation matrix", 1)
    appA = appA.replace("Figure A1 (`0_innovation_matrix.png`) shows the whole graph.",
                        "Figure \\ref{fig:im_full} shows the whole graph.")
    appA = appA.replace("# The microwave innovation matrix\n", "# The microwave innovation matrix\n" + figure(
        "figures/0_innovation_matrix.pdf", "fig:im_full", "The full microwave innovation matrix (condition A)."), 1)

    def prompts():
        out = {}
        for f in ("analyze.py", "top_ideas.py"):
            for n in ast.parse(read(f)).body:
                if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
                    k = n.targets[0].id
                    if k in ("JUDGE_SYSTEM", "JUDGE_USER", "PATENT_SYSTEM", "PATENT_USER"):
                        out[(f, k)] = ast.literal_eval(n.value).replace("{{", "{").replace("}}", "}")
        return out

    p = prompts()

    def block(t):
        return "```\n" + t.strip() + "\n```\n"

    appB = ("# Generation prompt\n\nThe template used for every call (`template_prompt.txt`). Placeholders in "
            "braces are filled per call; `{persona}` is \"You are an innovation engineer.\" in the main study.\n\n"
            + block(read("template_prompt.txt")))
    appC = ("# Pairwise judge prompt\n\nSystem prompt:\n\n" + block(p[("analyze.py", "JUDGE_SYSTEM")])
            + "\nUser prompt:\n\n" + block(p[("analyze.py", "JUDGE_USER")]))
    appD = ("# Individual scoring prompts\n\nQuality (all ideas). System prompt:\n\n"
            + block(p[("top_ideas.py", "JUDGE_SYSTEM")]) + "\nUser prompt:\n\n" + block(p[("top_ideas.py", "JUDGE_USER")])
            + "\nPatentability (persona follow-up only), a separate call. System prompt:\n\n"
            + block(p[("top_ideas.py", "PATENT_SYSTEM")]) + "\nUser prompt:\n\n" + block(p[("top_ideas.py", "PATENT_USER")]))
    appE = files.replace("## Files", "# Data and code", 1)
    appE = chart_refs(appE)

    related = "```{=latex}\n" + read("related_work.tex") + "\n```\n"

    body = "\n\n".join([intro, related, methods, res, concl])
    appendix = "\n\n".join([appA, appB, appC, appD, appE])
    paper = body + "\n\n```{=latex}\n\\appendix\n```\n\n" + appendix
    (HERE / "paper.md").write_text(paper, encoding="utf-8")
    (HERE / "authors_notes.md").write_text("# Notes for the authors (not part of the paper)\n\n" + "\n".join(NOTES),
                                           encoding="utf-8")
    for name, text in (("body", body), ("appendix", appendix)):
        (HERE / f"_{name}.md").write_text(size_tables(market_need(re.sub(r"(?<=[ (])~(?=\d)", "∼", text))), encoding="utf-8")
        subprocess.run(["pandoc", f"_{name}.md", "-f", "markdown+tex_math_dollars", "-t", "latex", "--natbib",
                        "--wrap=preserve", "-o", f"{name}.tex"], cwd=HERE, check=True)
        (HERE / f"_{name}.md").unlink()
    write_unicode(paper + "∼")
    print("-> paper.md, body.tex, appendix.tex, unicode_chars.tex, authors_notes.md")


# non-ASCII characters in the text and how pdflatex should print them
UNICODE = {
    "≥": r"\ensuremath{\geq}", "≤": r"\ensuremath{\leq}", "÷": r"\ensuremath{\div}", "·": r"\ensuremath{\cdot}",
    "×": r"\ensuremath{\times}", "≈": r"\ensuremath{\approx}", "→": r"\ensuremath{\rightarrow}",
    "←": r"\ensuremath{\leftarrow}", "µ": r"\ensuremath{\mu}", "λ": r"\ensuremath{\lambda}", "−": r"\ensuremath{-}",
    "±": r"\ensuremath{\pm}", "∼": r"\ensuremath{\sim}", "─": "-", "…": r"\ldots{}",
    " ": r"\,", " ": r"\,", " ": "~", "²": r"\textsuperscript{2}", "³": r"\textsuperscript{3}",
    "Δ": r"\ensuremath{\Delta}", "α": r"\ensuremath{\alpha}", "β": r"\ensuremath{\beta}", "ρ": r"\ensuremath{\rho}",
    "≠": r"\ensuremath{\neq}", "∈": r"\ensuremath{\in}", "½": r"\ensuremath{\tfrac{1}{2}}",
}
KNOWN = set("–—‘’“”éèáàíóúñüöäçÉøØåÅšŠčČžŽłŁ°")


def write_unicode(text):
    lines, unknown = [], []
    for ch in sorted(set(text)):
        if ord(ch) < 128 or ch in KNOWN:
            continue
        if ch in UNICODE:
            lines.append("\\newunicodechar{" + ch + "}{" + UNICODE[ch] + "}")
        else:
            unknown.append(ch)
    (HERE / "unicode_chars.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if unknown:
        print("characters without a mapping (add them to UNICODE):", " ".join(f"{c} U+{ord(c):04X}" for c in unknown))


if __name__ == "__main__":
    build()
