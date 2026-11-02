"""Tie-out on the REAL downloaded Tier A releases (parsed bytes, not transcriptions).

Row roles here are hand-assigned (gold), so these tests isolate parser + engine.
The LLM row labeller is evaluated separately against the same expectations.
Skipped if the corpus has not been downloaded (python -I -m ngr.corpus fetch).
"""

from decimal import Decimal

import pytest

from ngr.corpus import load_document, raw_path
from ngr.tieout import ColumnRole, RowRole, tie_out, tie_out_horizontal


def _doc(doc_id):
    if not raw_path(doc_id).exists():
        pytest.skip(f"{doc_id} not downloaded")
    return load_document(doc_id)


def _row(table, label_prefix, after=None):
    rows = [r for r in table.data_rows if r.label.startswith(label_prefix)]
    if after is not None:
        rows = [r for r in rows if r.index > after]
    assert rows, f"{table.id}: no row starting {label_prefix!r}"
    return rows[0]


def test_parser_repeated_header_block_is_header_not_data():
    t = _doc("A02-turtlebeach-2023-08-07").table("t05")
    six = next(r for r in t.rows if r.label == "Six Months Ended")
    assert six.is_header
    later = _row(t, "Operating income (loss)", after=six.index)
    assert later.cells[0].header_path[:2] == ["Six Months Ended", "June 30, 2023"]


def test_turtle_beach_table5_columnar_lines_tie():
    t = _doc("A02-turtlebeach-2023-08-07").table("t05")
    cols = [ColumnRole(col_key=3, role="gaap_start")] + [ColumnRole(col_key=k, role="adjustment") for k in (6, 9, 12, 15)] + [ColumnRole(col_key=18, role="nongaap_result")]
    lines = [_row(t, p).id for p in ("Net revenue", "Cost of revenue", "Gross Profit", "Operating expenses", "Operating income (loss)")]
    r = tie_out_horizontal(t, cols, lines)
    assert r.orientation == "horizontal" and r.verdict == "PASS"
    assert len(r.columns) == 5


def test_turtle_beach_adjusted_ebitda_step_needs_inferred_sign_and_says_so():
    t = _doc("A02-turtlebeach-2023-08-07").table("t05")
    op, other, last = _row(t, "Operating income (loss)"), _row(t, "Other non-operating expense"), _row(t, "Net loss")
    assert last.value_at(18).number.value == Decimal(-5595)
    roles = [RowRole(row_id=op.id, role="gaap_start"), RowRole(row_id=other.id, role="adjustment"), RowRole(row_id=last.id, role="nongaap_result")]
    # printed +198 added -> does not tie; Q11: diagnosed as possible unlabelled subtraction, never PASS
    r0 = tie_out(t, roles, columns=[18])
    assert r0.verdict == "NEEDS_REVIEW" and r0.columns[0].reason_code == "possible_unlabelled_subtraction"
    assert any("Discrepancy of 396 equals 2x row 'Other non-operating expense, net'" in w for w in r0.provenance_warnings)
    roles[1] = RowRole(row_id=other.id, role="adjustment", sign_hint="subtract")
    r = tie_out(t, roles, columns=[18])
    assert r.verdict == "PASS" and r.relies_on_inferred_sign
    assert any(w.startswith("INFERRED_SIGN") and "Other non-operating expense, net" in w for w in r.provenance_warnings)


def test_capri_schedule6_columnar_including_per_share():
    t = _doc("A03-capri-2024-11-07").table("t07")
    cols = [ColumnRole(col_key=7, role="gaap_start")] + [ColumnRole(col_key=k, role="adjustment") for k in (13, 19, 31, 37, 43)] + [ColumnRole(col_key=49, role="nongaap_result")]
    r = tie_out_horizontal(t, cols, [x.id for x in t.data_rows])
    assert r.verdict == "PASS", [(c.header_path, c.verdict) for c in r.columns]
    assert len(r.columns) == 7  # gross profit ... diluted EPS


def test_adient_gaap_adj_adjusted_columns_and_memo_build_up():
    t = _doc("A06-adient-2024-02-07").table("t07")
    lines = [x.id for x in t.data_rows if x.value_at(7) is not None]
    for start, adj, res in ((7, 13, 19), (25, 31, 37)):
        cols = [ColumnRole(col_key=start, role="gaap_start"), ColumnRole(col_key=adj, role="adjustment"), ColumnRole(col_key=res, role="nongaap_result")]
        r = tie_out_horizontal(t, cols, lines)
        assert r.verdict == "PASS", [(c.header_path, c.verdict, c.reason_code) for c in r.columns if c.verdict != "PASS"]
    # memo: Adjusted EBITDA built up from ADJUSTED EBIT (non-GAAP start: SEC comment 2)
    ebit, dep, eq, ebitda = (_row(t, p) for p in ("Earnings before interest", "Depreciation", "Equity based compensation", "Adjusted EBITDA"))
    roles = [RowRole(row_id=ebit.id, role="gaap_start"), RowRole(row_id=dep.id, role="adjustment"), RowRole(row_id=eq.id, role="adjustment"), RowRole(row_id=ebitda.id, role="nongaap_result")]
    assert tie_out(t, roles, columns=[19, 37]).verdict == "PASS"


def test_adient_less_label_printed_positive():
    t = _doc("A06-adient-2024-02-07").table("t09")
    a, less, res = _row(t, "Adjusted EBITDA"), _row(t, "Less: Adjusted Equity Income"), _row(t, "Adjusted EBITDA Excluding")
    roles = [RowRole(row_id=a.id, role="gaap_start"), RowRole(row_id=less.id, role="adjustment"), RowRole(row_id=res.id, role="nongaap_result")]
    r = tie_out(t, roles)
    assert r.verdict == "PASS" and not r.relies_on_inferred_sign


def test_citi_trends_adjusted_ebitda_both_periods():
    t = _doc("A04-cititrends-2025-06-03").table("t07")
    labels = [r.label for r in t.data_rows]
    roles = [RowRole(row_id=r.id, role="adjustment") for r in t.data_rows]
    roles[0] = RowRole(row_id=t.data_rows[0].id, role="gaap_start")
    roles[-1] = RowRole(row_id=t.data_rows[-1].id, role="nongaap_result")
    assert labels[0] == "Net income (loss)" and labels[-1] == "Adjusted EBITDA"
    r = tie_out(t, roles)
    assert r.verdict == "PASS" and len(r.columns) == 2
