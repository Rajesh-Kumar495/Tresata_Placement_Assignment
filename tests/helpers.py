"""Test helpers: build EDGAR-style HTML tables so tests exercise the real parser.

EDGAR Ex 99.1 tables typically split '$' and ')' into their own cells and use
colspan headers; `edgar_table` reproduces that so tie-out tests run on parsed
cells, never on hand-made Decimals.
"""

from __future__ import annotations

from ngr.docmodel import Document, Table, parse_html
from ngr.tieout import RowRole


def _value_cells(v: str) -> str:
    """One printed value -> EDGAR-style cells: '$' | '(1,234' | ')'."""
    v = v.strip()
    dollar = v.startswith("$")
    if dollar:
        v = v[1:].strip()
    close = ""
    if v.startswith("(") and v.endswith(")"):
        v, close = v[:-1], ")"
    return f"<td>{'$' if dollar else ''}</td><td>{v}</td><td>{close}</td>"


def edgar_table(rows: list[tuple[str, list[str]]], headers: list[str], caption: str = "(in thousands)") -> str:
    head = "<tr><td></td>" + "".join(f'<td colspan="3">{h}</td>' for h in headers) + "</tr>"
    body = "".join("<tr><td>" + label + "</td>" + "".join(_value_cells(v) for v in vals) + "</tr>" for label, vals in rows)
    return f"<p>{caption}</p><table>{head}{body}</table>"


def parse_table(rows: list[tuple[str, list[str]]], headers: list[str] | None = None, caption: str = "(in thousands)") -> tuple[Document, Table]:
    headers = headers or [f"P{i + 1}" for i in range(len(rows[0][1]))]
    doc = parse_html(f"<html><body>{edgar_table(rows, headers, caption)}</body></html>")
    assert len(doc.tables) == 1, "fixture should yield exactly one data table"
    return doc, doc.tables[0]


def roles_by_label(table: Table, spec: dict[str, str], subtract: set[str] = frozenset()) -> list[RowRole]:
    """Map row labels -> roles; labels not in spec are omitted (not part of the reconciliation)."""
    out = []
    for row in table.data_rows:
        if row.label in spec:
            out.append(RowRole(row_id=row.id, role=spec[row.label], sign_hint="subtract" if row.label in subtract else "as_printed"))
    missing = set(spec) - {r.label for r in table.data_rows}
    assert not missing, f"labels not found in parsed table: {missing}"
    return out
