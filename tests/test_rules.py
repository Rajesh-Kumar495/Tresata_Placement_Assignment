"""Deterministic rule tests: hand-built inventory + labellings, no LLM."""

from ngr.docmodel import parse_html
from ngr.inventory import GroundedMeasure, Inventory
from ngr.judges import check_forward
from ngr.reconcile import ReconResult, TableLabelling
from ngr.rules import run_rules
from ngr.tieout import RowRole, tie_out


def inv(*measures):
    ms = [GroundedMeasure(name=n, aliases=[], kind=k, per_share=ps, forward_looking=fw, comparable_gaap=None, comparable_gaap_span=None,
                          mentions=[], rationale="") for n, k, ps, fw in measures]
    return Inventory(doc_sha256="x", measures=ms, lexicon=[], unexplained_candidates=[], novel_measures=[], dropped_measures=[], grounding={})


BODY = "<p>" + "ACME reported results for the quarter. " * 8 + "</p>"
RECON = """<p>Reconciliation of net income to Adjusted EBITDA (in thousands)</p><table>
<tr><td></td><td>Q3 2026</td></tr>
<tr><td>Net income</td><td>100</td></tr><tr><td>Interest expense</td><td>20</td></tr><tr><td>Depreciation</td><td>30</td></tr>
<tr><td>Adjusted EBITDA</td><td>150</td></tr></table>"""


def doc(head, extra=""):
    return parse_html(f"<html><body>{head}{BODY}{extra}{RECON}</body></html>")


def labelled(d, start="Net income", measure="Adjusted EBITDA", start_is_gaap=True):
    t = d.tables[-1]
    roles = []
    for r in t.data_rows:
        role = "gaap_start" if r.label == start else "nongaap_result" if r.label == "Adjusted EBITDA" else "adjustment"
        roles.append(RowRole(row_id=r.id, role=role))
    rc = ReconResult(table_id=t.id, measure=measure, orientation="vertical", start_is_gaap=start_is_gaap, start_label=start, tieout=tie_out(t, roles))
    return [TableLabelling(table_id=t.id, is_reconciliation=True, reconciliations=[rc])]


def verdicts(findings, rule):
    return [f.verdict for f in findings if f.rule_id == rule]


I = inv(("Adjusted EBITDA", "performance", False, False))


def test_headline_omits_gaap_flags_and_gaap_first_passes():
    d = doc("<p><b>ACME Reports Adjusted EBITDA of $150 million</b></p>")
    assert "FLAG" in verdicts(run_rules(d, I, labelled(d)), "R-PROM-HEADLINE")
    d2 = doc("<p><b>ACME Reports Net Income of $100 million; Adjusted EBITDA of $150 million</b></p>")
    assert verdicts(run_rules(d2, I, labelled(d2)), "R-PROM-HEADLINE") == ["PASS"]


def test_bullet_nongaap_before_gaap_flags():
    d = doc("<p><b>ACME Reports Q3</b></p>", "<ul><li>Adjusted EBITDA of $150 million</li><li>Net income of $100 million</li></ul>")
    assert "FLAG" in verdicts(run_rules(d, I, labelled(d)), "R-PROM-ORDER")


def test_style_emphasis_flags():
    head = '<p><span style="font-weight:normal;font-size:10pt">Net income of $100 million; </span><span style="font-weight:bold;font-size:16pt">Adjusted EBITDA of $150 million</span></p>'
    d = doc(head)
    assert "FLAG" in verdicts(run_rules(d, I, labelled(d)), "R-PROM-STYLE")


def test_reconciled_measure_passes_unreconciled_flags():
    d = doc("<p>ACME Q3</p>")
    assert verdicts(run_rules(d, I, labelled(d)), "R-RECON-PRESENT") == ["PASS"]
    i2 = inv(("Adjusted EBITDA", "performance", False, False), ("Adjusted free cash flow", "liquidity", False, False))
    assert "FLAG" in verdicts(run_rules(d, i2, labelled(d)), "R-RECON-PRESENT")


def test_ebitda_from_operating_income_flags():
    d = parse_html(f"<html><body><p>ACME Q3</p>{BODY}" + RECON.replace("Net income", "Operating income") + "</body></html>")
    assert "FLAG" in verdicts(run_rules(d, I, labelled(d, start="Operating income")), "R-EBITDA-FROM-NI")


def test_plain_ebitda_title_with_extra_adjustments_flags():
    r = RECON.replace("Interest expense", "Restructuring").replace(">Adjusted EBITDA<", ">EBITDA<")
    d = parse_html(f"<html><body><p>ACME Q3</p>{BODY}{r}</body></html>")
    t = d.tables[-1]
    roles = [RowRole(row_id=x.id, role="gaap_start" if x.label == "Net income" else "nongaap_result" if x.label == "EBITDA" else "adjustment") for x in t.data_rows]
    lab = [TableLabelling(table_id=t.id, is_reconciliation=True, reconciliations=[ReconResult(table_id=t.id, measure="EBITDA", orientation="vertical", start_is_gaap=True, start_label="Net income", tieout=tie_out(t, roles))])]
    assert "FLAG" in verdicts(run_rules(d, inv(("EBITDA", "performance", False, False)), lab), "R-EBITDA-LABEL")


def test_non_gaap_start_flags():
    d = doc("<p>ACME Q3</p>")
    assert "FLAG" in verdicts(run_rules(d, I, labelled(d, start_is_gaap=False)), "R-RECON-START-GAAP")


def test_net_of_tax_flags():
    r = RECON.replace("<tr><td>Interest expense", "<tr><td>Adjustments, net of tax:</td></tr><tr><td>Interest expense")
    d = parse_html(f"<html><body><p>ACME Q3</p>{BODY}{r}</body></html>")
    assert "FLAG" in verdicts(run_rules(d, I, labelled(d)), "R-TAX-SEPARATE")


def test_per_share_liquidity_flags():
    d = doc("<p>ACME Q3</p>", "<p>Free cash flow per share was $1.23.</p>")
    assert "FLAG" in verdicts(run_rules(d, I, labelled(d)), "R-PERSHARE-LIQ")


def test_forward_looking_needs_exception_disclosure():
    i2 = inv(("Adjusted EBITDA", "performance", False, False))
    d = doc("<p>ACME Q3</p>", "<p>For fiscal 2027 we expect Adjusted EBITDA of $600 million to $650 million.</p>")
    assert "FLAG" in [f.verdict for f in check_forward(d, i2)]
    d2 = doc("<p>ACME Q3</p>", "<p>For fiscal 2027 we expect Adjusted EBITDA of $600 million to $650 million.</p>"
             "<p>We have not reconciled forward-looking non-GAAP guidance to GAAP because doing so would require unreasonable efforts.</p>")
    assert [f.verdict for f in check_forward(d2, i2)] == ["PASS"]
