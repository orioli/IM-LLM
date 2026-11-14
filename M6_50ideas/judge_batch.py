#!/usr/bin/env python3
"""
judge_batch.py: the judge requests of score_ideas.py, sent through OpenRouter's Batch API (about half price).

  cd M6_50ideas
  GEN_MODEL=qwen python judge_batch.py submit     # one batch with every request not yet scored
  GEN_MODEL=qwen python judge_batch.py wait       # poll once a minute, write the scores when the batch is done
  GEN_MODEL=qwen python judge_batch.py status     # where each batch stands (no waiting)
  GEN_MODEL=qwen python score_ideas.py table      # as after `score_ideas.py score`

The requests are those of `score_ideas.py score`, built by the same functions: the same system and user
prompts, 5 consecutive ideas per request, claude-sonnet-5-5, effort medium. Two things differ. The output
cap: OpenRouter reserves the worst case of a batch (requests x max_tokens at the output price) against the
key's credit until the batch is done, so with the paper's cap of 16,000 one model's 430 requests would
reserve USD 34. The default here is 2,000: the judge's largest answer in the paper's 1,252 requests was
530 tokens (median 435), the model is not told the cap, and a request that does stop at the cap is logged
as failed, to be scored again with `JUDGE_API=openrouter python score_ideas.py score` (cap 16,000). And the
route: instead of one streamed call per request to the Anthropic API, all requests go in one
batch to OpenRouter (POST /api/v1/batches, endpoint /v1/messages), which runs them on Anthropic's own
batch API (provider pinned to Anthropic, no fallback). The scores are appended to the same
results[/<model>]/idea_scores.jsonl, in the same record format, with judge_api = "openrouter-batch".
Batches are logged in results[/<model>]/judge_batches.jsonl; `submit` skips requests that are scored or
in a batch still running, so every step can be run again. Needs OPENROUTER_API_KEY.

  --check             judge-route check: re-score calls that already have scores, into
                      results[/<model>]/judge_route_check/ (never touches idea_scores.jsonl); use with --run-ids
  --run-ids ID ...    only these calls
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

import score_ideas as si
from common import OPENROUTER_API, OPENROUTER_CLAUDE, RESULTS, RUNS, load_calls, openrouter_claude_body, parse_json

BATCHES_URL = OPENROUTER_API + "/v1/batches"
FINAL = {"completed", "failed", "expired", "cancelled"}


def headers() -> dict:
    key = os.environ.get("OPENROUTER_API_KEY") or sys.exit("OPENROUTER_API_KEY is not set")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.open(encoding="utf-8"):
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def append(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def done_keys(scores: Path) -> set:
    return {(r["run_id"], r["start"]) for r in read_jsonl(scores) if r.get("ok")}


def pending(batches: Path) -> dict[str, dict]:
    """batch id -> its 'submitted' record, for batches whose results have not been written yet."""
    out = {}
    for r in read_jsonl(batches):
        if r.get("event") == "submitted":
            out[r["batch_id"]] = r
        elif r.get("event") == "fetched":
            out.pop(r["batch_id"], None)
    return out


def cid(run_id: str, start: int) -> str:
    return f"{run_id}-s{start}"                       # letters, digits, _ and - only, as Anthropic's batch API requires


def cmd_submit(args) -> None:
    calls = load_calls(args.logs)
    if args.run_ids:
        missing = [r for r in args.run_ids if r not in calls]
        if missing:
            sys.exit(f"not in the run log: {missing}")
        calls = {r: calls[r] for r in args.run_ids}
    done = done_keys(args.scores)
    waiting = {c for b in pending(args.batches).values() for c in b["requests"]}
    todo = [c for c in si.chunks(calls) if (c["run_id"], c["start"]) not in done
            and cid(c["run_id"], c["start"]) not in waiting]
    print(f"{len(calls)} calls; {len(todo)} requests of up to {si.CHUNK} ideas to score with {args.model} (batch); "
          f"{len(waiting)} already in a running batch")
    if not todo:
        return
    if args.limit and len(todo) > args.limit:
        print(f"--limit: submitting the first {args.limit} now; run `submit` again for the other {len(todo) - args.limit}")
        todo = todo[:args.limit]
    extra = openrouter_claude_body(args.effort)
    provider = extra.pop("provider")                  # set once for the whole batch
    size = args.batch_size or len(todo)
    for k in range(0, len(todo), size):
        part = todo[k:k + size]
        # endpoint, model and provider must come before requests: OpenRouter reads the body as a stream
        payload = {"endpoint": "/v1/messages", "model": OPENROUTER_CLAUDE.get(args.model, args.model),
                   "provider": provider,
                   "requests": [{"custom_id": cid(c["run_id"], c["start"]),
                                 "body": {"max_tokens": args.max_tokens, "system": si.JUDGE_SYSTEM,
                                          "messages": [{"role": "user", "content": si.judge_prompt(c)}], **extra}}
                                for c in part]}
        resp = httpx.post(BATCHES_URL, headers=headers(), json=payload, timeout=300)
        if resp.status_code != 202:
            sys.exit(f"batch not accepted ({resp.status_code}): {resp.text[:600]}")
        b = resp.json()
        append(args.batches, {"event": "submitted", "batch_id": b["id"], "ts": now(), "judge_model": args.model,
                              "effort": args.effort, "max_tokens": args.max_tokens, "provider": b.get("provider"),
                              "requests": {cid(c["run_id"], c["start"]): [c["run_id"], c["start"], len(c["ideas"])]
                                           for c in part}})
        print(f"submitted {b['id']}: {len(part)} requests, provider {b.get('provider')}, status {b.get('status')}")


def get_batch(batch_id: str) -> dict | None:
    resp = httpx.get(f"{BATCHES_URL}/{batch_id}", headers=headers(), timeout=300)
    if resp.status_code == 429 or resp.status_code >= 500:
        return None                                   # try again at the next poll
    if resp.status_code != 200:
        sys.exit(f"batch {batch_id}: {resp.status_code} {resp.text[:400]}")
    return resp.json()


def write_results(sub: dict, batch: dict, args) -> tuple[int, int]:
    """Append one score record per request, in score_ideas.py's format. Returns (ok, failed)."""
    n_ok = n_fail = 0
    seen = set()
    for res in batch.get("results") or []:
        key = res.get("custom_id")
        if key not in sub["requests"]:
            continue
        seen.add(key)
        run_id, start, n = sub["requests"][key]
        rec = {"run_id": run_id, "start": start, "n": n, "judge_model": sub["judge_model"], "ts": now(),
               "judge_api": "openrouter-batch", "batch_id": batch["id"], "served_by": batch.get("provider")}
        try:
            if res.get("error"):
                raise RuntimeError(f"request error: {res['error']}")
            body = (res.get("response") or {}).get("body") or {}
            if body.get("type") != "message":
                raise RuntimeError(f"unexpected response: {json.dumps(body)[:300]}")
            text = "".join(b.get("text", "") for b in body.get("content") or [] if b.get("type") == "text")
            out = parse_json(text)
            ratings = out.get("ratings") if isinstance(out, dict) else None
            if not isinstance(ratings, list) or len(ratings) != n:
                raise ValueError(f"expected {n} ratings, got: {text[:200]}")
            usage = body.get("usage") or {}
            if body.get("stop_reason") == "max_tokens":
                raise RuntimeError(f"cut off at max_tokens={sub['max_tokens']}: score this request again without the cap")
            rec.update(ok=True, ratings=ratings, input_tokens=usage.get("input_tokens"),
                       output_tokens=usage.get("output_tokens"), stop_reason=body.get("stop_reason"),
                       judge_model_version=body.get("model"))
            n_ok += 1
        except Exception as exc:
            rec.update(ok=False, error=f"{type(exc).__name__}: {exc}")
            n_fail += 1
        append(args.scores, rec)
    for key in set(sub["requests"]) - seen:           # the provider returned nothing for this request
        run_id, start, n = sub["requests"][key]
        append(args.scores, {"run_id": run_id, "start": start, "n": n, "judge_model": sub["judge_model"], "ts": now(),
                             "judge_api": "openrouter-batch", "batch_id": batch["id"], "ok": False,
                             "error": f"no result in batch (status {batch.get('status')})"})
        n_fail += 1
    return n_ok, n_fail


def poll(args, verbose: bool = True) -> int:
    """Fetch every finished batch once. Returns the number still running."""
    running = 0
    for batch_id, sub in pending(args.batches).items():
        b = get_batch(batch_id)
        if b is None or b.get("status") not in FINAL or (b["status"] == "completed" and b.get("results") is None):
            running += 1
            if verbose and b is not None:
                print(f"{batch_id}: {b.get('status')} {b.get('request_counts')}")
            continue
        n_ok, n_fail = write_results(sub, b, args)
        append(args.batches, {"event": "fetched", "batch_id": batch_id, "ts": now(), "status": b["status"],
                              "usage": b.get("usage"), "ok": n_ok, "failed": n_fail,
                              "error": (b.get("error") or {}).get("message")})
        cost = (b.get("usage") or {}).get("cost")
        print(f"{batch_id}: {b['status']}, {n_ok} scored, {n_fail} failed"
              + (f", ${cost:.4f} billed" if cost is not None else "")
              + (f", error: {(b.get('error') or {}).get('message')}" if b.get("error") else ""))
    return running


def cmd_status(args) -> None:
    if not poll(args):
        print("no batch running" + ("" if args.scores.exists() else " (and no scores yet)"))


def cmd_wait(args) -> None:
    t0, k = time.time(), 0
    while True:
        running = poll(args, verbose=(k % 5 == 0))    # a status line every 5 minutes
        if not running:
            break
        if args.timeout_min and time.time() - t0 > 60 * args.timeout_min:
            sys.exit(f"{running} batch(es) still running after {args.timeout_min} min: run `wait` again later")
        time.sleep(60)
        k += 1
    left = [r for r in read_jsonl(args.scores) if not r.get("ok")]
    done = done_keys(args.scores)
    failed = {(r["run_id"], r["start"]) for r in left} - done
    print(f"all batches done: {len(done)} requests scored"
          + (f", {len(failed)} failed (run `submit` and `wait` again to retry them)" if failed else ""))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["submit", "wait", "status"])
    ap.add_argument("--logs", nargs="+", default=[RUNS])
    ap.add_argument("--run-ids", nargs="+", default=None)
    ap.add_argument("--check", action="store_true", help="judge-route check: write to results[/<model>]/judge_route_check/")
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--max-tokens", type=int, default=2000,
                    help="output cap per request (default 2000; the paper's sync calls used 16000, see above)")
    ap.add_argument("--batch-size", type=int, default=0, help="requests per batch (default: all in one)")
    ap.add_argument("--limit", type=int, default=0,
                    help="submit: at most this many requests now (OpenRouter reserves requests x max_tokens against "
                         "the key's credit until a batch is done)")
    ap.add_argument("--timeout-min", type=float, default=0, help="wait: give up after this many minutes (default: never)")
    args = ap.parse_args()
    out = RESULTS / "judge_route_check" if args.check else RESULTS
    args.scores, args.batches = out / "idea_scores.jsonl", out / "judge_batches.jsonl"
    if args.check and not args.run_ids and args.cmd == "submit":
        sys.exit("--check re-scores calls that are already scored: name them with --run-ids")
    {"submit": cmd_submit, "wait": cmd_wait, "status": cmd_status}[args.cmd](args)


if __name__ == "__main__":
    main()
