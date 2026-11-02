"""Tie-out engine tests (test_plan §6.1/§6.2 tie-out cases + ADR-014).

Real-world fixtures reproduce reconciliations from locked Tier A releases.
Their numbers were transcribed during triage and are re-verified against the
downloaded bytes in step 4 (ADR-020).
"""

from decimal import Decimal

from helpers import parse_table, roles_by_label
from hypothesis import given, settings
from hypothesis import strategies as st

from ngr.tieout import tie_out

BASE = [
    ("Net income", ["10,100", "25,000"]),
    ("Interest expense", ["2,000", "6,000"]),
    ("Income tax expense", ["3,000", "7,000"]),
    ("Depreciation and amortization", ["4,000", "12,000"]),
    ("Restructuring", ["1,500", "—"]),
    ("Adjusted EBITDA", ["20,600", "50,000"]),
]
ROLES = {
    "Net income": "gaap_start",
    "Interest expense": "adjustment",
    "Income tax expense": "adjustment",
    "Depreciation and amortization": "adjustment",
    "Restructuring": "adjustment",
    "Adjusted EBITDA": "nongaap_result",
}


def run(rows, roles=ROLES, subtract=frozenset()):
    _, t = parse_table(rows)
    return tie_out(t, roles_by_label(t, roles, subtract))


def replace(rows, label, values):
    return [(l, values if l == label else v) for l, v in rows]


# ---- happy path and basic failures
def test_clean_reconciliation_passes_every_column():
    r = run(BASE)
    assert r.verdict == "PASS"
    assert [c.verdict for c in r.columns] == ["PASS", "PASS"]


def test_M02_deleted_adjustment_flags_with_diff():
    rows = [x for x in BASE if x[0] != "Interest expense"]
    roles = {k: v for k, v in ROLES.items() if k != "Interest expense"}
    r = run(rows, roles)
    assert r.verdict == "FLAG"
    seg = r.columns[0].segments[-1]
    assert seg.reason_code == "tieout_mismatch" and seg.diff == Decimal(2000)


def test_M03_perturbation_beyond_rounding_band_flags():
    r = run(replace(BASE, "Restructuring", ["1,520", "—"]))
    assert r.columns[0].verdict == "FLAG"
    assert r.columns[1].verdict == "PASS"


def test_D08_off_by_one_rounding_passes():
    r = run(replace(BASE, "Adjusted EBITDA", ["20,601", "50,000"]))
    assert r.verdict == "PASS"


def test_rounding_band_is_needs_review_not_flag_or_pass():
    # off by 3 units with 5 rounded terms in segment -> within worst-case band (0.5*1*7=3.5)
    r = run(replace(BASE, "Adjusted EBITDA", ["20,603", "50,000"]))
    assert r.columns[0].verdict == "NEEDS_REVIEW"
    assert r.columns[0].reason_code == "rounding_band"


def test_D04_error_only_in_one_period_column_names_header():
    r = run(replace(BASE, "Depreciation and amortization", ["4,000", "12,900"]))
    assert [c.verdict for c in r.columns] == ["PASS", "FLAG"]
    assert r.columns[1].header_path == ["P2"]


# ---- ADR-014: polarity
def test_M13_less_label_positive_print_is_subtracted_by_lexicon():
    rows = BASE[:5] + [("Less: gain on sale of assets", ["600", "—"]), ("Adjusted EBITDA", ["20,000", "50,000"])]
    roles = dict(ROLES, **{"Less: gain on sale of assets": "adjustment"})
    r = run(rows, roles)
    assert r.verdict == "PASS"
    term = next(t for t in r.columns[0].segments[0].terms if t.label.startswith("Less"))
    assert term.effective == Decimal(-600) and term.sign_source == "lexicon"
    assert term.sign_source_conflict  # LLM said as_printed, lexicon said subtract -> surfaced


def test_llm_sign_hint_without_lexicon_cue_is_applied_and_recorded():
    rows = BASE[:5] + [("Gain on sale of assets", ["600", "—"]), ("Adjusted EBITDA", ["20,000", "50,000"])]
    roles = dict(ROLES, **{"Gain on sale of assets": "adjustment"})
    r = run(rows, roles, subtract={"Gain on sale of assets"})
    assert r.verdict == "PASS"
    term = next(t for t in r.columns[0].segments[0].terms if t.label.startswith("Gain"))
    assert term.sign_source == "llm"


def test_sign_ambiguous_is_needs_review_naming_the_row():
    # "Less: X (600)" printed negative: as-printed adds -600, but intent was +600
    rows = BASE[:5] + [("Less: tax benefit", ["(600)", "—"]), ("Adjusted EBITDA", ["21,200", "50,000"])]
    roles = dict(ROLES, **{"Less: tax benefit": "adjustment"})
    _, t = parse_table(rows)
    r = tie_out(t, roles_by_label(t, roles))
    col = r.columns[0]
    assert col.verdict == "NEEDS_REVIEW" and col.reason_code == "sign_ambiguous"
    assert col.segments[0].diagnosis_row == next(x.id for x in t.data_rows if x.label == "Less: tax benefit")


def test_D14_flip_diagnosis_cannot_mask_a_real_error():
    rows = BASE[:5] + [("Less: gain on sale of assets", ["600", "—"]), ("Adjusted EBITDA", ["20,010", "50,000"])]
    roles = dict(ROLES, **{"Less: gain on sale of assets": "adjustment"})
    r = run(rows, roles)
    assert r.columns[0].verdict == "FLAG"


# ---- ADR-014: subtotals
def test_M14_intermediate_subtotal_is_a_checkpoint_not_an_addend():
    rows = [
        ("Net income", ["10,100", "25,000"]),
        ("Income tax expense", ["3,000", "7,000"]),
        ("Interest expense", ["2,000", "6,000"]),
        ("Adjusted operating income", ["15,100", "38,000"]),
        ("Depreciation and amortization", ["4,000", "12,000"]),
        ("Adjusted EBITDA", ["19,100", "50,000"]),
    ]
    roles = {
        "Net income": "gaap_start",
        "Income tax expense": "adjustment",
        "Interest expense": "adjustment",
        "Adjusted operating income": "subtotal",
        "Depreciation and amortization": "adjustment",
        "Adjusted EBITDA": "nongaap_result",
    }
    r = run(rows, roles)
    assert r.verdict == "PASS"
    assert [s.target_kind for s in r.columns[0].segments] == ["subtotal", "nongaap_result"]


def test_wrong_subtotal_flags_at_the_checkpoint():
    rows = [
        ("Net income", ["10,100"]),
        ("Interest expense", ["2,000"]),
        ("Adjusted operating income", ["13,000"]),  # should be 12,100
        ("Depreciation and amortization", ["4,000"]),
        ("Adjusted EBITDA", ["17,000"]),
    ]
    roles = {
        "Net income": "gaap_start",
        "Interest expense": "adjustment",
        "Adjusted operating income": "subtotal",
        "Depreciation and amortization": "adjustment",
        "Adjusted EBITDA": "nongaap_result",
    }
    r = run(rows, roles)
    segs = r.columns[0].segments
    assert segs[0].verdict == "FLAG" and segs[1].verdict == "PASS"


def test_D13_subtotal_misclassified_as_adjustment_is_diagnosed():
    rows = [
        ("Net income", ["10,100"]),
        ("Interest expense", ["2,000"]),
        ("Adjusted operating income", ["12,100"]),
        ("Depreciation and amortization", ["4,000"]),
        ("Adjusted EBITDA", ["16,100"]),
    ]
    roles = {
        "Net income": "gaap_start",
        "Interest expense": "adjustment",
        "Adjusted operating income": "adjustment",  # simulated LLM row-role error
        "Depreciation and amortization": "adjustment",
        "Adjusted EBITDA": "nongaap_result",
    }
    r = run(rows, roles)
    col = r.columns[0]
    assert col.verdict == "NEEDS_REVIEW" and col.reason_code == "possible_subtotal_misclassified"


# ---- abstention / structure
def test_no_gaap_start_is_not_evaluated():
    r = run(BASE, dict(ROLES, **{"Net income": "other"}))
    assert r.verdict == "NOT_EVALUATED" and r.columns[0].reason_code == "no_gaap_start"


def test_memo_rows_never_summed():
    rows = BASE[:5] + [("Memo: capex", ["9,999", "9,999"])] + BASE[5:]
    r = run(rows, dict(ROLES, **{"Memo: capex": "memo"}))
    assert r.verdict == "PASS"


# ---- real-world reconciliations from locked Tier A cases (transcribed; re-verified at ingest)
def test_real_turtle_beach_table5_subtotal_and_uncued_subtraction():
    # A02 Turtle Beach 8-K 2023-08-07, Table 5 (in thousands); starts at operating income (SEC c7)
    # Row labels abbreviated; amounts as transcribed. Starting row = reported operating loss.
    rows = [
        ("Operating loss, as reported", ["(15,793)"]),
        ("Depreciation and amortization", ["971"]),
        ("Stock-based compensation", ["248"]),
        ("Restructuring and other", ["4,970"]),
        ("Business transaction costs", ["4,207"]),
        ("Operating income (loss)", ["(5,397)"]),
        ("Other non-operating expense, net", ["198"]),
        ("Adjusted EBITDA", ["(5,595)"]),
    ]
    roles = {
        "Operating loss, as reported": "gaap_start",
        "Depreciation and amortization": "adjustment",
        "Stock-based compensation": "adjustment",
        "Restructuring and other": "adjustment",
        "Business transaction costs": "adjustment",
        "Operating income (loss)": "subtotal",
        "Other non-operating expense, net": "adjustment",
        "Adjusted EBITDA": "nongaap_result",
    }
    # without the LLM's sign hint: genuinely ambiguous -> must not PASS
    assert run(rows, roles).verdict == "FLAG"
    # with sign_hint=subtract on the expense row (LLM semantic cue) -> ties, lineage records 'llm'
    r = run(rows, roles, subtract={"Other non-operating expense, net"})
    assert r.verdict == "PASS"


def test_real_adient_less_equity_income():
    # A06 Adient 8-K 2024-02-07: Adjusted EBITDA 216, "Less: Adjusted Equity Income 25" -> 191.
    # Arithmetic-only check: the starting row is itself non-GAAP. That is the SEC's
    # c2/c3 point, caught by R-RECON-START-GAAP, not by tie-out.
    rows = [("Adjusted EBITDA", ["216", "205"]), ("Less: Adjusted Equity Income", ["25", "27"]), ("Adjusted EBITDA excluding adjusted equity income", ["191", "178"])]
    roles = {"Adjusted EBITDA": "gaap_start", "Less: Adjusted Equity Income": "adjustment", "Adjusted EBITDA excluding adjusted equity income": "nongaap_result"}
    assert run(rows, roles).verdict == "PASS"


def test_real_citi_trends_negative_printed_subtractions():
    # A04 Citi Trends 8-K 2025-06-03, Adjusted EBITDA reconciliation (in thousands)
    rows = [
        ("Net income (loss)", ["871"]),
        ("Interest income", ["(458)"]),
        ("Interest expense", ["76"]),
        ("Income tax benefit", ["—"]),
        ("Depreciation", ["4,370"]),
        ("Asset impairment", ["64"]),
        ("Cyber incident expenses", ["(402)"]),
        ("Other non-recurring expenses", ["885"]),
        ("Adjusted EBITDA", ["5,406"]),
    ]
    roles = {l: "adjustment" for l, _ in rows}
    roles["Net income (loss)"] = "gaap_start"
    roles["Adjusted EBITDA"] = "nongaap_result"
    assert run(rows, roles).verdict == "PASS"


def test_real_capri_operating_income_columnar_sum():
    # A03 Capri Sch. 6 (in millions): operating loss (38) + 43 + 1 + 4 + 12 + 10 = 32
    rows = [("Income from operations", ["(38)"]), ("Impairment", ["43"]), ("Restructuring", ["1"]), ("ERP", ["4"]), ("Transformation", ["12"]), ("Merger related", ["10"]), ("Adjusted income from operations", ["32"])]
    roles = {l: "adjustment" for l, _ in rows}
    roles["Income from operations"] = "gaap_start"
    roles["Adjusted income from operations"] = "nongaap_result"
    assert run(rows, roles).verdict == "PASS"


# ---- property-based: valid reconciliations always pass; big perturbations never pass
_amount = st.integers(min_value=-500_000, max_value=500_000)


def _fmt(v: int) -> str:
    s = f"{abs(v):,}"
    return f"({s})" if v < 0 else s


@settings(max_examples=60, deadline=None)
@given(start=_amount, adjs=st.lists(_amount, min_size=1, max_size=8))
def test_property_valid_reconciliation_passes(start, adjs):
    rows = [("GAAP measure", [_fmt(start)])] + [(f"Adj {i}", [_fmt(a)]) for i, a in enumerate(adjs)] + [("Non-GAAP measure", [_fmt(start + sum(adjs))])]
    roles = {"GAAP measure": "gaap_start", "Non-GAAP measure": "nongaap_result", **{f"Adj {i}": "adjustment" for i in range(len(adjs))}}
    assert run(rows, roles).verdict == "PASS"


@settings(max_examples=60, deadline=None)
@given(start=_amount, adjs=st.lists(_amount, min_size=1, max_size=8), idx=st.integers(min_value=0), err=st.integers(min_value=10, max_value=10_000))
def test_property_perturbed_reconciliation_never_passes(start, adjs, idx, err):
    i = idx % len(adjs)
    printed = list(adjs)
    printed[i] += err
    rows = [("GAAP measure", [_fmt(start)])] + [(f"Adj {k}", [_fmt(a)]) for k, a in enumerate(printed)] + [("Non-GAAP measure", [_fmt(start + sum(adjs))])]
    roles = {"GAAP measure": "gaap_start", "Non-GAAP measure": "nongaap_result", **{f"Adj {k}": "adjustment" for k in range(len(adjs))}}
    assert run(rows, roles).verdict != "PASS"
