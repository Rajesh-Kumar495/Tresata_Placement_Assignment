"""Step-5 runner: parse -> inventory (HC1 proposal) -> row-role labelling -> tie-out, on the real corpus.

    python -I -m ngr.pipeline [doc_id ...] [--mode record|replay|live]

Writes runs/<run_id>/<doc_id>/{inventory.json, hc1_proposal.json, reconciliations.json}
and runs/<run_id>/manifest.json (input hashes, model, every LLM call).
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone

from .config import PROJECT_ROOT
from .corpus import MANIFEST, load_document
from .inventory import Inventory, build_inventory, names_match
from .labels import load_labels
from .llm import LLMClient
from .reconcile import TableLabelling, candidate_tables, label_and_tie

RUNS = PROJECT_ROOT / "runs"


def run_doc(doc_id: str, llm: LLMClient, out_dir) -> dict:
    doc = load_document(doc_id)
    inv = build_inventory(doc, llm)
    tables = candidate_tables(doc, [m.name for m in inv.measures])
    with ThreadPoolExecutor(max_workers=4) as pool:
        labellings: list[TableLabelling] = list(pool.map(lambda t: label_and_tie(t, llm), tables))

    # Cross-check (deterministic): measures the labeller found reconciled in tables but the inventory missed.
    inv_names = [n for m in inv.measures for n in [m.name, *m.aliases]]
    recon_only = sorted({rc.measure.split(" [group")[0] for lab in labellings for rc in lab.reconciliations
                         if not any(names_match(rc.measure, n) for n in inv_names)})

    d = out_dir / doc_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "inventory.json").write_text(inv.model_dump_json(indent=1))
    hc1 = {
        "doc_id": doc_id,
        "doc_sha256": doc.sha256,
        "status": "PROPOSED - awaiting reviewer confirmation (HC1)",
        "measures": [{"name": m.name, "kind": m.kind, "per_share": m.per_share, "forward_looking": m.forward_looking,
                      "comparable_gaap": m.comparable_gaap, "evidence": [s.ref for s in m.mentions], "confirmed": None} for m in inv.measures],
        "review_also": {"unexplained_lexicon_candidates": inv.unexplained_candidates, "novel_measures_without_lexicon_support": inv.novel_measures,
                        "reconciled_in_tables_but_not_inventoried": recon_only, "dropped_for_failed_grounding": inv.dropped_measures},
    }
    (d / "hc1_proposal.json").write_text(json.dumps(hc1, indent=1))
    (d / "reconciliations.json").write_text(json.dumps([l.model_dump(mode="json") for l in labellings], indent=1))
    return {"doc_id": doc_id, "inventory": inv, "labellings": labellings, "recon_only": recon_only}


def inventory_recall(names: list[str], gold_measures) -> tuple[int, int, list[str]]:
    missed = [g.name for g in gold_measures if not any(names_match(g.name, n) for n in names)]
    return len(gold_measures) - len(missed), len(gold_measures), missed


def main(argv: list[str]) -> int:
    mode = "record"
    if "--mode" in argv:
        mode = argv[argv.index("--mode") + 1]
    labels = {l.doc_id: l for l in load_labels() if not l.synthetic}
    wanted = [a for a in argv[1:] if not a.startswith("--") and a not in ("record", "replay", "live")] or sorted(labels)
    llm = LLMClient(mode=mode)  # type: ignore[arg-type]
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = RUNS / run_id
    t0 = time.monotonic()
    results = [run_doc(d, llm, out_dir) for d in wanted]
    elapsed = time.monotonic() - t0

    corpus = json.loads(MANIFEST.read_text())
    manifest = {"run_id": run_id, "mode": mode, "model": llm.model, "elapsed_s": round(elapsed, 1),
                "inputs": {d: corpus.get(d, {}).get("sha256") for d in wanted}, "calls": [asdict(c) for c in llm.calls]}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=1))

    print(f"run {run_id}  model={llm.model}  mode={mode}  {elapsed:.0f}s  calls={len(llm.calls)} (cache hits {sum(c.cache_hit for c in llm.calls)})")
    for r in results:
        inv: Inventory = r["inventory"]
        gold = labels[r["doc_id"]].measures
        llm_names = [n for m in inv.measures for n in [m.name, *m.aliases]]
        got, tot, missed = inventory_recall(llm_names, gold)
        sgot, _, smissed = inventory_recall(llm_names + inv.unexplained_candidates + r["recon_only"], gold)
        gs = inv.grounding
        print(f"\n== {r['doc_id']}  inventory: {len(inv.measures)} measures | gold recall LLM-only {got}/{tot}, surfaced-to-HC1 {sgot}/{tot}"
              f" | grounding {gs.get('grounded', 0)}/{gs.get('quotes', 0)}{'  STATUS=' + inv.status if inv.status != 'ok' else ''}")
        if missed:
            print(f"   missed by LLM: {missed}" + (f"  (still missed after union: {smissed})" if smissed else "  (all surfaced via lexicon/table cross-check)"))
        if r["recon_only"]:
            print(f"   reconciled in tables but not inventoried: {r['recon_only'][:6]}")
        if inv.unexplained_candidates:
            print(f"   unexplained lexicon: {inv.unexplained_candidates[:8]}")
        if inv.dropped_measures:
            print(f"   dropped (ungrounded): {inv.dropped_measures}")
        for lab in r["labellings"]:
            if lab.status != "ok":
                print(f"   {lab.table_id}: {lab.status} {lab.error}")
                continue
            for rc in lab.reconciliations:
                to = rc.tieout
                v = to.verdict if to else "NO_TIEOUT"
                n = len(to.columns) if to else 0
                bad = [f"{'/'.join(c.header_path)[:40]}:{c.verdict}:{c.reason_code}" for c in (to.columns if to else []) if c.verdict != "PASS"]
                print(f"   {lab.table_id} {rc.orientation[:4]} start_is_gaap={rc.start_is_gaap!s:5} {v:13} x{n:<2} {rc.measure[:45]!r}"
                      + (f"  gate_errors={rc.gate_errors}" if rc.gate_errors else "") + (f"  issues={bad[:3]}" if bad else ""))
                for w in (to.provenance_warnings if to else [])[:2]:
                    print(f"      ! {w[:170]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
