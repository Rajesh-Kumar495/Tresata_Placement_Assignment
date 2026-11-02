"""Finding model + rule-pack access (architecture §4.9, ADR-017).

A Finding is the only thing a reviewer sees. It always carries: the rule and its
verbatim-backed citation, the category for this document type (never inferred by
the LLM), evidence spans grounded in the document, and lineage saying which
inputs were deterministic, LLM-derived, or human-confirmed.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

import yaml
from pydantic import BaseModel

from .config import PROJECT_ROOT

DOC_TYPE = "8-K_2.02_EX99"
Verdict = Literal["PASS", "FLAG", "NEEDS_REVIEW", "NOT_EVALUATED"]
SEVERITY = {"REQUIREMENT": "high", "STAFF_COMMENT_RISK": "medium"}


class Evidence(BaseModel):
    ref: str  # block id, table row id, or table id
    quote: str = ""
    char_start: int | None = None
    char_end: int | None = None


class Lineage(BaseModel):
    check_type: Literal["deterministic", "d_over_l", "llm_judge", "hybrid"]
    llm_inputs: list[str] = []  # which LLM-derived facts this finding relied on
    llm_call_ids: list[str] = []
    hc1_confirmed: bool = False
    provenance: list[str] = []  # e.g. INFERRED_SIGN / DIAGNOSIS warnings from tie-out


class Finding(BaseModel):
    rule_id: str
    verdict: Verdict
    category: str
    severity: str
    citation: list[str]
    excerpts: list[str]
    subject: str  # measure / table / block the finding is about
    message: str
    reason_code: str | None = None
    evidence: list[Evidence] = []
    lineage: Lineage
    confidence: str | None = None  # composed, e.g. "k=1 schema+grounded" or "agreement 2/3"


@lru_cache
def rulepack() -> dict[str, dict]:
    data = yaml.safe_load((PROJECT_ROOT / "rules" / "rulepack.yaml").read_text(encoding="utf-8"))
    return {r["id"]: r for r in data["rules"]}


def make(rule_id: str, verdict: Verdict, subject: str, message: str, *, evidence=None, reason_code=None,
         check_type=None, llm_inputs=None, provenance=None, call_ids=None, confidence=None) -> Finding:
    spec = rulepack()[rule_id]
    category = spec["category"][DOC_TYPE]
    ct = check_type or {"llm_presence": "llm_judge"}.get(spec["check"], spec["check"])
    if ct not in ("deterministic", "d_over_l", "llm_judge", "hybrid"):
        ct = "hybrid"
    return Finding(
        rule_id=rule_id,
        verdict=verdict,
        category=category,
        severity=SEVERITY[category],
        citation=list(spec["citation"]),
        excerpts=list(spec.get("excerpts", [])),
        subject=subject,
        message=message,
        reason_code=reason_code,
        evidence=evidence or [],
        lineage=Lineage(check_type=ct, llm_inputs=llm_inputs or [], provenance=provenance or [], llm_call_ids=call_ids or []),
        confidence=confidence,
    )
