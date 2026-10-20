#!/usr/bin/env python3
"""Build script for the IM-LLM paper.

Steps:
1. Ensure python virtual environment (.venv) is set up with requirements.txt.
2. (Optional) Run data analysis scripts to regenerate results/*.csv.
3. (Optional) Run chart generation scripts to regenerate figures.
4. Sync figures into paper/figures/.
5. Compile paper/main.tex with tectonic.
6. Verify output PDF integrity (page count, missing figure checks, unresolved references).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = ROOT / "paper"
VENV_DIR = ROOT / ".venv"
PYTHON_BIN = VENV_DIR / "bin" / "python"
TECTONIC_BIN = shutil.which("tectonic") or "/home/marc/.local/bin/tectonic"


def run_cmd(cmd: list[str] | str, cwd: Path = ROOT, shell: bool = False) -> None:
    print(f"==> Running: {cmd if isinstance(cmd, str) else ' '.join(cmd)} (cwd: {cwd})")
    res = subprocess.run(cmd, cwd=cwd, shell=shell, check=True)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {res.returncode}")


def setup_venv() -> None:
    if not PYTHON_BIN.exists():
        print("==> Setting up .venv...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        subprocess.run([str(VENV_DIR / "bin" / "pip"), "install", "-r", str(ROOT / "requirements.txt")], check=True)
    else:
        print("==> Python virtual environment found at .venv")


def generate_results(py_bin: Path) -> None:
    print("==> Regenerating analysis results...")
    run_cmd([str(py_bin), "analyze.py", "stats", "--logs", "runs/rq1_full.jsonl"])
    run_cmd([str(py_bin), "analyze.py", "summary", "--logs", "runs/rq1_full.jsonl"])
    run_cmd([str(py_bin), "top_ideas.py", "report", "--logs", "runs/rq1_full.jsonl"])


def generate_charts(py_bin: Path) -> None:
    print("==> Generating charts and figures...")
    run_cmd([str(py_bin), "figure_innovation_matrix.py"])
    run_cmd([str(py_bin), "charts.py"])
    run_cmd([str(py_bin), "tail_charts.py"])


def sync_figures() -> None:
    print("==> Syncing figures to paper/figures/...")
    target_dir = PAPER_DIR / "figures"
    target_dir.mkdir(parents=True, exist_ok=True)

    src_dirs = [ROOT / "results" / "charts"]
    copied = 0
    for sdir in src_dirs:
        if sdir.exists():
            for f in sdir.glob("*"):
                if f.is_file() and f.suffix in {".png", ".pdf", ".jpg", ".jpeg"}:
                    shutil.copy2(f, target_dir / f.name)
                    copied += 1
    print(f"==> Synced {copied} figures into {target_dir}")


def compile_latex(engine: str = "tectonic") -> Path:
    print(f"==> Compiling LaTeX with {engine}...")
    if engine == "tectonic":
        run_cmd([str(TECTONIC_BIN), "main.tex"], cwd=PAPER_DIR)
        out_pdf = PAPER_DIR / "main.pdf"
    elif engine == "pdflatex":
        run_cmd(["pdflatex", "-interaction=nonstopmode", "main.tex"], cwd=PAPER_DIR)
        run_cmd(["bibtex", "main"], cwd=PAPER_DIR)
        run_cmd(["pdflatex", "-interaction=nonstopmode", "main.tex"], cwd=PAPER_DIR)
        run_cmd(["pdflatex", "-interaction=nonstopmode", "main.tex"], cwd=PAPER_DIR)
        out_pdf = PAPER_DIR / "main.pdf"
    else:
        raise ValueError(f"Unsupported LaTeX engine: {engine}")

    if not out_pdf.exists():
        raise FileNotFoundError(f"Expected compiled PDF at {out_pdf}, but not found.")
    return out_pdf


def verify_pdf(pdf_path: Path) -> None:
    print(f"==> Verifying compiled PDF: {pdf_path}")
    if shutil.which("pdfinfo"):
        res = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True, check=True)
        for line in res.stdout.splitlines():
            if "Pages:" in line or "Page size:" in line or "File size:" in line:
                print(f"    {line}")

    if shutil.which("pdftotext"):
        res = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True, check=True)
        text = res.stdout
        if "missing:" in text:
            print("WARNING: 'missing:' placeholder found in compiled PDF text!")
        else:
            print("    ✓ No missing figure placeholders found.")

        if "??" in text:
            print("WARNING: Undefined citation/reference '??' found in compiled PDF text!")
        else:
            print("    ✓ No broken reference marks (??) found.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the IM-LLM paper PDF.")
    parser.add_argument("--skip-venv", action="store_true", help="Skip venv check/setup")
    parser.add_argument("--skip-stats", action="store_true", help="Skip recalculating results/*.csv")
    parser.add_argument("--skip-charts", action="store_true", help="Skip regenerating chart images")
    parser.add_argument("--engine", default="tectonic", choices=["tectonic", "pdflatex"], help="LaTeX compiler engine")
    parser.add_argument("--copy-to-tmp", action="store_true", help="Copy final PDF to tmp/paper_latex.pdf")
    args = parser.parse_args()

    if not args.skip_venv:
        setup_venv()

    py_bin = PYTHON_BIN if PYTHON_BIN.exists() else Path(sys.executable)

    if not args.skip_stats:
        generate_results(py_bin)

    if not args.skip_charts:
        generate_charts(py_bin)

    sync_figures()

    pdf_path = compile_latex(engine=args.engine)
    verify_pdf(pdf_path)

    if args.copy_to_tmp:
        tmp_target = ROOT / "tmp" / "paper_latex.pdf"
        tmp_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf_path, tmp_target)
        print(f"==> Copied {pdf_path} -> {tmp_target}")

    print("\n✓ Paper build complete!")


if __name__ == "__main__":
    main()
