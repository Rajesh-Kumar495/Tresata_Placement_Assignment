"""Meta-tests on the evaluation set itself: labels must be well-formed before they can score anything."""

import yaml

from ngr.config import PROJECT_ROOT
from ngr.labels import GoldLabel, load_labels, load_rule_ids, missing_anchors, validate_rule_refs

RULE_IDS = load_rule_ids()
LABELS = load_labels()


def test_corpus_meets_locked_minimums():
    tiers = [l.tier for l in LABELS]
    assert tiers.count("A") >= 4 and tiers.count("B") >= 2  # human-set minimums (2026-11-02)


def test_doc_ids_unique():
    ids = [l.doc_id for l in LABELS]
    assert len(ids) == len(set(ids))


def test_every_rule_reference_exists_in_rulepack():
    for label in LABELS:
        assert validate_rule_refs(label, RULE_IDS) == [], label.doc_id


def test_tier_b_pairs_resolve_to_tier_a():
    a_ids = {l.doc_id for l in LABELS if l.tier == "A"}
    for b in (l for l in LABELS if l.tier == "B"):
        assert b.paired_with in a_ids, b.doc_id


def test_every_tier_a_expected_finding_traces_to_an_sec_comment_or_note():
    for label in (l for l in LABELS if l.tier == "A"):
        for e in label.expected_findings:
            assert e.sec_comment or e.note, f"{label.doc_id}/{e.rule_id} has no provenance"


def test_mvp_rules_are_the_only_scored_rules():
    mvp = {r["id"] for r in yaml.safe_load((PROJECT_ROOT / "rules/rulepack.yaml").read_text(encoding="utf-8"))["rules"] if r["mvp"]}
    for label in LABELS:
        for e in label.expected_findings:
            assert e.rule_id in mvp, f"{label.doc_id}: {e.rule_id} is Ext; list it under sec_raised_ext"
        for x in label.sec_raised_ext:
            assert x not in mvp, f"{label.doc_id}: {x} is MVP; score it instead"


def test_synthetic_specs_reference_known_rules_and_base():
    spec = yaml.safe_load((PROJECT_ROOT / "eval/synthetic_cases.yaml").read_text(encoding="utf-8"))
    assert spec["base_doc"] in {l.doc_id for l in LABELS}
    for case in spec["mutations"] + spec["traps"]:
        for rid in case.get("expect", {}):
            assert rid in RULE_IDS, case["id"]
        nf = case.get("expect_no_flag", [])
        if nf != "all":
            assert set(nf) <= RULE_IDS, case["id"]
    core = [c for c in spec["mutations"] + spec["traps"] if c["core"]]
    assert len(core) >= 16


def test_anchor_validator_catches_missing_and_normalises_typography():
    label = GoldLabel.model_validate(
        {
            "doc_id": "X",
            "tier": "C",
            "synthetic": True,
            "source": {"company": "x", "cik": 1, "accession": "a", "filed": "2026-01-01", "exhibit_url": "u"},
            "label_source": "unit test",
            "expected_findings": [
                {"rule_id": "R-PROM-HEADLINE", "verdict": "FLAG", "evidence_contains": "Company's “record” EBITDA"},
                {"rule_id": "R-RECON-TIEOUT", "verdict": "FLAG", "evidence_contains": "not in document"},
            ],
        }
    )
    text = "The Company's  \"record\"\nEBITDA rose."
    assert missing_anchors(label, text) == ["not in document"]
