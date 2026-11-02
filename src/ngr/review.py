"""End-to-end review of one document: parse -> inventory -> row roles + tie-out -> rules -> judges."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from pydantic import BaseModel

from .docmodel import Document
from .findings import Finding
from .inventory import Inventory, build_inventory
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


def review(doc_id: str, doc: Document, llm: LLMClient,
           labelling_hook: Callable[[list[TableLabelling], Document], list[TableLabelling]] | None = None) -> Review:
    inv = build_inventory(doc, llm)
    tables = candidate_tables(doc, [m.name for m in inv.measures])
    with ThreadPoolExecutor(max_workers=4) as pool:
        labellings = list(pool.map(lambda t: label_and_tie(t, llm), tables))
    if labelling_hook:  # used only by trap D13 to simulate a labeller error
        labellings = labelling_hook(labellings, doc)
    findings = run_rules(doc, inv, labellings) + run_judges(doc, inv, labellings, llm)
    return Review(doc_id=doc_id, doc_sha256=doc.sha256, inventory=inv, labellings=labellings, findings=findings)
