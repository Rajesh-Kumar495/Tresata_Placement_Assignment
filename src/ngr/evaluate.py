"""Full evaluation harness (test_plan §2, §8): Tiers A/B (real, gold labels) + C/D (synthetic, pre-registered).

    python -I -m ngr.evaluate [--mode record|replay]

Writes runs/<run_id>/<case>/{report.html, review.json, hc2_dispositions.json},
eval/results/full_eval.json and eval/results/full_eval.md (numbers + every miss and false flag).
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from .config import PROJECT_ROOT
from .corpus import load_document
from .docmodel import Document, parse_html
from .findings import Finding
from .grounding import Grounder
from .inventory import names_match
from .labels import GoldLabel, load_labels
from .llm import LLMClient
from .report import write as write_report
from .review import Review, review
from .synthetic import build_cases

RESULTS = PROJECT_ROOT / "eval" / "results"
FAMILY = {"R-PROM-HEADLINE": "102.10(a)b2", "R-PROM-ORDER": "102.10(a)b2"}  # same C&DI clause, split by location (ADR-027)


def fam(rule: str) -> str:
    return FAMILY.get(rule, rule)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip().lower()


def locate(doc: Document, anchor: str | None):
    """ALL occurrences of the anchor (captions and footnotes repeat, e.g. Turtle Beach Table 5 '(continued)')."""
    if not anchor:
        return None
    g = Grounder(doc)
    q = re.sub(r"\s+", " ", anchor.translate(str.maketrans({"’": "'", "“": '"', "”": '"', "–": "-", "—": "-"}))).strip()
    locs, i = [], g.hay.find(q)
    while i >= 0:
        locs.append((g.ref_at(i) or "doc", i, i + len(q)))
        i = g.hay.find(q, i + 1)
    return locs or [("?", -1, -1)]


def matches(f: Finding, locs, anchor: str | None) -> bool:
    if locs is None:
        return True
    return any(_match_one(f, loc, anchor) for loc in locs)


def _match_one(f: Finding, loc, anchor: str | None) -> bool:
    ref, s, e = loc
    table = ref.split(".")[0] if re.match(r"t\d+\.r", ref) else None
    for ev in f.evidence:
        if ev.ref == ref:
            return True
        if ev.char_start is not None and ev.char_end is not None and ev.char_start < e and s < ev.char_end:
            return True
        if table and (ev.ref == table or ev.ref.startswith(table + ".")):
            return True
        if anchor and ev.quote and _norm(anchor)[:60] in _norm(ev.quote):
            return True
    return False


# ---------------------------------------------------------------- scoring: gold (Tier A/B)

def score_gold(label: GoldLabel, rv: Review, doc: Document) -> dict:
    nonpass = [f for f in rv.findings if f.verdict != "PASS"]
    used: set[int] = set()
    exp_rows = []
    for e in label.expected_findings:
        cands = [f for f in nonpass if fam(f.rule_id) == fam(e.rule_id)]
        if e.verdict == "NOT_EVALUATED":
            hit = [f for f in cands if f.verdict == "NOT_EVALUATED"]
            exp_rows.append({"rule": e.rule_id, "expected": "NOT_EVALUATED", "anchor": e.evidence_contains, "result": "hit" if hit else "miss",
                             "got": sorted({f.verdict for f in cands}) or ["PASS"]})
            used |= {id(f) for f in hit}
            continue
        loc = locate(doc, e.evidence_contains)
        local = [f for f in cands if matches(f, loc, e.evidence_contains) and f.verdict in ("FLAG", "NEEDS_REVIEW")]
        accept = {e.verdict, *e.also_accept}
        strict = [f for f in local if f.verdict in accept]
        if strict:
            res = "hit"
        elif local:
            res = "weak"  # NEEDS_REVIEW where FLAG expected: a human still sees it (test_plan §2), reported separately
        elif any(f.verdict in ("FLAG", "NEEDS_REVIEW") for f in cands):
            res = "offsite"  # same rule raised elsewhere in the document, but not at the SEC's location: NOT counted as a hit
        else:
            res = "miss"
        used |= {id(f) for f in local}
        exp_rows.append({"rule": e.rule_id, "expected": e.verdict, "anchor": e.evidence_contains, "result": res,
                         "got": sorted({f.verdict for f in local}), "sec": e.sec_comment, "elsewhere": sorted({f"{f.verdict}:{f.subject[:40]}" for f in cands if f not in local})[:3]})
    neg_rows = []
    for n in label.must_not_flag:
        loc = locate(doc, n.evidence_contains)
        # family equivalence only resolves WHERE a prominence issue sits; an anchorless negative names its exact rule
        same = (lambda r: fam(r) == fam(n.rule_id)) if n.evidence_contains else (lambda r: r == n.rule_id)
        viol = [f for f in rv.findings if same(f.rule_id) and f.verdict == "FLAG" and matches(f, loc, n.evidence_contains)]
        review_only = [f for f in rv.findings if same(f.rule_id) and f.verdict == "NEEDS_REVIEW" and matches(f, loc, n.evidence_contains)]
        neg_rows.append({"rule": n.rule_id, "anchor": n.evidence_contains, "violated": bool(viol), "needs_review": len(review_only),
                         "by": [f.message[:140] for f in viol[:2]]})
    unscored = set(label.unscored_rules) | set(label.sec_raised_ext)
    extras = [{"rule": f.rule_id, "verdict": f.verdict, "subject": f.subject, "message": f.message[:180]}
              for f in nonpass if id(f) not in used and f.verdict in ("FLAG", "NEEDS_REVIEW") and f.rule_id not in unscored
              and not any(n["violated"] and f.message[:140] in n["by"] for n in neg_rows)]
    return {"expected": exp_rows, "negatives": neg_rows, "extras": extras}


def score_inventory(label: GoldLabel, rv: Review) -> dict:
    gold = label.measures
    pred = rv.inventory.measures
    names = lambda m: [m.name, *m.aliases]
    recalled = [g.name for g in gold if any(names_match(g.name, n) for m in pred for n in names(m))]
    surfaced_pool = [n for m in pred for n in names(m)] + rv.inventory.unexplained_candidates
    surfaced = [g.name for g in gold if any(names_match(g.name, n) for n in surfaced_pool)]
    precise = [m.name for m in pred if any(names_match(g.name, n) for g in gold for n in names(m))]
    return {"gold": len(gold), "recalled": len(recalled), "surfaced": len(surfaced), "predicted": len(pred), "precise": len(precise),
            "missed": [g.name for g in gold if g.name not in recalled], "unmatched_predictions": [m.name for m in pred if m.name not in precise]}


# ---------------------------------------------------------------- scoring: synthetic (Tier C/D)

def score_case(case, rv: Review, doc: Document) -> dict:
    spec, checks = case.spec, []
    loc = locate(doc, case.anchor)
    for rule, want in (spec.get("expect") or {}).items():
        fs = [f for f in rv.findings if f.rule_id == rule]
        if want == "PASS":
            bad = [f for f in fs if f.verdict in ("FLAG", "NEEDS_REVIEW") and (loc is None or matches(f, loc, case.anchor))]
            checks.append((f"{rule}=PASS", "pass" if not bad else "fail", [f"{f.verdict}:{f.reason_code}" for f in bad][:3]))
        elif want == "FLAG":
            local = [f for f in fs if f.verdict in ("FLAG", "NEEDS_REVIEW") and (loc is None or matches(f, loc, case.anchor))]
            res = "pass" if any(f.verdict == "FLAG" for f in local) else "weak" if local else "fail"
            checks.append((f"{rule}=FLAG", res, [f"{f.verdict}:{f.reason_code}" for f in fs if f.verdict != "PASS"][:3]))
        else:  # NEEDS_REVIEW / NOT_EVALUATED
            ok = [f for f in fs if f.verdict == want and (not spec.get("reason") or f.reason_code == spec["reason"])]
            checks.append((f"{rule}={want}" + (f"({spec['reason']})" if spec.get("reason") else ""), "pass" if ok else "fail",
                           [f"{f.verdict}:{f.reason_code}" for f in fs if f.verdict != "PASS"][:3]))
    nf = spec.get("expect_no_flag")
    if nf == "all":
        bad = [f for f in rv.findings if f.verdict == "FLAG"]
        checks.append(("no FLAG at all", "pass" if not bad else "fail", [f"{f.rule_id}:{f.subject[:30]}" for f in bad][:4]))
    elif nf:
        for rule in nf:
            bad = [f for f in rv.findings if f.rule_id == rule and f.verdict == "FLAG" and (loc is None or matches(f, loc, case.anchor))]
            checks.append((f"no {rule} FLAG", "pass" if not bad else "fail", [f.message[:80] for f in bad][:2]))
    if spec.get("expect_inventory_empty"):
        checks.append(("inventory empty", "pass" if not rv.inventory.measures else "fail", [m.name for m in rv.inventory.measures][:4]))
    if case.id == "D01":
        leaked = [f.rule_id for f in rv.findings for e in f.evidence if "SYSTEM:" in (e.quote or "")]
        checks.append(("injected text never used as evidence", "pass" if not leaked else "fail", leaked[:3]))
    if case.id == "D04":
        bad_cols = sum(1 for lab in rv.labellings for rc in lab.reconciliations if rc.tieout for c in rc.tieout.columns if c.verdict != "PASS")
        checks.append(("exactly one period column non-PASS", "pass" if bad_cols == 1 else "fail", [f"{bad_cols} non-PASS columns"]))
    if case.id == "D05":
        found = any(names_match("cash earnings", n) for m in rv.inventory.measures for n in [m.name, *m.aliases]) or "cash earnings" in rv.inventory.unexplained_candidates
        checks.append(("'cash earnings' inventoried or surfaced", "pass" if found else "fail", []))
    worst = "fail" if any(c[1] == "fail" for c in checks) else "weak" if any(c[1] == "weak" for c in checks) else "pass"
    return {"case": case.id, "core": bool(spec.get("core", True)), "result": worst, "checks": checks}


def grounding_audit(rv: Review, doc: Document) -> tuple[int, int]:
    text = _norm(doc.text)
    n = bad = 0
    for f in rv.findings:
        for e in f.evidence:
            if not e.quote or re.fullmatch(r"t\d+", e.ref) or e.quote.startswith("table "):
                continue
            n += 1
            if _norm(e.quote) not in text:
                bad += 1
    return n, bad


# ---------------------------------------------------------------- main

def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    mode = argv[argv.index("--mode") + 1] if "--mode" in argv else "record"
    llm = LLMClient(mode=mode)  # type: ignore[arg-type]
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = PROJECT_ROOT / "runs" / run_id
    t0 = time.monotonic()
    labels = [l for l in load_labels() if not l.synthetic]

    def do_real(label):
        doc = load_document(label.doc_id)
        rv = review(label.doc_id, doc, llm)
        write_report(rv, doc, out / label.doc_id, label.source.company + " " + label.source.filed, llm.model)
        return label, doc, rv

    def do_case(case):
        doc = parse_html(case.html)
        rv = review(case.id, doc, llm, labelling_hook=case.labelling_hook)
        write_report(rv, doc, out / case.id, f"{case.id} (synthetic, base B01 Aviat 2025-05-06)", llm.model, synthetic=True)
        return case, doc, rv

    with ThreadPoolExecutor(max_workers=3) as pool:
        real = list(pool.map(do_real, labels))
        synth = list(pool.map(do_case, build_cases()))
    elapsed = time.monotonic() - t0

    res = {"run_id": run_id, "mode": mode, "model": llm.model, "elapsed_s": round(elapsed, 1), "docs": {}, "synthetic": []}
    for label, doc, rv in real:
        g = score_gold(label, rv, doc)
        g["inventory"] = score_inventory(label, rv)
        g["grounding"] = grounding_audit(rv, doc)
        g["tier"] = label.tier
        g["verdicts"] = dict(Counter(f"{f.rule_id}:{f.verdict}" for f in rv.findings))
        tie = Counter(c.verdict for lab in rv.labellings for rc in lab.reconciliations if rc.tieout for c in rc.tieout.columns)
        g["tieout"] = {"reconciliations": sum(len(l.reconciliations) for l in rv.labellings), "checks": dict(tie),
                       "inferred_sign": sum(1 for l in rv.labellings for rc in l.reconciliations if rc.tieout and rc.tieout.relies_on_inferred_sign)}
        res["docs"][label.doc_id] = g
    for case, doc, rv in synth:
        s = score_case(case, rv, doc)
        s["grounding"] = grounding_audit(rv, doc)
        res["synthetic"].append(s)
    calls = llm.calls
    res["llm"] = {"calls": len(calls), "cache_hits": sum(c.cache_hit for c in calls), "repairs": sum(c.repaired for c in calls),
                  "schema_failures": sum(not c.schema_valid for c in calls), "prompt_tokens": sum(c.prompt_tokens for c in calls),
                  "completion_tokens": sum(c.completion_tokens for c in calls),
                  "escalations": sum(1 for c in calls if ":escalate" in c.step)}
    all_f = [f for _, _, rv in real + synth for f in rv.findings]
    abst = defaultdict(lambda: Counter())
    for f in all_f:
        abst[f.rule_id][f.verdict] += 1
    res["verdicts_by_rule"] = {k: dict(v) for k, v in sorted(abst.items())}
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "full_eval.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    (RESULTS / "full_eval.md").write_text(render_md(res), encoding="utf-8")
    samples = RESULTS / "sample_reports"
    samples.mkdir(exist_ok=True)
    for d in ("A02-turtlebeach-2023-08-07", "A03-capri-2024-11-07", "M05"):
        if (out / d / "report.html").exists():
            shutil.copy(out / d / "report.html", samples / f"{d}.html")
    print(render_md(res))
    return 0


def render_md(r: dict) -> str:
    L = [f"# Full evaluation: run `{r['run_id']}`", "",
         f"Model `{r['model']}` · mode {r['mode']} · wall-clock {r['elapsed_s']} s · LLM calls {r['llm']['calls']} "
         f"(cache hits {r['llm']['cache_hits']}, escalations {r['llm']['escalations']}, repairs {r['llm']['repairs']}, schema failures {r['llm']['schema_failures']}) · "
         f"tokens {r['llm']['prompt_tokens']:,} in / {r['llm']['completion_tokens']:,} out", ""]
    # Tier A recall
    rows = [(d, e) for d, g in r["docs"].items() for e in g["expected"] if g["tier"] == "A"]
    scored = [e for _, e in rows if e["expected"] != "NOT_EVALUATED"]
    hit = sum(e["result"] == "hit" for e in scored)
    weak = sum(e["result"] == "weak" for e in scored)
    ne = [e for _, e in rows if e["expected"] == "NOT_EVALUATED"]
    off = sum(e["result"] == "offsite" for e in scored)
    L += ["## Tier A: SEC-raised issues (recall)", "",
          f"**{hit + weak}/{len(scored)} detected** ({hit} with the expected verdict, {weak} as NEEDS_REVIEW where FLAG was expected; "
          f"{off} 'offsite' = same rule raised elsewhere in the document but not at the SEC's location, NOT counted) · "
          f"pre-registered target ≥ 70% · NOT_EVALUATED expectations: {sum(e['result'] == 'hit' for e in ne)}/{len(ne)}", "",
          "| Doc | Rule | Expected | Result | Got | SEC comment |", "|---|---|---|---|---|---|"]
    for d, e in rows:
        L.append(f"| {d.split('-')[0]} {d.split('-')[1]} | {e['rule']} | {e['expected']} | **{e['result']}** | {', '.join(e['got']) or '-'} | {(e.get('sec') or '')[:70]} |")
    # negatives
    negs = [(d, n) for d, g in r["docs"].items() for n in g["negatives"]]
    viol = [(d, n) for d, n in negs if n["violated"]]
    L += ["", "## Must-not-flag checks (Tier A + B precision)", "",
          f"**{len(negs) - len(viol)}/{len(negs)} clean** (violations = FLAG where the gold says no issue)", ""]
    for d, n in viol:
        L.append(f"- VIOLATION {d} {n['rule']} @ {n['anchor']!r}: {n['by']}")
    nr = sum(n["needs_review"] for _, n in negs)
    if nr:
        L.append(f"- {nr} NEEDS_REVIEW finding(s) on must-not-flag rules (not violations; a reviewer looks)")
    # extras
    ex = [(d, x) for d, g in r["docs"].items() for x in g["extras"]]
    by_rule = Counter(x["rule"] for _, x in ex)
    L += ["", "## Unlabelled findings on real documents (need manual adjudication)", "",
          f"{len(ex)} FLAG/NEEDS_REVIEW findings not covered by any gold label: " + ", ".join(f"{k} {v}" for k, v in by_rule.most_common()), ""]
    for d, x in ex:
        L.append(f"- {d.split('-')[0]} {x['verdict']} {x['rule']}: {x['message'][:150]}")
    # inventory
    inv = {d: g["inventory"] for d, g in r["docs"].items()}
    G = sum(v["gold"] for v in inv.values())
    L += ["", "## Measure inventory (10 real releases)", "",
          f"Recall LLM-only **{sum(v['recalled'] for v in inv.values())}/{G}** · surfaced to HC1 **{sum(v['surfaced'] for v in inv.values())}/{G}** · "
          f"precision **{sum(v['precise'] for v in inv.values())}/{sum(v['predicted'] for v in inv.values())}** (predictions matching a gold measure)", ""]
    for d, v in inv.items():
        if v["missed"] or v["unmatched_predictions"]:
            L.append(f"- {d}: missed {v['missed']}; unmatched predictions {v['unmatched_predictions']}")
    # tie-out
    tc = Counter()
    for g in r["docs"].values():
        tc.update(g["tieout"]["checks"])
    L += ["", "## Tie-out on real releases", "",
          f"{sum(g['tieout']['reconciliations'] for g in r['docs'].values())} reconciliations · checks: " + ", ".join(f"{k} {v}" for k, v in tc.items())
          + f" · reconciliations relying on an LLM-inferred sign: {sum(g['tieout']['inferred_sign'] for g in r['docs'].values())}"]
    # synthetic
    syn = r["synthetic"]
    core = [s for s in syn if s["core"]]
    L += ["", "## Tier C/D: synthetic mutations and traps", "",
          f"**{sum(s['result'] == 'pass' for s in syn)}/{len(syn)} pass**, {sum(s['result'] == 'weak' for s in syn)} weak (NEEDS_REVIEW where FLAG expected), "
          f"{sum(s['result'] == 'fail' for s in syn)} fail · core set {sum(s['result'] == 'pass' for s in core)}/{len(core)}", "",
          "| Case | Core | Result | Checks |", "|---|---|---|---|"]
    for s in syn:
        L.append(f"| {s['case']} | {'✓' if s['core'] else ''} | **{s['result']}** | " + "; ".join(f"{c[0]} → {c[1]}" + (f" ({', '.join(map(str, c[2]))})" if c[1] != 'pass' and c[2] else '') for c in s["checks"]) + " |")
    # grounding
    gn = sum(g["grounding"][0] for g in r["docs"].values()) + sum(s["grounding"][0] for s in syn)
    gb = sum(g["grounding"][1] for g in r["docs"].values()) + sum(s["grounding"][1] for s in syn)
    L += ["", "## Grounding of final evidence", "", f"{gn - gb}/{gn} evidence quotes found verbatim in the source (target: 0 failures)", "",
          "## Verdicts by rule (all 30 documents)", "", "| Rule | PASS | FLAG | NEEDS_REVIEW | NOT_EVALUATED |", "|---|---|---|---|---|"]
    for k, v in r["verdicts_by_rule"].items():
        L.append(f"| {k} | {v.get('PASS', 0)} | {v.get('FLAG', 0)} | {v.get('NEEDS_REVIEW', 0)} | {v.get('NOT_EVALUATED', 0)} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main(sys.argv))
