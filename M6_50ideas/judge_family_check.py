#!/usr/bin/env python3
"""
judge_family_check.py: does the paper's Claude judge prefer ideas written by Claude models?

  cd M6_50ideas
  for m in haiku opus fable deepseek deepseekpro qwen; do
      GEN_MODEL=$m python second_judge.py score --judge deepseek/deepseek-v4.1-flash --host deepinfra/fp8 \
                                                --sample-per-arm 40
  done
  python judge_family_check.py          # no API calls -> results/judge_family_check.md, .csv

Design and decision rule: CHINESE_REPLICATION.md, Section 10 (written before the calls). A sample of the
ideas Sonnet already scored in the six 50-idea runs is scored again by DeepSeek V4.1 Flash with the paper's
judge prompt. Only ideas rated by both judges are used.

Primary. For each judge: the gap between the families, mean score of the three Claude runs minus mean score
of the three Chinese runs (runs weighted equally), in units of that judge's standard deviation over the
sampled ideas. Family preference index = Sonnet's gap minus the DeepSeek judge's gap.
Guard. The same gap inside one family (Opus and Fable against Haiku). The DeepSeek judge's gap divided by
Sonnet's gap is the share it keeps; a family preference needs it to keep more of the within-Claude gap than
of the between-family gap.
Intervals: 2,000 bootstrap resamples of judge requests within run, the same requests for both judges.
"""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE.parent))
from top_ideas import IDEA_CRITERIA  # noqa: E402

RUNS = [("haiku", "Haiku 5.5", "Claude"), ("opus", "Opus 5.5", "Claude"), ("fable", "Fable 5.1", "Claude"),
        ("deepseek", "DeepSeek V4.1 Flash", "Chinese"), ("deepseekpro", "DeepSeek V4 Pro", "Chinese"),
        ("qwen", "Qwen3.8 Flash", "Chinese")]
JUDGE = "deepseek/deepseek-v4.1-flash"
REPS, TOP = 2000, 4.0


def folder(key: str) -> Path:
    return HERE / "results" if key == "haiku" else HERE / "results" / key


def latest(path: Path) -> dict:
    out = {}
    if path.exists():
        for line in path.open(encoding="utf-8"):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("ok"):
                out[(r["run_id"], r["start"])] = r["ratings"]
    return out


def score(rating) -> float | None:
    if not isinstance(rating, dict):
        return None
    vals = [rating.get(c) for c in IDEA_CRITERIA if isinstance(rating.get(c), (int, float))]
    return sum(vals) / len(vals) if len(vals) == len(IDEA_CRITERIA) else None


def load() -> dict[str, list[list[tuple[float, float]]]]:
    """run key -> requests, each a list of (Sonnet score, DeepSeek score) for the ideas both judges rated."""
    data = {}
    for key, _, _ in RUNS:
        first = latest(folder(key) / "idea_scores.jsonl")
        second = latest(folder(key) / "second_judge" / JUDGE.replace("/", "_") / "idea_scores.jsonl")
        reqs = []
        for k, ratings in second.items():
            if k not in first:
                continue
            pairs = [(score(a), score(b)) for a, b in zip(first[k], ratings)]
            pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
            if pairs:
                reqs.append(pairs)
        data[key] = reqs
    return data


def stats(data: dict) -> dict:
    """Gaps in SD units for both judges, from one (possibly resampled) data set."""
    out = {}
    for j in (0, 1):
        allv = [p[j] for reqs in data.values() for r in reqs for p in r]
        m = sum(allv) / len(allv)
        sd = (sum((v - m) ** 2 for v in allv) / (len(allv) - 1)) ** 0.5
        mean = {k: sum(p[j] for r in reqs for p in r) / sum(len(r) for r in reqs) for k, reqs in data.items()}
        fam = lambda f: sum(mean[k] for k, _, g in RUNS if g == f) / 3
        out[j] = {"sd": sd, "mean": mean,
                  "between": (fam("Claude") - fam("Chinese")) / sd,
                  "within": ((mean["opus"] + mean["fable"]) / 2 - mean["haiku"]) / sd,
                  "own": ((mean["deepseek"] + mean["deepseekpro"]) / 2 - mean["qwen"]) / sd}
    return out


def ci(vals: list[float]) -> tuple[float, float]:
    v = sorted(vals)
    return v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]


def top_shares(data: dict) -> tuple[dict, dict, float]:
    """Share of top ideas per run: Sonnet at 4.0, the DeepSeek judge at the matched cut-off."""
    pairs = [p for reqs in data.values() for r in reqs for p in r]
    n_top = sum(a >= TOP for a, _ in pairs)
    cut = min(sorted({b for _, b in pairs}), key=lambda c: abs(sum(b >= c for _, b in pairs) - n_top))
    s1, s2 = {}, {}
    for k, reqs in data.items():
        flat = [p for r in reqs for p in r]
        s1[k] = sum(a >= TOP for a, _ in flat) / len(flat)
        s2[k] = sum(b >= cut for _, b in flat) / len(flat)
    return s1, s2, cut


def spearman(x: list[float], y: list[float]) -> float:
    rank = lambda v: [sorted(v).index(a) for a in v]
    rx, ry = rank(x), rank(y)
    n = len(x)
    return 1 - 6 * sum((a - b) ** 2 for a, b in zip(rx, ry)) / (n * (n * n - 1))


def main() -> None:
    data = load()
    missing = [k for k, reqs in data.items() if not reqs]
    if missing:
        sys.exit(f"no second-judge scores yet for: {missing}")
    point = stats(data)
    rng = random.Random("family-check")
    boot = [stats({k: [rng.choice(reqs) for _ in reqs] for k, reqs in data.items()}) for _ in range(REPS)]
    fpi = [b[0]["between"] - b[1]["between"] for b in boot]
    keep_w = [b[1]["within"] / b[0]["within"] for b in boot]
    keep_b = [b[1]["between"] / b[0]["between"] for b in boot]
    guard = [w - bb for w, bb in zip(keep_w, keep_b)]
    own = [b[1]["own"] - b[0]["own"] for b in boot]
    p_fpi = point[0]["between"] - point[1]["between"]
    p_kw, p_kb = point[1]["within"] / point[0]["within"], point[1]["between"] / point[0]["between"]
    s1, s2, cut = top_shares(data)
    fam_share = lambda s, f: sum(s[k] for k, _, g in RUNS if g == f) / 3
    names = {k: n for k, n, _ in RUNS}
    n_ideas = {k: sum(len(r) for r in reqs) for k, reqs in data.items()}

    lo, hi = ci(fpi)
    glo, ghi = ci(guard)
    verdict = ("Sonnet prefers Claude-written ideas" if lo > 0 and glo > 0 else
               "no evidence of a family preference" if lo <= 0 <= hi else
               f"ambiguous. The DeepSeek judge keeps {p_kw:.0%} of the gap inside Claude and {p_kb:.0%} of the gap "
               f"between the families, but the difference has an interval that includes 0, so a judge that "
               f"separates ideas less well in general can't be ruled out")

    L = ["# Does the judge prefer its own family?", "",
         f"Ideas from the six 50-idea runs, scored by Sonnet 5.5 (the paper's judge) and again by `{JUDGE}` with the "
         f"paper's judge prompt. Design and decision rule: `CHINESE_REPLICATION.md`, Section 10. {sum(n_ideas.values()):,} "
         f"ideas rated by both judges. Gaps are in standard deviations of each judge's scores (Sonnet "
         f"{point[0]['sd']:.2f}, DeepSeek {point[1]['sd']:.2f} points). Intervals: 95%, {REPS:,} bootstrap resamples of "
         "requests within run.", "",
         "| Run | Family | Ideas | Mean score, Sonnet | Mean score, DeepSeek | Top ideas, Sonnet (score ≥ 4.0) | "
         f"Top ideas, DeepSeek (score ≥ {cut:g}, same overall share) |", "| --- | --- | --- | --- | --- | --- | --- |"]
    rows = []
    for k, n, f in RUNS:
        L.append(f"| {n} | {f} | {n_ideas[k]} | {point[0]['mean'][k]:.2f} | {point[1]['mean'][k]:.2f} | "
                 f"{100 * s1[k]:.1f}% | {100 * s2[k]:.1f}% |")
        rows.append({"run": n, "family": f, "ideas": n_ideas[k], "mean_sonnet": round(point[0]["mean"][k], 4),
                     "mean_deepseek": round(point[1]["mean"][k], 4), "top_share_sonnet": round(s1[k], 4),
                     "top_share_deepseek_matched": round(s2[k], 4)})
    rho = spearman([point[0]["mean"][k] for k, _, _ in RUNS], [point[1]["mean"][k] for k, _, _ in RUNS])
    blo, bhi = ci([b[0]["between"] for b in boot])
    dlo, dhi = ci([b[1]["between"] for b in boot])
    wlo, whi = ci([b[0]["within"] for b in boot])
    vlo, vhi = ci([b[1]["within"] for b in boot])
    olo, ohi = ci(own)
    L += ["", "| Gap (standard deviations) | Sonnet | DeepSeek judge | Share the DeepSeek judge keeps |",
          "| --- | --- | --- | --- |",
          f"| Claude runs minus Chinese runs | {point[0]['between']:+.2f} [{blo:+.2f}, {bhi:+.2f}] | "
          f"{point[1]['between']:+.2f} [{dlo:+.2f}, {dhi:+.2f}] | {p_kb:.2f} |",
          f"| Opus and Fable minus Haiku (inside Claude) | {point[0]['within']:+.2f} [{wlo:+.2f}, {whi:+.2f}] | "
          f"{point[1]['within']:+.2f} [{vlo:+.2f}, {vhi:+.2f}] | {p_kw:.2f} |",
          f"| DeepSeek runs minus Qwen (inside Chinese) | {point[0]['own']:+.2f} | {point[1]['own']:+.2f} | |", "",
          f"- Family preference index (Sonnet's between-family gap minus the DeepSeek judge's): **{p_fpi:+.2f}** "
          f"[{lo:+.2f}, {hi:+.2f}].",
          f"- Guard (share kept of the within-Claude gap minus share kept of the between-family gap): {p_kw - p_kb:+.2f} "
          f"[{glo:+.2f}, {ghi:+.2f}].",
          f"- Does the DeepSeek judge favour DeepSeek-written ideas over Qwen's more than Sonnet does? Difference "
          f"{point[1]['own'] - point[0]['own']:+.2f} [{olo:+.2f}, {ohi:+.2f}].",
          f"- Claude-to-Chinese ratio of top-idea shares: {fam_share(s1, 'Claude') / fam_share(s1, 'Chinese'):.2f} under "
          f"Sonnet, {fam_share(s2, 'Claude') / fam_share(s2, 'Chinese'):.2f} under the DeepSeek judge.",
          f"- Ranking of the six runs by mean score, Spearman correlation between the judges: {rho:.2f}.", "",
          f"**Verdict (pre-registered rule): {verdict}.**"]
    out = HERE / "results" / "judge_family_check.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    with out.with_suffix(".csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("\n".join(L))
    print(f"-> {out.relative_to(HERE)}, {out.with_suffix('.csv').name}")


if __name__ == "__main__":
    main()
