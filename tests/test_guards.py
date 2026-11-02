"""Guards added after the first run on real data (2026-11-02). Each one prevents a real observed failure."""

from helpers import parse_table, roles_by_label

from ngr.inventory import names_match
from ngr.reconcile import _ColAssign, split_column_groups
from ngr.tieout import tie_out


def test_no_adjustment_rows_cannot_pass_on_tolerance():
    # Lumen: GAAP EPS 0.50 -> non-GAAP EPS 0.51 with no adjustment rows passed on 1-cent tolerance
    _, t = parse_table([("Diluted EPS", ["0.50", "(3.08)"]), ("Diluted EPS excluding special items", ["0.51", "0.43"])])
    r = tie_out(t, roles_by_label(t, {"Diluted EPS": "gaap_start", "Diluted EPS excluding special items": "nongaap_result"}))
    assert [c.reason_code for c in r.columns] == ["no_adjustment_values", "no_adjustment_values"]
    assert r.verdict == "NEEDS_REVIEW"


def test_identity_with_no_adjustments_passes_only_if_exact():
    _, t = parse_table([("Net revenue", ["47,982"]), ("Adjusted net revenue", ["47,982"])])
    r = tie_out(t, roles_by_label(t, {"Net revenue": "gaap_start", "Adjusted net revenue": "nongaap_result"}))
    assert r.verdict == "PASS"


def test_percent_rows_are_not_summed():
    # Adient effective tax rate table: 30.8% + 45.0% != 34.1%, and must not be FLAGged
    _, t = parse_table([("As reported", ["30.8%"]), ("Adjustments", ["45.0%"]), ("As adjusted", ["34.1%"])])
    r = tie_out(t, roles_by_label(t, {"As reported": "gaap_start", "Adjustments": "adjustment", "As adjusted": "nongaap_result"}))
    assert r.verdict == "NOT_EVALUATED" and r.columns[0].reason_code == "ratio_not_additive"


def test_split_two_period_column_groups():
    cols = [_ColAssign(col_key=k, role=r) for k, r in [(7, "gaap_start"), (13, "adjustment"), (19, "nongaap_result"), (25, "gaap_start"), (31, "adjustment"), (37, "nongaap_result")]]
    groups = split_column_groups(cols)
    assert [[c.col_key for c in g] for g in groups] == [[7, 13, 19], [25, 31, 37]]


def test_eps_synonyms_match():
    assert names_match("Adjusted diluted EPS", "Adjusted diluted earnings per share")
    assert names_match("Non-GAAP diluted EPS", "Non-GAAP Diluted Earnings per Share")
    assert not names_match("Adjusted EBITDA", "Adjusted EPS")
