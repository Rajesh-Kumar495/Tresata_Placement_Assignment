"""Review memo: self-contained static HTML (inline CSS, no network) + JSON (ADR-018).

Findings are grouped by verdict; every finding shows its rule, category, legal basis,
verbatim rule excerpt (collapsible), evidence linked to highlighted spans in the
rendered release, lineage and provenance warnings. HC1/HC2 stay file-based (CLI/JSON).
"""

from __future__ import annotations

import html
import json
from collections import Counter
from pathlib import Path

from .docmodel import Document
from .review import Review
from .rule_sources import load as load_excerpts

_ORDER = {"FLAG": 0, "NEEDS_REVIEW": 1, "NOT_EVALUATED": 2, "PASS": 3}
_CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a65;--line:#e4e1d8;--flag:#b42318;--rev:#b54708;--ne:#475467;--pass:#067647;--hl:#fff1a8;--card:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#161614;--fg:#ecebe6;--muted:#a3a29b;--line:#34332f;--flag:#f97066;--rev:#fdb022;--ne:#98a2b3;--pass:#47cd89;--hl:#5c4d00;--card:#1e1e1b}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
header{padding:20px 24px;border-bottom:1px solid var(--line)}h1{font-size:20px;margin:0 0 4px}h2{font-size:16px;margin:24px 0 8px}
.meta{color:var(--muted);font-size:12px;word-break:break-all}.wrap{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:0}
@media (max-width:900px){.wrap{grid-template-columns:1fr}}
.col{padding:16px 24px;min-width:0}.doc{border-left:1px solid var(--line);max-height:100vh;overflow:auto;position:sticky;top:0}
.chips span{display:inline-block;margin:0 8px 6px 0;padding:2px 10px;border-radius:999px;border:1px solid var(--line);font-size:12px}
.f{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--ne);border-radius:6px;padding:10px 12px;margin:8px 0}
.f.FLAG{border-left-color:var(--flag)}.f.NEEDS_REVIEW{border-left-color:var(--rev)}.f.PASS{border-left-color:var(--pass)}
.v{font-weight:600;font-size:12px}.FLAG .v{color:var(--flag)}.NEEDS_REVIEW .v{color:var(--rev)}.PASS .v{color:var(--pass)}.NOT_EVALUATED .v{color:var(--ne)}
.small{font-size:12px;color:var(--muted)}.ev a{color:inherit}.ev li{margin:2px 0}.prov{font-family:ui-monospace,Consolas,monospace;font-size:11px;white-space:pre-wrap;color:var(--rev)}
details summary{cursor:pointer;color:var(--muted);font-size:12px}blockquote{margin:6px 0;padding:6px 10px;border-left:3px solid var(--line);font-size:12px;color:var(--muted)}
.blk{padding:3px 6px;margin:1px 0;border-radius:3px}.blk.hl{background:var(--hl)}.k{color:var(--muted);font-size:10px;margin-right:6px}
table.t{border-collapse:collapse;font-size:11px;margin:6px 0;width:100%}table.t td{border-bottom:1px solid var(--line);padding:1px 4px;text-align:right}table.t td:first-child{text-align:left}
tr.hl td{background:var(--hl)}
"""


def _esc(s) -> str:
    return html.escape(str(s))


def render_html(rv: Review, doc: Document, title: str, model: str, synthetic: bool = False) -> str:
    ex = load_excerpts()
    hl = {e.ref for f in rv.findings if f.verdict != "PASS" for e in f.evidence}
    counts = Counter(f.verdict for f in rv.findings)
    cats = Counter(f.category for f in rv.findings if f.verdict in ("FLAG", "NEEDS_REVIEW"))
    parts = [f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Non-GAAP review memo</title><style>{_CSS}</style></head><body>"]
    parts.append(f"<header><h1>Non-GAAP review memo: {_esc(title)}</h1><div class=meta>"
                 f"{'<b>SYNTHETIC test document</b> · ' if synthetic else ''}input sha256 {rv.doc_sha256} · model {_esc(model)} · rule pack v1.0 · "
                 "Review aid only: not a compliance determination. Findings require reviewer disposition (HC2).</div>"
                 "<div class=chips style='margin-top:8px'>" + "".join(f"<span>{k}: {counts.get(k, 0)}</span>" for k in _ORDER) +
                 "".join(f"<span>{k}: {v}</span>" for k, v in cats.items()) + "</div></header>")
    parts.append("<div class=wrap><div class=col>")
    parts.append("<h2>HC1 · measure inventory (proposed)</h2><ul class=small>" + "".join(
        f"<li><b>{_esc(m.name)}</b>: {m.kind}{', per share' if m.per_share else ''}{', forward-looking' if m.forward_looking else ''}; GAAP comparable: {_esc(m.comparable_gaap)}</li>" for m in rv.inventory.measures) + "</ul>")
    if rv.inventory.unexplained_candidates:
        parts.append(f"<p class=small>Also review (lexicon hits not explained by the inventory): {_esc(', '.join(rv.inventory.unexplained_candidates))}</p>")
    parts.append("<h2>Findings</h2>")
    for f in sorted(rv.findings, key=lambda f: (_ORDER[f.verdict], f.rule_id)):
        evs = "".join(f"<li><a href='#{_esc(e.ref)}'>{_esc(e.ref)}</a>: “{_esc(e.quote[:220])}”</li>" for e in f.evidence[:5])
        excerpt = "".join(f"<blockquote><b>{_esc(k)}</b> {_esc(ex.get(k, '')[:1500])}</blockquote>" for k in f.excerpts)
        prov = "".join(f"<div class=prov>{_esc(p)}</div>" for p in f.lineage.provenance)
        parts.append(
            f"<div class='f {f.verdict}'><div><span class=v>{f.verdict}</span> · <b>{_esc(f.rule_id)}</b> · {_esc(f.category)} · severity {f.severity}"
            f"{' · ' + _esc(f.reason_code) if f.reason_code else ''}</div><div>{_esc(f.message)}</div>"
            f"<div class=small>Basis: {_esc('; '.join(f.citation))} · check: {f.lineage.check_type}"
            f"{' · LLM inputs: ' + _esc(', '.join(f.lineage.llm_inputs)) if f.lineage.llm_inputs else ''}"
            f"{' · confidence: ' + _esc(f.confidence) if f.confidence else ''} · HC1 confirmed: {f.lineage.hc1_confirmed}</div>"
            f"{prov}{'<ul class=ev>' + evs + '</ul>' if evs else ''}<details><summary>Rule text (verbatim)</summary>{excerpt}</details></div>")
    parts.append("</div><div class='col doc'><h2>Release (as parsed)</h2>")
    items = [(b.order, "b", b) for b in doc.blocks] + [(t.order, "t", t) for t in doc.tables]
    for _, kind, it in sorted(items, key=lambda x: x[0]):
        if kind == "b":
            parts.append(f"<div id='{it.id}' class='blk{' hl' if it.id in hl else ''}'><span class=k>{it.id} {it.kind}</span>{_esc(it.text)}</div>")
        else:
            rows = "".join(
                f"<tr id='{r.id}' class='{'hl' if r.id in hl else ''}'><td>{_esc(r.label)}</td>" + "".join(f"<td>{_esc(c.text)}</td>" for c in r.cells) + "</tr>"
                for r in it.rows if not r.is_header)
            parts.append(f"<div id='{it.id}' class='{'blk hl' if it.id in hl else 'blk'}'><span class=k>{it.id} table · scale {it.scale}</span><table class=t>{rows}</table></div>")
    parts.append("</div></div></body></html>")
    return "".join(parts)


def write(rv: Review, doc: Document, out_dir: Path, title: str, model: str, synthetic: bool = False) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.html").write_text(render_html(rv, doc, title, model, synthetic), encoding="utf-8")
    (out_dir / "review.json").write_text(rv.model_dump_json(indent=1), encoding="utf-8")
    hc2 = [{"rule_id": f.rule_id, "verdict": f.verdict, "subject": f.subject, "disposition": None, "reviewer_note": None}
           for f in rv.findings if f.verdict in ("FLAG", "NEEDS_REVIEW")]
    (out_dir / "hc2_dispositions.json").write_text(json.dumps({"status": "AWAITING REVIEWER", "findings": hc2}, indent=1), encoding="utf-8")
