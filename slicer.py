#!/usr/bin/env python3
"""
slicer.py — build the graph-context files for the RQ1 experiment.

For every target market need M_k it writes:
  A_full.yaml            the whole graph G (one file, shared by all needs)
  B_<need>.yaml          vertical slice anchored on the need
  R_<need>_s<seed>.yaml  random slice, size- and layer-matched to B
  C_<need>.yaml          no-graph floor: schema + the target need only
plus slices/manifest.csv with sizes, token counts and a sha256 per file.

All files go through the same serializer (same fields, same ordering, same
meta block), so the only thing that differs between conditions is WHICH
nodes and edges are present. No file says which condition it belongs to;
that lives only in the manifest.

Usage
  python slicer.py microwave_base_graph.yaml                  # all needs, 1 random seed
  python slicer.py G.yaml --needs M1 M8 M17 --r-seeds 1 2 3   # chosen needs, 3 random slices each
  python slicer.py G.yaml --count-tokens                      # exact counts via Anthropic API
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

# ── Graph conventions ───────────────────────────────────────────────
TYPE_ORDER = ["Product", "Field", "Technology", "Component", "Function",
              "MarketNeed", "Actor", "Constraint"]
LAYER_ABBR = {"Field": "D", "Technology": "T", "Component": "C", "Function": "F",
              "MarketNeed": "M", "Actor": "A", "Constraint": "X", "Product": "P"}
CONSTRAINT_LINKS = {"causes", "contradicts", "partially_mitigates", "relevant_to"}
NODE_FIELDS = ["id", "type", "label", "detail"]   # proposed_by/status dropped: identical everywhere
META_KEYS = ["graph_id", "base_product", "layers", "cross_cutting", "edge_types"]


def _num(node_id: str) -> int:
    m = re.search(r"\d+", node_id)
    return int(m.group()) if m else 0


class Graph:
    def __init__(self, path: Path):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.meta = raw.get("meta", {})
        self.nodes = {n["id"]: n for n in raw["nodes"]}
        self.edges = raw["edges"]
        missing = {e[k] for e in self.edges for k in ("from", "to")} - self.nodes.keys()
        if missing:
            sys.exit(f"Edges reference unknown node ids: {sorted(missing)}")
        self.out = defaultdict(list)   # id -> [(to, type)]
        self.inc = defaultdict(list)   # id -> [(from, type)]
        for e in self.edges:
            self.out[e["from"]].append((e["to"], e["type"]))
            self.inc[e["to"]].append((e["from"], e["type"]))

    def ids_of(self, t: str) -> list[str]:
        return sorted((i for i, n in self.nodes.items() if n["type"] == t), key=_num)

    def type_of(self, i: str) -> str:
        return self.nodes[i]["type"]


# ── Condition B: vertical need slice ────────────────────────────────
def vertical_slice(g: Graph, need: str) -> set[str]:
    """Walk DOWN the matrix from one MarketNeed. Edges point up, so we follow them backwards."""
    if need not in g.nodes or g.type_of(need) != "MarketNeed":
        raise ValueError(f"{need} is not a MarketNeed in the graph")

    # 1–2 functions addressing the need, plus every function that enables them (recursively)
    funcs = {s for s, t in g.inc[need] if t == "addresses_need"}
    frontier = list(funcs)
    while frontier:
        f = frontier.pop()
        for s, t in g.inc[f]:
            if t == "enables_function" and s not in funcs:
                funcs.add(s)
                frontier.append(s)

    # 3 components performing those functions
    comps = {s for f in funcs for s, t in g.inc[f] if t == "performs_function"}
    # 4 technologies enabling the components or functions
    techs = {d for x in comps | funcs for d, t in g.out[x] if t == "enabled_by"}
    # 5 fields the technologies are rooted in
    fields = {d for x in techs for d, t in g.out[x] if t == "rooted_in"}

    core = {need} | funcs | comps | techs | fields

    # 6 context: constraints touching any core node (either direction), actors caring about the need
    constraints = set()
    for x in core:
        for o, t in g.out[x] + g.inc[x]:
            if t in CONSTRAINT_LINKS and g.type_of(o) == "Constraint":
                constraints.add(o)
    actors = {s for s, t in g.inc[need] if t == "relevant_to" and g.type_of(s) == "Actor"}

    products = set(g.ids_of("Product"))   # product anchor kept in every condition
    return core | constraints | actors | products


# ── Condition R: random slice matched to B ──────────────────────────
def random_slice(g: Graph, need: str, b_nodes: set[str], seed: int) -> set[str]:
    """Same node count per type as B; the target need and the product are always kept."""
    rng = random.Random(f"{need}-{seed}")       # deterministic, independent of call order
    fixed = {need} | set(g.ids_of("Product"))
    counts = Counter(g.type_of(i) for i in b_nodes - fixed)
    picked = set(fixed)
    for t, k in sorted(counts.items(), key=lambda kv: TYPE_ORDER.index(kv[0])):
        pool = [i for i in g.ids_of(t) if i not in fixed]
        picked |= set(rng.sample(pool, k))
    return picked


# ── Common serializer (identical for A, B, R, C) ────────────────────
class _FlowDict(dict):
    pass


class _Dumper(yaml.SafeDumper):
    pass


_Dumper.add_representer(
    _FlowDict, lambda d, v: d.represent_mapping("tag:yaml.org,2002:map", v.items(), flow_style=True))


def serialize(g: Graph, keep: set[str]) -> str:
    nodes = sorted(keep, key=lambda i: (TYPE_ORDER.index(g.type_of(i)), _num(i)))
    out_nodes = [{k: g.nodes[i][k] for k in NODE_FIELDS if g.nodes[i].get(k)} for i in nodes]
    out_edges = [_FlowDict([("from", e["from"]), ("to", e["to"]), ("type", e["type"])])
                 for e in g.edges if e["from"] in keep and e["to"] in keep]   # induced edges, original order
    doc = {"meta": {k: g.meta[k] for k in META_KEYS if k in g.meta},
           "nodes": out_nodes,
           "edges": out_edges}
    return yaml.dump(doc, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=10_000)


def n_edges(g: Graph, keep: set[str]) -> int:
    return sum(1 for e in g.edges if e["from"] in keep and e["to"] in keep)


# ── Token counting ──────────────────────────────────────────────────
def token_counter(exact: bool, model: str):
    if exact:
        try:
            import anthropic
            client = anthropic.Anthropic()        # reads ANTHROPIC_API_KEY
            def count(text: str) -> int:
                r = client.messages.count_tokens(
                    model=model, messages=[{"role": "user", "content": text}])
                return r.input_tokens
            return count, "api"
        except Exception as exc:                   # no key, no network, no package
            print(f"[warn] exact token count unavailable ({exc}); using estimate", file=sys.stderr)
    return (lambda text: round(len(text) / 3.5)), "estimate_chars/3.5"


# ── Main ────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("graph", type=Path)
    ap.add_argument("--needs", nargs="*", help="MarketNeed ids (default: all)")
    ap.add_argument("--r-seeds", nargs="*", type=int, default=[1], help="random-slice seeds per need")
    ap.add_argument("--out", type=Path, default=Path("slices"))
    ap.add_argument("--count-tokens", action="store_true", help="exact counts via Anthropic count_tokens")
    ap.add_argument("--model", default="claude-haiku-5-5", help="model for token counting")
    args = ap.parse_args()

    g = Graph(args.graph)
    needs = args.needs or g.ids_of("MarketNeed")
    args.out.mkdir(parents=True, exist_ok=True)
    count, method = token_counter(args.count_tokens, args.model)
    total_nodes = len(g.nodes)

    rows = []

    def emit(slice_id, condition, need, seed, keep, b_nodes=None):
        text = serialize(g, keep)
        path = args.out / f"{slice_id}.yaml"
        path.write_text(text, encoding="utf-8")
        types = Counter(g.type_of(i) for i in keep)
        rows.append({
            "slice_id": slice_id, "condition": condition, "target_need": need, "seed": seed,
            "file": path.as_posix(), "n_nodes": len(keep), "share_of_G": round(len(keep) / total_nodes, 3),
            "n_edges": n_edges(g, keep), "n_tokens": count(text), "token_method": method,
            **{f"n_{LAYER_ABBR[t]}": types.get(t, 0) for t in TYPE_ORDER},
            "overlap_with_B": len(keep & b_nodes) if b_nodes is not None else "",
            "node_ids": " ".join(sorted(keep, key=lambda i: (TYPE_ORDER.index(g.type_of(i)), _num(i)))),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        })

    emit("A_full", "A", "ALL", "", set(g.nodes))
    for need in needs:
        b = vertical_slice(g, need)
        emit(f"B_{need}", "B", need, "", b)
        for s in args.r_seeds:
            emit(f"R_{need}_s{s}", "R", need, s, random_slice(g, need, b, s), b_nodes=b)
        emit(f"C_{need}", "C", need, "", {need})

    manifest = args.out / "manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"{len(rows)} slice files + manifest written to {args.out}/ (tokens: {method})")
    print(f"{'slice_id':<14}{'nodes':>6}{'share':>7}{'edges':>7}{'tokens':>8}")
    for r in rows:
        print(f"{r['slice_id']:<14}{r['n_nodes']:>6}{r['share_of_G']:>7}{r['n_edges']:>7}{r['n_tokens']:>8}")


if __name__ == "__main__":
    main()
