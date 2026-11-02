# Progress

## Stage status
| Stage | Status | Gate |
|---|---|---|
| 1. Research & problem ranking | ✅ Done (2026-11-01) | Human picked #2 (primary), #1 (secondary) |
| 2. Architecture & test plan — primary | ✅ **Approved 2026-11-02** with human amendments (ADR-014…019) | — |
| 3. Implementation + eval — primary | 🟡 In progress: steps 0–3 done (triage, labels, document model, tie-out) | **Checkpoint now: human review of triage, labels, tie-out engine** |
| 4. Brief (4 pages + appendix) | Not started | — |
| 5. Secondary target (#1 withholding) | Parked | Only if Stage 3–4 for #2 are submittable |

## Build order (architecture §16)
| Step | Item | Status |
|---|---|---|
| 0 | Tier A triage (18 letters) | ✅ 6 Tier A + 4 Tier B locked |
| 1 | Gold labels + validator; synthetic case specs | ✅ (anchors provisional until step 4) |
| 2 | Document model + numeric parser + tests | ✅ |
| 3 | Tie-out engine + unit/property tests | ✅ (68 tests passing; mutation-checked) |
| 4 | Corpus download → label anchor validation; model bake-off | ⛔ **Needs `SEC_EDGAR_USER_AGENT` in .env** (and an OpenRouter key for the bake-off) |
| 5 | Measure inventory (lexicon + LLM + grounding) + HC1 | — |
| 6 | Deterministic rules + applicability/category resolver + rule-pack excerpts | — |
| 7 | LLM judges (k=1, escalation) | — |
| 8 | Static HTML report, manifest, replay | — |
| 9 | Full eval + failure write-up | — |
| 10 | Optional: recurrence enrichment | — |

## Log
- **2026-11-01** — Stage 1 research; human chose #2 primary, #1 secondary. Stage 2 design drafted.
- **2026-11-02** — Human review: 3 design changes + 7 open-question decisions → ADR-014…019; architecture and test plan v1.0 approved. Q1 legal basis verified in the Form 8-K PDF. 18 SEC letters triaged; corpus locked. Deterministic core built and tested. Tolerance spec refined during implementation (ADR-014 addendum, pending human review).
