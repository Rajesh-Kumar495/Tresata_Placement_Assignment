# Progress

## Stage status
| Stage | Status | Gate |
|---|---|---|
| 1. Research & problem ranking | ✅ Done (2026-11-01) | Human picked #2 (primary), #1 (secondary) |
| 2. Architecture & test plan — primary | ✅ **Approved 2026-11-02** with human amendments (ADR-014…019) | — |
| 3. Implementation + eval — primary | 🟡 In progress: steps 0–5 done (real corpus verified; inventory + labeller running on real files) | **Checkpoint now: human review of step-5 results + Q11** |
| 4. Brief (4 pages + appendix) | Not started | — |
| 5. Secondary target (#1 withholding) | Parked | Only if Stage 3–4 for #2 are submittable |

## Build order (architecture §16)
| Step | Item | Status |
|---|---|---|
| 0 | Tier A triage (18 letters) | ✅ 6 Tier A + 4 Tier B locked |
| 1 | Gold labels + validator; synthetic case specs | ✅ (anchors provisional until step 4) |
| 2 | Document model + numeric parser + tests | ✅ |
| 3 | Tie-out engine + unit/property tests | ✅ (68 tests passing; mutation-checked) |
| 4 | Corpus download → label anchor validation; model choice | ✅ 10/10 docs, 27/27 anchors; model chosen by human (ADR-024) |
| 5 | Measure inventory (lexicon + LLM + grounding) + HC1, plus row-role labeller on real files | ✅ 43/46 LLM-only, 46/46 surfaced; 191/193 tie-out PASS; **checkpoint: Q11 decision** |
| 6 | Deterministic rules + applicability/category resolver + rule-pack excerpts | — |
| 7 | LLM judges (k=1, escalation) | — |
| 8 | Static HTML report, manifest, replay | — |
| 9 | Full eval + failure write-up | — |
| 10 | Optional: recurrence enrichment | — |

## Log
- **2026-11-01** — Stage 1 research; human chose #2 primary, #1 secondary. Stage 2 design drafted.
- **2026-11-02** — Human review: 3 design changes + 7 open-question decisions → ADR-014…019; architecture and test plan v1.0 approved. Q1 legal basis verified in the Form 8-K PDF. 18 SEC letters triaged; corpus locked. Deterministic core built and tested. Tolerance spec refined during implementation (ADR-014 addendum, pending human review).
