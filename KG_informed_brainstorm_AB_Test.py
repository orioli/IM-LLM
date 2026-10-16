#!/usr/bin/env python3
"""
KG_informed_brainstorm_AB_Test.py — run the RQ1 experiment.

For every (condition, target need, replicate) it fills template_prompt.txt
with the matching slice file from slices/manifest.csv, calls Claude Haiku,
and appends one JSON line per call to the log (prompt hash, slice hash,
token usage, latency, raw response, parsed ideas).

Conditions:  A = full graph   B = vertical need slice
             R = random size-matched slice   C = no graph (need only)

Typical use
  # 1. inspect the exact prompts, no API calls, no cost
  python KG_informed_brainstorm_AB_Test.py --dry-run

  # 2. pilot: 2 needs x 2 conditions x 3 replicates
  python KG_informed_brainstorm_AB_Test.py --needs M16 M8 --conditions A B --reps 3

  # 2b. effort sweep: same cells at three thinking-effort levels (36 calls)
  python KG_informed_brainstorm_AB_Test.py --needs M16 M8 --conditions A B --reps 3 --effort low medium high

  # 3. full run (defaults: 7 needs x 4 conditions x 10 reps = 280 calls)
  export ANTHROPIC_API_KEY=...
  python KG_informed_brainstorm_AB_Test.py

Re-running with the same --out resumes: calls already logged successfully are skipped.

Personas (--persona, default: engineer)
  The SYSTEM prompt starts with {persona}, filled from --personas-file (YAML: name -> system_intro).
  The built-in "engineer" is the main study's sentence, so its prompts and run ids are unchanged.
  Other personas get their name as a run-id prefix, e.g. lateral_B_M8_high_r01.
    python KG_informed_brainstorm_AB_Test.py --persona engineer lateral patent \
        --personas-file persona_as_factor/personas.yaml ...
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Target needs span small to large vertical slices. M2, M9, M10, M15 have no functions in G (degenerate slices).
DEFAULT_NEEDS = ["M16", "M14", "M6", "M8", "M11", "M7", "M1"]
DEFAULT_OPERATOR_NAME = "SUBSTITUTE"
DEFAULT_PERSONA = "engineer"
BUILTIN_PERSONAS = {"engineer": "You are an innovation engineer."}   # the main study's wording, verbatim
DEFAULT_OPERATOR_DEF = ("Identify components and the functions they perform, then replace them with "
                        "something cheaper or simpler that fulfils the same function equally well or better.")


# ── Inputs ──────────────────────────────────────────────────────────
def load_template(path: Path) -> tuple[str, str]:
    """Split template_prompt.txt into its SYSTEM and USER parts."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"=== SYSTEM ===\s*\n(.*?)\n=== USER ===\s*\n(.*)", text, re.S)
    if not m:
        sys.exit(f"{path}: expected '=== SYSTEM ===' and '=== USER ===' sections")
    return m.group(1).strip(), m.group(2).strip()


def fill(template: str, values: dict[str, str]) -> str:
    """Plain replace, not str.format: the JSON example in the template contains braces."""
    for k, v in values.items():
        template = template.replace("{" + k + "}", str(v))
    left = re.findall(r"\{(persona|product_name|target_need_id|target_need_label|operator_name|"
                      r"operator_definition|graph_yaml|n_ideas)\}", template)
    if left:
        sys.exit(f"Unfilled placeholders: {sorted(set(left))}")
    return template


def load_personas(path: Path | None) -> dict[str, str]:
    """name -> system_intro. The built-in engineer is always available; a file may add or override."""
    personas = dict(BUILTIN_PERSONAS)
    if path:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        personas.update({k: " ".join(str(v["system_intro"]).split()) for k, v in data.items()})
    return personas


def run_id_for(persona: str, cond: str, need: str, effort: str, rep: int) -> str:
    """The main study's ids for the engineer; other personas are prefixed with their name."""
    base = f"{cond}_{need}_{effort}_r{rep:02d}"
    return base if persona == DEFAULT_PERSONA else f"{persona}_{base}"


def slice_path(row: dict, manifest: Path) -> Path:
    """Manifest paths are relative to the project root (the manifest's parent's parent),
    so runs started from a sub-folder still find the slice files."""
    p = Path(row["file"])
    return p if p.exists() else manifest.parent.parent / row["file"]


def load_manifest(path: Path) -> dict[str, dict]:
    with path.open(encoding="utf-8") as fh:
        return {row["slice_id"]: row for row in csv.DictReader(fh)}


def need_labels(graph_path: Path) -> dict[str, str]:
    g = yaml.safe_load(graph_path.read_text(encoding="utf-8"))
    return {n["id"]: n["label"] for n in g["nodes"] if n["type"] == "MarketNeed"}


def slice_id_for(condition: str, need: str, r_seed: int) -> str:
    return {"A": "A_full", "B": f"B_{need}", "R": f"R_{need}_s{r_seed}", "C": f"C_{need}"}[condition]


# ── Output parsing (a failed parse is a result, not an error) ───────
def parse_ideas(text: str):
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", cleaned, re.S)          # tolerate stray prose around the JSON
        if not m:
            return None
        try:
            data = json.loads(m.group())
        except json.JSONDecodeError:
            return None
    ideas = data.get("ideas") if isinstance(data, dict) else None
    return ideas if isinstance(ideas, list) else None


# ── One API call ────────────────────────────────────────────────────
def call_model(client, job: dict, args) -> dict:
    """Returns the log record for one call. Network errors are retried by the SDK itself."""
    if args.cache:
        # cache the static prefix (everything up to and including the graph), not the output spec
        head, sep, tail = job["user"].partition("\nOUTPUT\n")
        content = [{"type": "text", "text": head, "cache_control": {"type": "ephemeral"}},
                   {"type": "text", "text": sep + tail}]
    else:
        content = job["user"]

    rec = {k: job[k] for k in ("run_id", "persona", "condition", "target_need", "effort", "rep", "slice_id",
                               "slice_sha256", "slice_n_nodes", "prompt_sha256")}
    rec.update(model=args.model, max_tokens=args.max_tokens,
               cache=args.cache, ts_start=datetime.now(timezone.utc).isoformat())
    # Claude 5.x models reject temperature/top_p/top_k, so none are sent: sampling uses the model's
    # defaults, which still vary between replicates. Effort is always sent explicitly (via extra_body,
    # so it works whatever SDK version is installed) and logged for analysis.
    extra = {"extra_body": {"output_config": {"effort": job["effort"]}}}
    t0 = time.perf_counter()
    try:
        # streaming: the SDK refuses non-streamed requests that may run >10 min (large max_tokens);
        # get_final_message() returns the same Message object as a normal call
        with client.messages.stream(
                model=args.model, max_tokens=args.max_tokens,
                system=job["system"], messages=[{"role": "user", "content": content}], **extra) as stream:
            resp = stream.get_final_message()
        # adaptive thinking may add thinking blocks; only the text blocks are the answer
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        u = resp.usage
        ideas = parse_ideas(text)
        rec.update(
            ok=True, latency_s=round(time.perf_counter() - t0, 3), stop_reason=resp.stop_reason,
            input_tokens=u.input_tokens, output_tokens=u.output_tokens,
            cache_read_tokens=getattr(u, "cache_read_input_tokens", 0) or 0,
            cache_write_tokens=getattr(u, "cache_creation_input_tokens", 0) or 0,
            parse_ok=ideas is not None, n_ideas=len(ideas) if ideas else 0,
            ideas=ideas, raw_text=text)
    except Exception as exc:                               # logged, not raised: the run continues
        rec.update(ok=False, latency_s=round(time.perf_counter() - t0, 3),
                   error=f"{type(exc).__name__}: {exc}")
    return rec


# ── Main ────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--graph", type=Path, default=Path("microwave_base_graph.yaml"))
    ap.add_argument("--manifest", type=Path, default=Path("slices/manifest.csv"))
    ap.add_argument("--template", type=Path, default=Path("template_prompt.txt"))
    ap.add_argument("--needs", nargs="+", default=DEFAULT_NEEDS)
    ap.add_argument("--conditions", nargs="+", default=["A", "B", "R", "C"], choices=["A", "B", "R", "C"])
    ap.add_argument("--reps", type=int, default=10)
    ap.add_argument("--r-seed", type=int, default=1, help="which random slice to use for condition R")
    ap.add_argument("--product-name", default="microwave")
    ap.add_argument("--operator-name", default=DEFAULT_OPERATOR_NAME)
    ap.add_argument("--operator-definition", default=DEFAULT_OPERATOR_DEF)
    ap.add_argument("--n-ideas", type=int, default=5)
    ap.add_argument("--persona", nargs="+", default=[DEFAULT_PERSONA],
                    help="one or more personas; each becomes its own set of calls (default: engineer)")
    ap.add_argument("--personas-file", type=Path, default=None,
                    help="YAML with persona descriptions (name -> system_intro)")
    ap.add_argument("--model", default="claude-haiku-5-5")
    ap.add_argument("--effort", nargs="+", choices=["low", "medium", "high", "xhigh", "max"],
                    default=["medium"],
                    help="one or more thinking-effort levels; each becomes its own set of calls "
                         "(default: medium, the Haiku 5.5 default)")
    ap.add_argument("--max-tokens", type=int, default=8000,
                    help="output budget; adaptive thinking counts against it, so keep headroom")
    ap.add_argument("--cache", action="store_true", help="prompt-cache the static prefix")
    ap.add_argument("--workers", type=int, default=4, help="parallel API calls")
    ap.add_argument("--order-seed", type=int, default=42, help="seed for randomizing call order")
    ap.add_argument("--out", type=Path, default=Path("runs/rq1_runs.jsonl"))
    ap.add_argument("--dry-run", action="store_true", help="write prompts to runs/dry_run/, no API calls")
    args = ap.parse_args()

    system_t, user_t = load_template(args.template)
    personas = load_personas(args.personas_file)
    unknown = [p for p in args.persona if p not in personas]
    if unknown:
        sys.exit(f"Unknown persona(s) {unknown}; known: {sorted(personas)} (pass --personas-file?)")
    manifest = load_manifest(args.manifest)
    labels = need_labels(args.graph)

    # ── build every job up front
    jobs = []
    for need in args.needs:
        if need not in labels:
            sys.exit(f"{need} is not a MarketNeed in {args.graph}")
        for cond in args.conditions:
            sid = slice_id_for(cond, need, args.r_seed)
            if sid not in manifest:
                sys.exit(f"{sid} missing from {args.manifest}; run slicer.py first")
            row = manifest[sid]
            graph_yaml = slice_path(row, args.manifest).read_text(encoding="utf-8")
            if hashlib.sha256(graph_yaml.encode("utf-8")).hexdigest() != row["sha256"]:
                sys.exit(f"{row['file']} changed since the manifest was written; re-run slicer.py")
            for persona in args.persona:
                values = {"persona": personas[persona], "product_name": args.product_name,
                          "target_need_id": need, "target_need_label": labels[need],
                          "operator_name": args.operator_name, "operator_definition": args.operator_definition,
                          "n_ideas": args.n_ideas, "graph_yaml": graph_yaml.rstrip()}
                system, user = fill(system_t, values), fill(user_t, values)
                prompt_sha = hashlib.sha256((system + "\n\n" + user).encode("utf-8")).hexdigest()
                for effort, rep in ((e, r) for e in args.effort for r in range(1, args.reps + 1)):
                    jobs.append({"run_id": run_id_for(persona, cond, need, effort, rep), "persona": persona,
                                 "effort": effort, "condition": cond, "target_need": need,
                                 "rep": rep, "slice_id": sid, "slice_sha256": row["sha256"],
                                 "slice_n_nodes": int(row["n_nodes"]), "prompt_sha256": prompt_sha,
                                 "system": system, "user": user})
    random.Random(args.order_seed).shuffle(jobs)          # spread conditions evenly over time

    # ── dry run: show exactly what would be sent
    if args.dry_run:
        out_dir = args.out.parent / "dry_run"
        out_dir.mkdir(parents=True, exist_ok=True)
        seen = set()
        for j in jobs:
            key = (j["persona"], j["condition"], j["target_need"])
            if key in seen:
                continue                                  # replicates and efforts share one prompt
            seen.add(key)
            prefix = "" if j["persona"] == DEFAULT_PERSONA else f"{j['persona']}_"
            (out_dir / f"{prefix}{j['condition']}_{j['target_need']}.txt").write_text(
                f"=== SYSTEM ===\n{j['system']}\n\n=== USER ===\n{j['user']}\n", encoding="utf-8")
        print(f"{len(jobs)} calls planned ({len(seen)} distinct prompts) -> prompts written to {out_dir}/")
        for cond in args.conditions:
            chars = [len(j["system"]) + len(j["user"]) for j in jobs if j["condition"] == cond]
            print(f"  {cond}: {len(chars)} calls, ~{round(sum(chars) / len(chars) / 3.5):,} input tokens per call (estimate)")
        if args.out.exists():                             # what a real run would still have to do
            done = {json.loads(l)["run_id"] for l in args.out.open(encoding="utf-8")
                    if l.strip() and json.loads(l).get("ok") and json.loads(l).get("model") == args.model}
            todo = [j for j in jobs if j["run_id"] not in done]
            print(f"  {args.out}: {len(jobs) - len(todo)} of these already logged, {len(todo)} would be run")
            for p in args.persona:
                print(f"    {p}: {sum(j['persona'] == p for j in todo)} to run")
        return

    # ── resume: skip calls already logged successfully
    args.out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if args.out.exists():
        with args.out.open(encoding="utf-8") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                    if r.get("ok") and r.get("model") == args.model:
                        done.add(r["run_id"])
                except json.JSONDecodeError:
                    pass
    todo = [j for j in jobs if j["run_id"] not in done]
    print(f"{len(jobs)} calls planned, {len(done)} already done, {len(todo)} to run -> {args.out}")
    if not todo:
        return

    import anthropic
    client = anthropic.Anthropic(max_retries=5)           # SDK retries 429/5xx with backoff

    lock, n_ok, n_fail = threading.Lock(), 0, 0
    with args.out.open("a", encoding="utf-8") as fh, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(call_model, client, j, args) for j in todo]
        for i, fut in enumerate(as_completed(futures), 1):
            rec = fut.result()
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
            n_ok += rec["ok"]
            n_fail += not rec["ok"]
            status = (f"in={rec['input_tokens']} out={rec['output_tokens']} ideas={rec['n_ideas']}"
                      if rec["ok"] else rec["error"][:80])
            print(f"[{i}/{len(todo)}] {rec['run_id']:<22} {status}")
    print(f"done: {n_ok} ok, {n_fail} failed (re-run the same command to retry failures)")


if __name__ == "__main__":
    main()
