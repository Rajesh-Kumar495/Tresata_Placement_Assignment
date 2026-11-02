"""Gold-label schema and validator (test_plan §5, ADR-013, ADR-020).

Labels are written by a human before pipeline code exists. They are held to the
same grounding standard as the model: every evidence anchor must occur verbatim
in the ingested document, or the label stays `provisional` and is not scored.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, model_validator

from .config import PROJECT_ROOT

GOLD_DIR = PROJECT_ROOT / "eval" / "gold"
RULEPACK = PROJECT_ROOT / "rules" / "rulepack.yaml"

Verdict = Literal["PASS", "FLAG", "NEEDS_REVIEW", "NOT_EVALUATED"]


class Source(BaseModel):
    company: str
    cik: int
    form: str = "8-K"
    accession: str
    filed: str
    exhibit_url: str
    sha256: str | None = None  # filled at ingest


class GoldMeasure(BaseModel):
    name: str
    kind: Literal["performance", "liquidity", "unknown"]
    per_share: bool = False
    comparable_gaap: str | None = None
    forward_looking: bool = False


class Expected(BaseModel):
    rule_id: str
    verdict: Verdict
    # other verdicts that also count as a correct detection (e.g. NEEDS_REVIEW for a judgment call)
    also_accept: list[Verdict] = []
    evidence_contains: str | None = None
    sec_comment: str | None = None
    note: str | None = None


class Negative(BaseModel):
    rule_id: str
    evidence_contains: str | None = None  # None = no FLAG anywhere for this rule
    note: str | None = None


class GoldLabel(BaseModel):
    doc_id: str
    tier: Literal["A", "B", "C", "D"]
    synthetic: bool
    source: Source
    label_source: str
    anchor_status: Literal["provisional", "validated"] = "provisional"
    paired_with: str | None = None
    measures: list[GoldMeasure] = []
    expected_findings: list[Expected] = []
    must_not_flag: list[Negative] = []
    sec_raised_ext: list[str] = []  # SEC-raised issues mapped to Ext rules: reported, not scored
    unscored_rules: dict[str, str] = {}  # rule_id -> why we can't know the truth
    notes: str | None = None

    @model_validator(mode="after")
    def _tier_rules(self) -> GoldLabel:
        if self.tier == "A" and not self.expected_findings:
            raise ValueError(f"{self.doc_id}: Tier A needs at least one SEC-derived expected finding")
        if self.tier == "B" and not self.paired_with:
            raise ValueError(f"{self.doc_id}: Tier B must name its Tier A pair")
        if self.tier in ("A", "B") and self.synthetic:
            raise ValueError(f"{self.doc_id}: Tier A/B are real documents")
        return self

    def anchors(self) -> list[str]:
        a = [e.evidence_contains for e in self.expected_findings if e.evidence_contains]
        return a + [n.evidence_contains for n in self.must_not_flag if n.evidence_contains]


def load_rule_ids(path: Path = RULEPACK) -> set[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {r["id"] for r in data["rules"]}


def load_labels(directory: Path = GOLD_DIR) -> list[GoldLabel]:
    return [GoldLabel.model_validate(yaml.safe_load(p.read_text(encoding="utf-8"))) for p in sorted(directory.glob("*.yaml"))]


def validate_rule_refs(label: GoldLabel, rule_ids: set[str]) -> list[str]:
    refs = [e.rule_id for e in label.expected_findings] + [n.rule_id for n in label.must_not_flag]
    refs += label.sec_raised_ext + list(label.unscored_rules)
    return sorted({r for r in refs if r not in rule_ids})


_QUOTES = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " "})


def normalize_for_anchor(text: str) -> str:
    """Same normalisation the grounding gate uses: whitespace + typographic quotes/dashes only."""
    return re.sub(r"\s+", " ", text.translate(_QUOTES)).strip()


def missing_anchors(label: GoldLabel, document_text: str) -> list[str]:
    hay = normalize_for_anchor(document_text)
    return [a for a in label.anchors() if normalize_for_anchor(a) not in hay]
