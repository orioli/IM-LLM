"""common.py: shared paths and helpers for the M6_50ideas study.

Loading run logs, exploding calls into ideas, rendering ideas blind (no node ids, no condition),
reading the codebook, and calling Claude the same way as the main study's scripts.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent            # this study's folder, wherever scripts are run from
ROOT = HERE.parent                                 # the main study (read only)
RUNS = HERE / "runs" / "m6_50ideas.jsonl"          # this study: 50 ideas per call
REF_LOGS = [ROOT / "runs" / "rq1_full.jsonl"]      # the main study: 5 ideas per call (the reference)
N_IDEAS = 50
PERSONA = "engineer50"                              # the main study's engineer sentence, verbatim (personas_50ideas.yaml);
                                                    # the name only keeps run ids apart from the main study's
RESULTS = HERE / "results"
CODEBOOK_DIR = HERE / "codebook"
CODEBOOK = CODEBOOK_DIR / "codebook.yaml"
MOVES = RESULTS / "moves.jsonl"
PROMPTS = HERE / "prompts"
GRAPH = ROOT / "microwave_base_graph.yaml"

NEED = "M6"
CONDITIONS = ["A", "B", "R", "C"]
COND_NAME = {"A": "A · full graph", "B": "B · need slice", "R": "R · random slice", "C": "C · no graph"}
CATEGORIES = ["technology", "interaction", "behaviour", "ecosystem"]
PRIOR_ART = ["unchecked", "commercial", "patented", "published", "not_found"]
MOVE_FIELDS = ["id", "label", "replaces", "by", "definition", "category", "worked_example_echo",
               "source", "prior_art", "prior_art_ref", "examples"]
NODE_ID = re.compile(r"\(?\b[ACDFMPTX]\d{1,2}\b\)?")   # graph ids could hint at the condition (as human_check.py)
CODER_MODEL = "claude-sonnet-5-5"                        # the main study's judge model


# ── Run logs ────────────────────────────────────────────────────────
def load_calls(paths) -> dict[str, dict]:
    """run_id -> successful call; later lines (and later files) win, as in ../analyze.py."""
    calls = {}
    for p in ([paths] if isinstance(paths, (str, Path)) else paths):
        p = Path(p)
        if not p.exists():
            sys.exit(f"{p} not found")
        with p.open(encoding="utf-8") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("ok"):
                    calls[r["run_id"]] = r
    return calls


def tokens(call: dict) -> int:
    return (call.get("input_tokens") or 0) + (call.get("output_tokens") or 0)


def idea_records(calls: dict, need: str | None = NEED) -> list[dict]:
    """One record per idea: idea_id is '<run_id>#<k>' (as ../top_ideas.py), k = position in the call's list."""
    out = []
    for run_id, c in calls.items():
        if need and c.get("target_need") != need:
            continue
        for k, idea in enumerate(c.get("ideas") or [], 1):
            if not isinstance(idea, dict):
                continue
            out.append({"idea_id": f"{run_id}#{k}", "run_id": run_id, "k": k,
                        "condition": c.get("condition"), "effort": c.get("effort"),
                        "title": clean(idea.get("title", "")), "elements": elements(idea),
                        "rationale": clean(idea.get("rationale", ""))})
    return out


# ── Blind rendering ─────────────────────────────────────────────────
def clean(text) -> str:
    text = NODE_ID.sub("", str(text or ""))
    text = re.sub(r"\s+([,.;:)])", r"\1", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def elements(idea: dict) -> str:
    return "; ".join(f"{clean(n.get('label', ''))} ({clean(n.get('detail', ''))})"
                     for n in (idea.get("new_nodes") or []) if isinstance(n, dict))


def render_ideas(items: list[dict], key: str | None = None) -> str:
    """Numbered (or keyed) ideas: title, new elements, rationale. Nothing about who made them."""
    out = []
    for n, it in enumerate(items, 1):
        head = it[key] if key else str(n)
        out.append(f"{head}. {it['title'] or '(untitled)'}\n   New elements: {it['elements'] or '-'}\n"
                   f"   Why: {it['rationale'] or '-'}")
    return "\n".join(out)


# ── Codebook ────────────────────────────────────────────────────────
def load_codebook(path: Path = CODEBOOK, require_final: bool = True) -> dict:
    if not path.exists():
        sys.exit(f"{path} not found. Build it first (README, step 'codebook').")
    text = path.read_text(encoding="utf-8")
    cb = yaml.safe_load(text) or {}
    if require_final and cb.get("status") != "final":
        sys.exit(f"{path}: status is {cb.get('status')!r}; set 'status: final' once the codebook is edited.")
    moves = cb.get("moves") or []
    problems, seen = [], set()
    for m in moves:
        mid = m.get("id")
        if not mid or mid in seen or mid == "NEW":
            problems.append(f"bad or duplicate id: {mid!r}")
        seen.add(mid)
        if m.get("category") not in CATEGORIES:
            problems.append(f"{mid}: category must be one of {CATEGORIES}, got {m.get('category')!r}")
        if m.get("prior_art", "unchecked") not in PRIOR_ART:
            problems.append(f"{mid}: prior_art must be one of {PRIOR_ART}, got {m.get('prior_art')!r}")
        if not str(m.get("definition") or "").strip():
            problems.append(f"{mid}: definition is empty")
    if problems:
        sys.exit(f"{path}:\n  " + "\n  ".join(problems))
    cb["by_id"] = {m["id"]: m for m in moves}
    cb["sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    cb.setdefault("version", 1)
    return cb


def render_codebook(cb: dict) -> str:
    return "\n".join(f"{m['id']} · {m['label']}: replaces {m.get('replaces') or '-'} by {m.get('by') or '-'}. "
                     f"{' '.join(str(m['definition']).split())}" for m in cb["moves"])


def latest_codes(path: Path = MOVES) -> dict[str, dict]:
    """idea_id -> latest successful code (recoding appends; the last line wins)."""
    codes = {}
    if path.exists():
        for line in path.open(encoding="utf-8"):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("ok"):
                codes[r["idea_id"]] = r
    return codes


# ── Prompts and API ─────────────────────────────────────────────────
def load_prompt(name: str) -> tuple[str, str]:
    text = (PROMPTS / name).read_text(encoding="utf-8")
    m = re.search(r"=== SYSTEM ===\s*\n(.*?)\n=== USER ===\s*\n(.*)", text, re.S)
    if not m:
        sys.exit(f"{name}: expected '=== SYSTEM ===' and '=== USER ===' sections")
    return m.group(1).strip(), m.group(2).strip()


def fill(template: str, values: dict) -> str:
    """Plain replace, not str.format: the JSON examples in the prompts contain braces."""
    for k, v in values.items():
        template = template.replace("{" + k + "}", str(v))
    return template


def need_label(need: str = NEED) -> str:
    g = yaml.safe_load(GRAPH.read_text(encoding="utf-8"))
    return next(n["label"] for n in g["nodes"] if n["id"] == need)


def parse_json(text: str):
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    m = re.search(r"\{.*\}", cleaned, re.S)
    try:
        return json.loads(m.group() if m else cleaned)
    except (json.JSONDecodeError, AttributeError):
        return None


_client = None


def call_claude(system: str, user: str, model: str, effort: str, max_tokens: int) -> tuple[str, dict]:
    """Streaming call with effort sent explicitly, as in the main study. Returns (text, usage)."""
    global _client
    if _client is None:
        import anthropic                                   # only needed for real calls
        _client = anthropic.Anthropic(max_retries=5)
    t0 = time.perf_counter()
    with _client.messages.stream(model=model, max_tokens=max_tokens, system=system,
                                 messages=[{"role": "user", "content": user}],
                                 extra_body={"output_config": {"effort": effort}}) as s:
        resp = s.get_final_message()
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    return text, {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
                  "latency_s": round(time.perf_counter() - t0, 2), "stop_reason": resp.stop_reason}
