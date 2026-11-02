"""End-to-end review of one document: parse -> inventory -> row roles + tie-out -> rules -> judges."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from pydantic import BaseModel

from .docmodel import Document
from .findings import Finding
from .grounding import Grounder
from .inventory import GroundedMeasure, Inventory, build_inventory
from .judges import run_judges
from .llm import LLMClient
from .reconcile import TableLabelling, candidate_tables, label_and_tie
from .rules import run_rules


class Review(BaseModel):
    doc_id: str
    doc_sha256: str
    inventory: Inventory
    labellings: list[TableLabelling]
    findings: list[Finding]


def apply_hc1(inv: Inventory, doc: Document, confirmed: list[dict]) -> Inventory:
    """HC1 (ADR-006): the reviewer's confirmed measure list replaces the LLM proposal.

    `confirmed` items: {name, kind, per_share, forward_looking, comparable_gaap, confirmed: true|false}.
    Proposed measures keep their grounded mentions; measures the reviewer adds are located in the
    text by exact name where possible. Lexicon leftovers are considered reviewed.
    """
    g = Grounder(doc)
    by_name = {m.name.lower(): m for m in inv.measures}
    out = []
    for c in confirmed:
        if c.get("confirmed") is False:
            continue
        prev = by_name.get(c["name"].lower())
        span = g.ground(c["name"])
        out.append(GroundedMeasure(
            name=c["name"], aliases=prev.aliases if prev else [], kind=c.get("kind", "unknown"), per_share=bool(c.get("per_share")),
            forward_looking=bool(c.get("forward_looking")), comparable_gaap=c.get("comparable_gaap"), comparable_gaap_span=None,
            mentions=prev.mentions if prev else ([span] if span else []), rationale="confirmed at HC1",
            lexicon_support=prev.lexicon_support if prev else []))
    return inv.model_copy(update={"measures": out, "unexplained_candidates": [], "novel_measures": []})


def review(doc_id: str, doc: Document, llm: LLMClient,
           labelling_hook: Callable[[list[TableLabelling], Document], list[TableLabelling]] | None = None,
           hc1: list[dict] | None = None) -> Review:
    inv = build_inventory(doc, llm)
    if hc1 is not None:
        inv = apply_hc1(inv, doc, hc1)
    tables = candidate_tables(doc, [m.name for m in inv.measures])
    with ThreadPoolExecutor(max_workers=4) as pool:
        labellings = list(pool.map(lambda t: label_and_tie(t, llm), tables))
    if labelling_hook:  # used only by trap D13 to simulate a labeller error
        labellings = labelling_hook(labellings, doc)
    findings = run_rules(doc, inv, labellings) + run_judges(doc, inv, labellings, llm)
    if hc1 is not None:
        for f in findings:
            f.lineage.hc1_confirmed = True
    return Review(doc_id=doc_id, doc_sha256=doc.sha256, inventory=inv, labellings=labellings, findings=findings)
