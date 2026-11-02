"""MVP deterministic rules (architecture §6.2). Pure functions over the document model,
the HC1 inventory and the labelled reconciliations; no I/O, no randomness.

"d_over_l" rules are deterministic logic over facts an LLM proposed (measure names,
kinds, row roles); their lineage says so, and HC1 confirmation upgrades them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .docmodel import Block, Document, Table
from .findings import Evidence, Finding, make
from .inventory import _LEX_RE, Inventory, _tokens, names_match
from .reconcile import ReconResult, TableLabelling

# ---------------------------------------------------------------- GAAP comparables

_NOT_GAAP_PREFIX = re.compile(r"(adjusted|non-gaap|non gaap|core|modified|pro forma|constant currency|organic|excluding special items)[\s\-:,]*$", re.I)
_NI = r"net\s+(?:\(loss\)\s+|\(income\)\s+)?(?:income|loss|earnings)(?:\s*\((?:loss|income)\))?"
_FAM = {
    "net_margin": r"net\s+(?:income|loss|earnings)?\s*margin",
    "operating_margin": r"operating\s+(?:income\s+)?margin",
    "gross": r"gross\s+(?:margin|profit)",
    "eps": r"(?:diluted\s+)?(?:net\s+)?(?:earnings|income|loss)(?:\s*\((?:loss|earnings)\))?\s+per\s+(?:diluted\s+)?(?:ordinary\s+|common\s+)?share|\b(?:diluted\s+)?EPS\b",
    "net_income": _NI,
    "operating_income": r"operating\s+(?:income|loss|profit)(?:\s*\((?:loss|income)\))?|income\s+from\s+operations|(?:income|loss)\s+from\s+operations",
    "opex": r"operating\s+expenses?",
    "cash_ops": r"cash\s+(?:flows?\s+)?(?:provided\s+by|from|generated\s+(?:by|from)|used\s+in)\s+operat|operating\s+cash\s+flow",
    "revenue": r"\b(?:revenue|net\s+sales|sales)\b",
    "sga": r"selling,?\s+general\s+and\s+administrative|\bSG&A\b",
    "sa": r"selling\s+and\s+administrative",
    "rnd": r"research\s+and\s+development|\bR&D\b",
    "tax": r"income\s+tax(?:es)?|tax\s+provision|provision\s+for\s+(?:\(benefit\s+from\)\s+)?income\s+taxes",
    "debt": r"total\s+(?:debt|borrowings)|long-term\s+debt",
}


def gaap_family(name: str) -> str | None:
    n = name.lower()
    if "margin" in n:
        if "ebit" in n or "net" in n:
            return "net_margin"
        if "operating" in n:
            return "operating_margin"
        if "gross" in n:
            return "gross"
    if re.search(r"per\s+(diluted\s+)?share|\beps\b", n):
        return "eps"
    if "ebit" in n or "flowthrough" in n:
        return "net_income"
    if "cash flow" in n:
        return "cash_ops"
    if "net debt" in n or "leverage" in n:
        return "debt"
    if "operating expense" in n:
        return "opex"
    if re.search(r"operating\s+(income|loss|profit)|from\s+operations", n):
        return "operating_income"
    if "gross" in n:
        return "gross"
    if re.search(r"net\s+(income|loss|earnings)|\bearnings\b", n):
        return "net_income"
    if "sg&a" in n or "selling, general" in n:
        return "sga"
    if "selling and administrative" in n:
        return "sa"
    if "r&d" in n or "research" in n:
        return "rnd"
    if "tax" in n:
        return "tax"
    if "constant currency" in n or "organic" in n or "revenue" in n or "sales" in n:
        return "revenue"
    return None


def first_gaap(text: str, family: str, before: int | None = None) -> int | None:
    """Earliest position of a GAAP (non-adjusted) mention of `family` in text, or None."""
    for m in re.finditer(_FAM[family], text, re.I):
        if before is not None and m.start() >= before:
            return None
        if _NOT_GAAP_PREFIX.search(text[max(0, m.start() - 30) : m.start()]):
            continue
        return m.start()
    return None


# ---------------------------------------------------------------- mentions


@dataclass
class Mention:
    measure: str
    block: Block
    start: int
    end: int
    source: str  # inventory | lexicon


def mentions_in(text: str, inv: Inventory) -> list[tuple[str, int, int, str]]:
    found: list[tuple[str, int, int, str]] = []
    for m in inv.measures:
        for n in [m.name, *m.aliases]:
            if len(n) < 4 or not _tokens(n):  # generic aliases ("Non-GAAP") would match everything
                continue
            for hit in re.finditer(re.escape(n), text, re.I):
                # the matched text decides the GAAP family: an alias like "Non-GAAP R&D expenses" under
                # "Non-GAAP operating expenses" must be compared with GAAP R&D, not GAAP opex
                found.append((n if gaap_family(n) else m.name, hit.start(), hit.end(), "inventory"))
    for hit in _LEX_RE.finditer(text):
        found.append((hit.group(0), hit.start(), hit.end(), "lexicon"))
    found.sort(key=lambda x: (x[1], -(x[2] - x[1])))
    out, last_end = [], -1
    for f in found:  # drop overlaps, keep earliest/longest
        if f[1] >= last_end:
            out.append(f)
            last_end = f[2]
    return out


def block_mentions(b: Block, inv: Inventory) -> list[Mention]:
    return [Mention(n, b, s, e, src) for n, s, e, src in mentions_in(b.text, inv)]


def _ev(b: Block) -> Evidence:
    return Evidence(ref=b.id, quote=b.text[:400], char_start=b.char_start, char_end=b.char_end)


# ---------------------------------------------------------------- review context


@dataclass
class Ctx:
    doc: Document
    inv: Inventory
    labellings: list[TableLabelling]
    findings: list[Finding] = field(default_factory=list)

    @property
    def headline(self) -> list[Block]:
        return [b for b in self.doc.blocks if b.kind == "headline"]

    @property
    def body_start_order(self) -> int:
        for b in self.doc.blocks:
            if b.kind not in ("headline", "bullet") and len(b.text) >= 200:
                return b.order
        return 10**9

    def headline_is_image(self) -> bool:
        """Images inside the headline region and no financial figures in its text (Adient)."""
        region = self.headline
        if not region:
            return bool(self.doc.images)
        first, end = region[0].order, self.body_start_order
        imgs = [i for i in self.doc.images if first < i.order < end]
        text_mentions = any(block_mentions(b, self.inv) or re.search(r"\$\s?\d", b.text) for b in region)
        return bool(imgs) and not text_mentions

    def recons(self) -> list[tuple[Table, ReconResult]]:
        out = []
        for lab in self.labellings:
            t = self.doc.table(lab.table_id)
            out += [(t, rc) for rc in lab.reconciliations]
        return out

    def caption_block(self, t: Table) -> Block | None:
        prior = [b for b in self.doc.blocks if b.order < t.order]
        return prior[-1] if prior else None


def _qualifiers(s: str) -> set[str]:
    q = {"modified", "excluding", "special", "core", "organic", "constant", "unlevered", "run", "margin", "ratio", "rate", "flowthrough", "eps", "guidance", "outlook", "segment", "leverage"}
    return _tokens(s) & q


def strict_match(a: str, b: str) -> bool:
    return names_match(a, b) and _qualifiers(a) == _qualifiers(b)


def _row_label(t: Table, row_id: str) -> str:
    try:
        return t.row(row_id).label
    except KeyError:
        return ""


def _col_header(t: Table, col_key: int) -> str:
    for r in t.data_rows:
        c = r.value_at(col_key)
        if c is not None and c.header_path:
            return " / ".join(c.header_path)
    return ""


def recon_start_label(t: Table, rc: ReconResult) -> str:
    if not rc.tieout or not rc.tieout.columns or not rc.tieout.columns[0].segments:
        return rc.start_label
    anchor = rc.tieout.columns[0].segments[0].anchor_row
    if ".col" in anchor:
        return _col_header(t, int(anchor.rsplit("col", 1)[1]))
    return _row_label(t, anchor)


def recon_result_names(t: Table, rc: ReconResult) -> list[str]:
    names = [rc.measure.split(" [group")[0]]
    to = rc.tieout
    if not to:
        return names
    if to.orientation == "horizontal":
        for c in to.columns:
            lbl = c.header_path[0] if c.header_path else ""
            names += [lbl, f"adjusted {lbl}", f"non-gaap {lbl}"]
    else:
        for c in to.columns:
            for s in c.segments:
                names.append(_row_label(t, s.target_row))
    return [n for n in names if n]


def _recon_evidence(ctx: Ctx, t: Table, rc: ReconResult, row_ids: list[str]) -> list[Evidence]:
    ev = []
    # caption context = up to 3 preceding blocks (same window as Table.context_before): titles are often split
    # across blocks, e.g. Turtle Beach "GAAP to Adjusted EBITDA Reconciliation" / "(in thousands)" / "Table 5."
    for b in [b for b in ctx.doc.blocks if b.order < t.order][-3:]:
        ev.append(Evidence(ref=b.id, quote=b.text[-200:]))
    ev.append(Evidence(ref=t.id, quote=f"table {t.id}: {rc.measure}"))
    for rid in row_ids:
        if not rid or ".col" in rid:
            continue
        try:
            r = t.row(rid)
            ev.append(Evidence(ref=r.id, quote=r.label, char_start=r.char_start, char_end=r.char_end))
        except KeyError:
            pass
    return ev


# ---------------------------------------------------------------- rules


def r_prom_headline(ctx: Ctx) -> None:
    if ctx.headline_is_image():
        ctx.findings.append(make("R-PROM-HEADLINE", "NOT_EVALUATED", "headline", "Headline/highlights are images; text not available (ADR-011)", reason_code="headline_is_image"))
        return
    region = ctx.headline
    text, offsets = "", []
    for b in region:
        offsets.append((len(text), b))
        text += b.text + "\n"
    seen: set[str] = set()
    flagged = 0
    for start, b in offsets:
        for m in block_mentions(b, ctx.inv):
            key = m.measure.lower()
            fam = gaap_family(m.measure)
            if key in seen or fam is None:
                continue
            seen.add(key)
            pos = start + m.start
            g = first_gaap(text, fam)
            if g is None or g > pos:
                flagged += 1
                why = "omits" if g is None else "presents the non-GAAP measure before"
                ctx.findings.append(make(
                    "R-PROM-HEADLINE", "FLAG", m.measure,
                    f"Headline {why} the most directly comparable GAAP measure ({fam.replace('_', ' ')}) for '{b.text[m.start:m.end]}'",
                    evidence=[_ev(b)], reason_code="gaap_omitted" if g is None else "nongaap_first",
                    llm_inputs=["inventory measure names"] if m.source == "inventory" else []))
    if not flagged:
        ctx.findings.append(make("R-PROM-HEADLINE", "PASS", "headline", f"{len(seen)} non-GAAP mention(s) in headline; GAAP comparable present and first",
                                 evidence=[_ev(b) for b in region[:3]]))


def _bullet_groups(doc: Document) -> list[list[Block]]:
    groups, cur, prev_idx = [], [], None
    for i, b in enumerate(doc.blocks):
        if b.kind == "bullet" and b.text.strip(" •·▪◦●■") != "":
            if prev_idx is not None and i - prev_idx > 2:
                groups.append(cur)
                cur = []
            cur.append(b)
            prev_idx = i
    if cur:
        groups.append(cur)
    return groups


def r_prom_order(ctx: Ctx) -> None:
    flagged = 0
    for group in _bullet_groups(ctx.doc):
        text, offsets = "", []
        for b in group:
            offsets.append((len(text), b))
            text += b.text + "\n"
        seen: set[str] = set()
        for start, b in offsets:
            for m in block_mentions(b, ctx.inv):
                fam = gaap_family(m.measure)
                if fam is None or m.measure.lower() in seen:
                    continue
                seen.add(m.measure.lower())
                g = first_gaap(text, fam)
                if g is None or g > start + m.start:
                    flagged += 1
                    ctx.findings.append(make(
                        "R-PROM-ORDER", "FLAG", m.measure,
                        f"Bullet presents '{b.text[m.start:m.end]}' {'without' if g is None else 'before'} the comparable GAAP measure ({fam.replace('_', ' ')}) in the same list",
                        evidence=[_ev(b)], reason_code="gaap_omitted" if g is None else "nongaap_first"))
    for t in ctx.doc.tables:
        labels = ""
        reported: set[str] = set()
        for r in t.data_rows:  # section rows ("Net loss per share:") count as GAAP context for the rows below
            if not r.cells:
                labels += r.label + "\n"
                continue
            for n, s, e, src in mentions_in(r.label, ctx.inv):
                fam = gaap_family(n)
                if fam is None or fam in reported:
                    continue
                if first_gaap(labels + r.label, fam, before=len(labels) + s) is None:
                    reported.add(fam)
                    flagged += 1
                    cap = ctx.caption_block(t)
                    ctx.findings.append(make(
                        "R-PROM-ORDER", "FLAG", n,
                        f"Table {t.id}: non-GAAP row '{r.label}' appears without a preceding GAAP {fam.replace('_', ' ')} row",
                        evidence=[Evidence(ref=r.id, quote=r.label, char_start=r.char_start, char_end=r.char_end)] + ([Evidence(ref=cap.id, quote=cap.text[-200:])] if cap else []),
                        reason_code="table_nongaap_first"))
            labels += r.label + "\n"
    if not flagged:
        ctx.findings.append(make("R-PROM-ORDER", "PASS", "bullets/tables", "No non-GAAP measure precedes or replaces its GAAP comparable in bullets or summary tables"))


def _style_at(b: Block, offset: int):
    """(bold, font_pt) of the run covering `offset` in the whitespace-normalised block text."""
    out_idx, run_of = 0, []
    pending_space = False
    for ri, r in enumerate(b.runs):
        for ch in r.text:
            if ch.isspace():
                pending_space = out_idx > 0
                continue
            if pending_space:
                run_of.append(ri)
                out_idx += 1
                pending_space = False
            run_of.append(ri)
            out_idx += 1
    if offset >= len(run_of):
        return None
    r = b.runs[run_of[offset]]
    return r.bold, r.font_size_pt


def r_prom_style(ctx: Ctx) -> None:
    if ctx.headline_is_image():
        ctx.findings.append(make("R-PROM-STYLE", "NOT_EVALUATED", "headline", "Headline/highlights are images; style not available", reason_code="headline_is_image"))
        return
    flagged = compared = 0
    blocks = ctx.headline + [b for g in _bullet_groups(ctx.doc) for b in g]
    for b in blocks:
        for m in block_mentions(b, ctx.inv):
            fam = gaap_family(m.measure)
            if fam is None:
                continue
            g = first_gaap(b.text, fam)
            if g is None:
                continue
            s_n, s_g = _style_at(b, m.start), _style_at(b, g)
            if not s_n or not s_g:
                continue
            compared += 1
            bold_more = s_n[0] and not s_g[0]
            bigger = (s_n[1] or 0) - (s_g[1] or 0) >= 1.0 if (s_n[1] and s_g[1]) else False
            if bold_more or bigger:
                flagged += 1
                ctx.findings.append(make(
                    "R-PROM-STYLE", "FLAG", m.measure,
                    f"'{b.text[m.start:m.end]}' is styled more prominently than its GAAP comparable ({'bold' if bold_more else ''}{' larger font' if bigger else ''})",
                    evidence=[_ev(b)], reason_code="emphasis"))
    if not flagged:
        ctx.findings.append(make("R-PROM-STYLE", "PASS", "headline/bullets", f"{compared} GAAP/non-GAAP pair(s) compared; no extra emphasis on non-GAAP"))


def r_recon_present(ctx: Ctx) -> None:
    reconciled = [n for t, rc in ctx.recons() if rc.tieout for n in recon_result_names(t, rc)]
    candidates = []
    for m in ctx.inv.measures:
        if m.forward_looking:
            continue
        # aliases must name the SAME measure; the LLM sometimes lumps distinct measures as aliases
        # (Aviat: R&D and S&A listed as aliases of total opex) -> those become separate candidates
        true_alias = [a for a in m.aliases if names_match(a, m.name)]
        candidates.append((m.name, true_alias, m.mentions, "inventory"))
        candidates += [(a, [], m.mentions, "inventory") for a in m.aliases if a not in true_alias and gaap_family(a)]
    candidates += [(term, [], [], "lexicon") for term in ctx.inv.unexplained_candidates if gaap_family(term)]
    flagged = 0
    gaap_eps_shown = first_gaap(ctx.doc.text, "eps") is not None
    for name, aliases, spans, src in candidates:
        if any(strict_match(n, r) for n in [name, *aliases] for r in reconciled):
            continue
        if gaap_family(name) == "eps" and gaap_eps_shown:
            # derived per-share figure: numerator reconciled + GAAP EPS presented (common practice, e.g. Aviat)
            numer = re.sub(r"(?i)\s*(diluted\s+)?(earnings|net income|income|loss)?\s*(\(loss\)\s*)?per\s+(diluted\s+)?(ordinary\s+|common\s+)?share|\s*\beps\b", " net income", name)
            if any(strict_match(numer, r) for r in reconciled):
                continue
        blocks = {s.ref for s in spans}
        ev_blocks = [b for b in ctx.doc.blocks if b.id in blocks or re.search(re.escape(name), b.text, re.I)]
        if "constant currency" in name.lower() and any(re.search(r"reported", b.text, re.I) for b in ev_blocks):
            continue  # C&DI 104.06: historical + constant-currency side by side satisfies reconciliation
        flagged += 1
        verdict = "FLAG" if src == "inventory" else "NEEDS_REVIEW"
        ctx.findings.append(make(
            "R-RECON-PRESENT", verdict, name,
            f"No quantitative reconciliation to the most directly comparable GAAP measure found for '{name}'"
            + ("" if src == "inventory" else " (lexicon candidate not confirmed as a measure)"),
            evidence=[_ev(b) for b in ev_blocks[:4]], reason_code="no_reconciliation",
            llm_inputs=["inventory measure", "row-role labelling"] if src == "inventory" else ["row-role labelling"]))
    if not flagged:
        ctx.findings.append(make("R-RECON-PRESENT", "PASS", "all measures", f"{len(candidates)} measure(s) checked; each has a reconciliation"))


def _gaap_result_names(ctx: Ctx) -> list[str]:
    out = []
    for t, rc in ctx.recons():
        if rc.tieout and rc.start_is_gaap and not re.search(r"\b(adjusted|non-gaap)\b", recon_start_label(t, rc), re.I):
            out += recon_result_names(t, rc)
    return out


def _nongaap_start(t: Table, rc: ReconResult) -> bool:
    return (not rc.start_is_gaap) or bool(re.search(r"\b(adjusted|non-gaap|modified)\b", recon_start_label(t, rc), re.I))


def r_recon_start_gaap(ctx: Ctx) -> None:
    gaap_results = _gaap_result_names(ctx)
    flagged = 0
    for t, rc in ctx.recons():
        if not rc.tieout or not _nongaap_start(t, rc):
            continue
        start = recon_start_label(t, rc)
        chained = any(names_match(start, g) or names_match(re.sub(r"(?i)\badjusted\b", "", start), g) for g in gaap_results)
        flagged += 1
        anchor = rc.tieout.columns[0].segments[0].anchor_row if rc.tieout.columns and rc.tieout.columns[0].segments else ""
        ctx.findings.append(make(
            "R-RECON-START-GAAP", "NEEDS_REVIEW" if chained else "FLAG", rc.measure,
            f"Reconciliation of '{rc.measure}' in {t.id} starts from '{start}', a non-GAAP figure"
            + (" that is itself reconciled from GAAP elsewhere in the release (chained)" if chained else ""),
            evidence=_recon_evidence(ctx, t, rc, [anchor]), reason_code="chained_from_reconciled_measure" if chained else "starts_from_nongaap",
            llm_inputs=["row-role labelling (start_is_gaap)"]))
    if not flagged:
        ctx.findings.append(make("R-RECON-START-GAAP", "PASS", "reconciliations", "All reconciliations start from a GAAP measure"))


def r_ebitda(ctx: Ctx) -> None:
    flagged_ni = flagged_lbl = 0
    for t, rc in ctx.recons():
        to = rc.tieout
        if not to or not re.search(r"\bebitda?\b", rc.measure, re.I):
            continue
        anchor = to.columns[0].segments[0].anchor_row if to.columns and to.columns[0].segments else ""
        if not _nongaap_start(t, rc):
            if to.orientation == "horizontal":
                ok = any(re.search(_NI, (c.header_path or [""])[0], re.I) for c in to.columns)
                start = "line items: " + ", ".join((c.header_path or [""])[0] for c in to.columns[:4])
            else:
                start = recon_start_label(t, rc)
                ok = bool(re.search(_NI, start, re.I))
            if not ok:
                flagged_ni += 1
                ctx.findings.append(make(
                    "R-EBITDA-FROM-NI", "FLAG", rc.measure,
                    f"'{rc.measure}' ({t.id}) is reconciled from {start!r}, not from GAAP net income (C&DI 103.02)",
                    evidence=_recon_evidence(ctx, t, rc, [anchor]), reason_code="not_from_net_income", llm_inputs=["row-role labelling"]))
        # 103.01: a measure titled plain "EBITDA"/"EBIT" may only remove interest, taxes, D&A
        title = re.sub(r"[\*\d\(\)]", "", rc.measure).strip()
        if re.fullmatch(r"(?i)ebitda?", title) and to.orientation == "vertical":
            extra = sorted({x.label for c in to.columns for s in c.segments for x in s.terms
                            if not re.search(r"interest|tax|depreciation|amortization", x.label, re.I)})
            if extra:
                flagged_lbl += 1
                ctx.findings.append(make(
                    "R-EBITDA-LABEL", "FLAG", rc.measure,
                    f"Measure titled '{rc.measure}' also adjusts for {extra[:4]}; it should be titled e.g. 'Adjusted EBITDA' (C&DI 103.01)",
                    evidence=_recon_evidence(ctx, t, rc, [anchor]), reason_code="ebitda_with_other_adjustments", llm_inputs=["row-role labelling"]))
    if not flagged_ni:
        ctx.findings.append(make("R-EBITDA-FROM-NI", "PASS", "EBITDA reconciliations", "EBITDA/EBIT reconciliations start from net income (or none present)"))
    if not flagged_lbl:
        ctx.findings.append(make("R-EBITDA-LABEL", "PASS", "EBITDA titles", "No plain 'EBITDA'/'EBIT' title with non-standard adjustments"))


def r_tax_separate(ctx: Ctx) -> None:
    flagged = 0
    for t in {t.id: t for t, _ in ctx.recons()}.values():
        rows = [r for r in t.rows if re.search(r"net\s+of\s+(income\s+)?tax", r.label, re.I)]
        ctx_hit = re.search(r"net\s+of\s+(income\s+)?tax", t.context_before[-200:], re.I)
        has_tax_line = any(re.search(r"tax\s+(effect|impact)|income\s+tax(es)?\s+(on|of|related to)\s+(the\s+)?(above\s+)?adjustments|tax\s+adjustments?", r.label, re.I) for r in t.rows)
        if (rows or ctx_hit) and not has_tax_line:
            flagged += 1
            r = rows[0] if rows else None
            ev = [Evidence(ref=r.id, quote=r.label, char_start=r.char_start, char_end=r.char_end)] if r else []
            cap = ctx.caption_block(t)
            ctx.findings.append(make(
                "R-TAX-SEPARATE", "FLAG", t.id,
                f"Adjustments in {t.id} are presented net of tax without a separate income-tax adjustment line (C&DI 102.11)",
                evidence=ev + ([Evidence(ref=cap.id, quote=cap.text[-200:])] if cap else []), reason_code="net_of_tax", check_type="deterministic"))
    if not flagged:
        ctx.findings.append(make("R-TAX-SEPARATE", "PASS", "reconciliations", "No net-of-tax adjustment presentation found"))


_PERSHARE_LIQ = re.compile(r"(free\s+cash\s+flows?|cash\s+flows?|fcf)\s+(per|/)\s+(diluted\s+)?share", re.I)


def r_pershare_liq(ctx: Ctx) -> None:
    flagged = 0
    for m in ctx.inv.measures:
        if m.kind == "liquidity" and m.per_share:
            flagged += 1
            ctx.findings.append(make("R-PERSHARE-LIQ", "FLAG", m.name, f"Liquidity measure '{m.name}' presented per share (C&DI 102.05/102.07)",
                                     evidence=[Evidence(ref=s.ref, quote=s.quote, char_start=s.char_start, char_end=s.char_end) for s in m.mentions[:2]],
                                     reason_code="liquidity_per_share", llm_inputs=["inventory kind/per_share"]))
    for b in ctx.doc.blocks:
        hit = _PERSHARE_LIQ.search(b.text)
        if hit and not any(f.rule_id == "R-PERSHARE-LIQ" and f.verdict == "FLAG" and any(e.ref == b.id for e in f.evidence) for f in ctx.findings):
            flagged += 1
            ctx.findings.append(make("R-PERSHARE-LIQ", "FLAG", hit.group(0), f"'{hit.group(0)}' presents a liquidity measure per share",
                                     evidence=[_ev(b)], reason_code="liquidity_per_share", check_type="deterministic"))
    if not flagged:
        ctx.findings.append(make("R-PERSHARE-LIQ", "PASS", "liquidity measures", "No liquidity measure presented per share"))


def r_recon_tieout(ctx: Ctx) -> None:
    for t, rc in ctx.recons():
        to = rc.tieout
        if to is None:
            ctx.findings.append(make("R-RECON-TIEOUT", "NOT_EVALUATED", rc.measure, f"{t.id}: labelling could not be applied ({'; '.join(rc.gate_errors) or 'no usable rows'})",
                                     evidence=_recon_evidence(ctx, t, rc, []), reason_code="invalid_labelling", llm_inputs=["row-role labelling"]))
            continue
        bad = [c for c in to.columns if c.verdict != "PASS"]
        rows = []
        for c in bad:
            for s in c.segments:
                rows += [s.anchor_row, s.target_row] + ([s.diagnosis_row] if s.diagnosis_row else [])
        detail = "; ".join(f"{'/'.join(c.header_path)[-50:]}: {c.verdict} {c.reason_code or ''}" for c in bad[:3])
        n = len(to.columns)
        msg = f"{t.id} {to.orientation} reconciliation of '{rc.measure}': {n - len(bad)}/{n} {'line items' if to.orientation == 'horizontal' else 'period columns'} tie" + (f" ({detail})" if detail else "")
        ctx.findings.append(make("R-RECON-TIEOUT", to.verdict, rc.measure, msg, evidence=_recon_evidence(ctx, t, rc, rows),
                                 reason_code=next((c.reason_code for c in bad), None), llm_inputs=["row-role labelling"],
                                 provenance=to.provenance_warnings))


ALL = [r_recon_tieout, r_recon_present, r_recon_start_gaap, r_prom_headline, r_prom_order, r_prom_style, r_tax_separate, r_ebitda, r_pershare_liq]


def dedupe(findings: list[Finding]) -> list[Finding]:
    """Identical (rule, verdict, message) findings, e.g. one per repeated column group, become one with merged evidence."""
    out: dict[tuple, Finding] = {}
    for f in findings:
        k = (f.rule_id, f.verdict, re.sub(r"\bt\d\d\b", "t", f.message))
        if k in out:
            seen = {e.ref for e in out[k].evidence}
            out[k].evidence += [e for e in f.evidence if e.ref not in seen]
            out[k].lineage.provenance += [p for p in f.lineage.provenance if p not in out[k].lineage.provenance]
        else:
            out[k] = f
    return list(out.values())


def run_rules(doc: Document, inv: Inventory, labellings: list[TableLabelling]) -> list[Finding]:
    ctx = Ctx(doc, inv, labellings)
    for rule in ALL:
        rule(ctx)
    return dedupe(ctx.findings)
