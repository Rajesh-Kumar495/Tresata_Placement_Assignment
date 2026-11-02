# Phase 2 Log — Architecture & Test Plan (Primary: SEC Non-GAAP)

## 2026-11-01 — Session 1

**Human instruction (summary):** Lock #2 as primary and #1 as secondary. Create a tracking folder. Design for industry standards (reliable, scalable, secure, adaptable, auditable), with a clear LLM-vs-deterministic split, source traceability and HITL. Eval-first: map 10+ test cases including breaking edge cases. No code until sign-off.

**Research done this session:**
- Fetched the SEC Non-GAAP C&DI page (last update 2022-12-13). Verbatim text retrieved through 104.01. 104.03+ was summary-only and is unverified (open question Q2).
- Fetched 17 CFR 229.10 (Item 10(e)) from Cornell LII: confirmed the (e)(1)(i)(A)–(D) and (e)(1)(ii)(A)–(E) structure.
- Queried the EDGAR full-text search: 18 SEC staff letters (UPLOAD), 2023–2025, matching "equal or greater prominence" + "earnings release". Recorded in test_plan §4, not yet triaged.

**Findings that changed the design:**
1. **Applicability nuance.** 102.10(a) explicitly applies the prominence requirement to furnished Item 2.02 earnings releases. The (e)(1)(ii) prohibitions are framed around "a filing". Result: added the applicability resolver (ADR-009) and open question Q1. Without this, the tool would emit legally overstated "violations".
2. **100.01 (Dec 2022) defines recurring as "repeatedly or occasionally, including at irregular intervals".** A single document can't establish that, so we added cross-period evidence (ADR-012).
3. **SEC letters are positive-only labels.** Hence the four-tier eval with mutation testing (ADR-013).
4. **Draft releases are MNPI.** This drove the data-classification routing policy (ADR-010).

**Artefacts produced:**
- docs/design/architecture.md (v0.1)
- docs/design/test_plan.md (v0.1)
- tracking/decisions.md (ADR-001…013)
- tracking/rejected-alternatives.md
- tracking/open-questions.md (Q1–Q7)

**Awaiting:** human review and challenge. Open questions Q1, Q3, Q6 and Q7 need human input.
