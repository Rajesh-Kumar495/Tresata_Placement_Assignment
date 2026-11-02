from decimal import Decimal

from helpers import parse_table

from ngr.docmodel import parse_html

RELEASE = """
<html><body>
<p style="font-weight:bold;font-size:14pt">ACME CORP ANNOUNCES THIRD QUARTER 2026 RESULTS</p>
<p style="font-size:12pt"><b>Adjusted EPS of $1.42; Revenue Up 8%</b></p>
<table>
  <tr><td>•</td><td>Net income of $10.1 million, or $0.31 per diluted share</td></tr>
  <tr><td>•</td><td>Adjusted EBITDA of $41.0 million</td></tr>
</table>
<p style="font-size:10pt">CHICAGO, Oct. 30, 2026 -- Acme Corp today reported results for the third quarter. Revenue
increased 8% compared with the prior year driven by volume and price, partially offset by mix. Management
believes these non-GAAP measures are useful to investors because they exclude items that are not indicative of
ongoing performance.</p>
<p>Reconciliation of Net Income to Adjusted EBITDA (in thousands)</p>
<table>
  <tr><td></td><td colspan="3">Three Months Ended</td><td colspan="3">Nine Months Ended</td></tr>
  <tr><td></td><td colspan="3">September 30, 2026</td><td colspan="3">September 30, 2026</td></tr>
  <tr><td>Net income</td><td>$</td><td>10,100</td><td></td><td>$</td><td>25,000</td><td></td></tr>
  <tr><td>Interest expense</td><td></td><td>2,000</td><td></td><td></td><td>6,000</td><td></td></tr>
  <tr><td>Less: gain on sale</td><td></td><td>500</td><td></td><td></td><td>—</td><td></td></tr>
  <tr><td>Adjusted EBITDA</td><td>$</td><td>11,600</td><td></td><td>$</td><td>31,000</td><td></td></tr>
</table>
<img src="chart.jpg" alt="EBITDA chart">
</body></html>
"""


def test_blocks_tables_images_and_order():
    doc = parse_html(RELEASE)
    assert len(doc.tables) == 1  # the bullet layout table is not a data table
    assert [i.src for i in doc.images] == ["chart.jpg"]
    texts = [b.text for b in doc.blocks]
    assert texts[0].startswith("ACME CORP ANNOUNCES")
    assert any("Adjusted EBITDA of $41.0 million" in t for t in texts)


def test_headline_and_bullet_classification():
    doc = parse_html(RELEASE)
    kinds = {b.text[:20]: b.kind for b in doc.blocks}
    assert kinds["ACME CORP ANNOUNCES "] == "headline"
    assert kinds["Adjusted EPS of $1.4"] == "headline"
    assert kinds["• Net income of $10."] == "bullet"
    body = next(b for b in doc.blocks if b.text.startswith("CHICAGO"))
    assert body.kind == "paragraph"


def test_style_runs():
    doc = parse_html(RELEASE)
    second = doc.blocks[1]
    assert second.bold_fraction == 1.0
    assert second.max_font_pt == 12.0


def test_table_cells_header_paths_and_scale():
    doc = parse_html(RELEASE)
    t = doc.tables[0]
    assert t.scale == "thousands"
    labels = [r.label for r in t.data_rows]
    assert labels == ["Net income", "Interest expense", "Less: gain on sale", "Adjusted EBITDA"]
    ni = t.data_rows[0]
    assert [c.number.value for c in ni.cells] == [Decimal(10100), Decimal(25000)]
    assert ni.cells[0].header_path == ["Three Months Ended", "September 30, 2026"]
    assert ni.cells[1].header_path == ["Nine Months Ended", "September 30, 2026"]
    # value columns align across rows whether or not a '$' cell is present
    assert len(t.value_columns()) == 2
    dash = t.data_rows[2].cells[1].number
    assert dash.is_dash and dash.value == 0


def test_split_paren_negative_merged_and_aligned():
    _, t = parse_table([("Net loss", ["(15,793)", "(1,000)"]), ("D&A", ["971", "50"]), ("Adj", ["(14,822)", "(950)"])])
    assert [c.number.value for c in t.data_rows[0].cells] == [Decimal(-15793), Decimal(-1000)]
    keys = [[c.col_key for c in r.cells] for r in t.data_rows]
    assert keys[0] == keys[1] == keys[2]


def test_stable_ids_and_char_spans_ground_text():
    a = parse_html(RELEASE)
    b = parse_html(RELEASE)
    assert [x.id for x in a.blocks] == [x.id for x in b.blocks]
    assert a.sha256 == b.sha256
    for blk in a.blocks:
        assert a.text[blk.char_start : blk.char_end] == blk.text
    row = a.tables[0].data_rows[0]
    assert a.text[row.char_start : row.char_end].startswith("Net income")


def test_image_only_headline_detectable():
    doc = parse_html('<html><body><img src="infographic.jpg"><p>Reconciliation follows.</p></body></html>')
    assert doc.images and doc.images[0].order < doc.blocks[0].order
