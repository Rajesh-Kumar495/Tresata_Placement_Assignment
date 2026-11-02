"""Deterministic reconciliation tie-out engine (architecture §4.4, ADR-005, ADR-014).

Input: a parsed Table plus row-role assignments (from the LLM row labeller or,
in tests/eval, from gold labels). The LLM never supplies numbers: values are
read from parsed cells here.

The reconciliation is evaluated as a *segmented chain*:

    anchor := gaap_start
    adjustment / tax_effect -> running += effective(row)
    subtotal                -> checkpoint (anchor + running == subtotal), re-anchor
    nongaap_result          -> final check
    memo / other            -> never summed

Verdict bands per segment, with u = unit of the last printed digit:
    |diff| <= u                       PASS          (normal single-digit rounding)
    u < |diff| <= 0.5*u*n_terms       NEEDS_REVIEW  rounding_band (can't tell rounding from error)
    |diff| >  0.5*u*n_terms           FLAG, unless a *diagnosis* explains it -> NEEDS_REVIEW

Diagnoses are explanations for a human, never auto-repairs, and they are
restricted so they cannot explain away arbitrary errors:
    sign_ambiguous                  flipping ONE cue-bearing row closes the gap
    possible_subtotal_misclassified removing ONE adjustment whose value equals the
                                    running total before it (or whose label looks
                                    like a subtotal) closes the gap
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from .docmodel import Row, Table

Role = Literal["gaap_start", "adjustment", "tax_effect", "subtotal", "nongaap_result", "memo", "other"]
SignHint = Literal["as_printed", "subtract"]
Verdict = Literal["PASS", "FLAG", "NEEDS_REVIEW", "NOT_EVALUATED"]

# Deterministic subtraction cues (independent of the LLM's sign_hint).
_SUBTRACT_CUE = re.compile(r"^\s*(less|deduct|minus|subtract|excluding)\b[:\s]", re.I)
_SUBTOTAL_LIKE = re.compile(r"\b(total|subtotal|income \(loss\)|operating income|adjusted [a-z ]+)\b", re.I)


class RowRole(BaseModel):
    row_id: str
    role: Role
    sign_hint: SignHint = "as_printed"


class Term(BaseModel):
    row_id: str
    label: str
    printed: Decimal
    effective: Decimal
    sign_source: Literal["printed", "llm", "lexicon", "llm+lexicon"] = "printed"
    sign_source_conflict: bool = False
    blank_as_zero: bool = False


class Segment(BaseModel):
    anchor_row: str
    anchor_value: Decimal
    terms: list[Term]
    target_row: str
    target_kind: Literal["subtotal", "nongaap_result"]
    reported: Decimal
    computed: Decimal
    diff: Decimal
    unit: Decimal
    strict_tol: Decimal
    band_tol: Decimal
    verdict: Verdict
    reason_code: str | None = None
    diagnosis_row: str | None = None


class ColumnResult(BaseModel):
    col_key: int
    header_path: list[str]
    verdict: Verdict
    reason_code: str | None = None
    segments: list[Segment] = []
    warnings: list[str] = []


class TieOutResult(BaseModel):
    table_id: str
    verdict: Verdict
    columns: list[ColumnResult]


_SEVERITY = {"FLAG": 3, "NEEDS_REVIEW": 2, "NOT_EVALUATED": 1, "PASS": 0}


def lexicon_subtract_cue(label: str) -> bool:
    return bool(_SUBTRACT_CUE.match(label))


def tie_out(table: Table, roles: list[RowRole], columns: list[int] | None = None) -> TieOutResult:
    """Check one reconciliation (the rows named in `roles`) in every value column."""
    role_by_row = {r.row_id: r for r in roles}
    ordered = [row for row in table.rows if row.id in role_by_row]
    if not ordered:
        return TieOutResult(table_id=table.id, verdict="NOT_EVALUATED", columns=[])
    cols = columns if columns is not None else _columns_for(ordered)
    results = [_tie_column(ordered, role_by_row, c) for c in cols]
    worst = max(results, key=lambda r: _SEVERITY[r.verdict]).verdict if results else "NOT_EVALUATED"
    return TieOutResult(table_id=table.id, verdict=worst, columns=results)


# ---------------------------------------------------------------- internals


def _columns_for(rows: list[Row]) -> list[int]:
    keys = {c.col_key for r in rows for c in r.cells if c.number is not None and c.number.value is not None}
    return sorted(keys)


def _value(row: Row, col: int):
    cell = row.value_at(col)
    if cell is None or cell.number is None or cell.number.value is None:
        return None, None
    return cell.number.value, cell


def _effective(row: Row, printed: Decimal, hint: SignHint) -> Term:
    llm = hint == "subtract"
    lex = lexicon_subtract_cue(row.label)
    cue = llm or lex
    source = "llm+lexicon" if (llm and lex) else "llm" if llm else "lexicon" if lex else "printed"
    effective = -abs(printed) if (cue and printed >= 0) else printed
    return Term(
        row_id=row.id,
        label=row.label,
        printed=printed,
        effective=effective,
        sign_source=source if cue and printed >= 0 else "printed",
        sign_source_conflict=llm != lex,
    )


def _tie_column(rows: list[Row], roles: dict[str, RowRole], col: int) -> ColumnResult:
    header = next((c.header_path for r in rows if (c := r.value_at(col)) is not None), [])
    res = ColumnResult(col_key=col, header_path=header, verdict="PASS")

    starts = [r for r in rows if roles[r.id].role == "gaap_start"]
    if not starts:
        res.verdict, res.reason_code = "NOT_EVALUATED", "no_gaap_start"
        return res
    if len(starts) > 1:
        res.verdict, res.reason_code = "NEEDS_REVIEW", "multiple_gaap_start"
        return res
    anchor_row = starts[0]
    anchor, _ = _value(anchor_row, col)
    if anchor is None:
        res.verdict, res.reason_code = "NOT_EVALUATED", "missing_anchor_value"
        return res

    anchor_id, anchor_cell_val = anchor_row.id, anchor
    unit_terms = [anchor_row]
    terms: list[Term] = []
    started = False
    finished = False
    for row in rows:
        role = roles[row.id].role
        if row is anchor_row:
            started = True
            continue
        if not started or role in ("memo", "other"):
            continue
        if finished:
            res.warnings.append(f"row {row.id} after nongaap_result ignored")
            continue
        if role in ("adjustment", "tax_effect"):
            val, _ = _value(row, col)
            if val is None:
                t = Term(row_id=row.id, label=row.label, printed=Decimal(0), effective=Decimal(0), blank_as_zero=True)
            else:
                t = _effective(row, val, roles[row.id].sign_hint)
                unit_terms.append(row)
            terms.append(t)
        elif role in ("subtotal", "nongaap_result"):
            reported, _ = _value(row, col)
            if reported is None:
                res.verdict, res.reason_code = "NOT_EVALUATED", f"missing_{role}_value"
                return res
            seg = _check_segment(anchor_id, anchor_cell_val, terms, row, role, reported, unit_terms + [row], col)
            res.segments.append(seg)
            anchor_id, anchor_cell_val = row.id, reported
            unit_terms, terms = [row], []
            if role == "nongaap_result":
                finished = True
        elif role == "gaap_start":  # pragma: no cover - guarded above
            pass

    if not finished:
        res.verdict, res.reason_code = "NOT_EVALUATED", "no_nongaap_result"
        return res
    res.verdict = max((s.verdict for s in res.segments), key=lambda v: _SEVERITY[v])
    worst = next(s for s in res.segments if s.verdict == res.verdict)
    res.reason_code = worst.reason_code
    return res


def _unit(rows: list[Row], col: int) -> Decimal:
    units = []
    for r in rows:
        _, cell = _value(r, col)
        if cell is not None and not cell.number.is_dash:
            units.append(cell.number.unit)
    return max(units) if units else Decimal(1)


def _check_segment(
    anchor_id: str,
    anchor: Decimal,
    terms: list[Term],
    target: Row,
    kind: str,
    reported: Decimal,
    unit_rows: list[Row],
    col: int,
) -> Segment:
    unit = _unit(unit_rows, col)
    n_terms = 2 + sum(1 for t in terms if not t.blank_as_zero)  # anchor + addends + reported
    strict = unit
    band = Decimal("0.5") * unit * n_terms
    computed = anchor + sum((t.effective for t in terms), Decimal(0))
    diff = reported - computed
    seg = Segment(
        anchor_row=anchor_id,
        anchor_value=anchor,
        terms=terms,
        target_row=target.id,
        target_kind=kind,  # type: ignore[arg-type]
        reported=reported,
        computed=computed,
        diff=diff,
        unit=unit,
        strict_tol=strict,
        band_tol=band,
        verdict="PASS",
    )
    if abs(diff) <= strict:
        return seg
    if abs(diff) <= band:
        seg.verdict, seg.reason_code = "NEEDS_REVIEW", "rounding_band"
        return seg

    # ---- diagnosis (explain, never repair)
    for t in terms:
        cue_bearing = t.sign_source != "printed" or lexicon_subtract_cue(t.label)
        if cue_bearing and abs(reported - (computed - 2 * t.effective)) <= strict:
            seg.verdict, seg.reason_code, seg.diagnosis_row = "NEEDS_REVIEW", "sign_ambiguous", t.row_id
            return seg
    running = anchor
    for t in terms:
        equals_running = abs(t.effective - running) <= strict
        if (equals_running or _SUBTOTAL_LIKE.search(t.label)) and abs(reported - (computed - t.effective)) <= strict:
            seg.verdict, seg.reason_code, seg.diagnosis_row = "NEEDS_REVIEW", "possible_subtotal_misclassified", t.row_id
            return seg
        running += t.effective

    seg.verdict, seg.reason_code = "FLAG", "tieout_mismatch"
    return seg
