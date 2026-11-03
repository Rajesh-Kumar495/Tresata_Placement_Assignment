# Progress

**Project status: COMPLETE (2026-11-03).** Final deliverable: [`Tresata_Brief.pdf`](../Tresata_Brief.pdf) (4 pages + 1-page appendix), plus the prototype, evaluation and this tracking record in the repository.

## Stage status
| Stage | Status | Outcome |
|---|---|---|
| 1. Research & problem ranking | ✅ Done 2026-11-01 | 5 problems ranked; human picked #2 (SEC non-GAAP review) as primary, #1 (India treaty withholding) parked |
| 2. Architecture & test plan | ✅ Done 2026-11-02 | Approved with amendments (ADR-014…019); eval-first test plan with pre-registered targets |
| 3. Implementation + evaluation | ✅ Done 2026-11-03 | Full pipeline; 10 real + 20 synthetic cases; HC1-confirmed run; single-call baseline; adjudication |
| 4. Brief (4 pages + appendix) | ✅ Done 2026-11-03 | `Tresata_Brief.pdf` at the repository root |
| 5. Secondary target (#1 withholding) | ⏹ Not built (deliberate) | Time went into evaluation quality instead; see `secondary-target_withholding.md` |

## Build order (architecture §16): all steps
| Step | Item | Status |
|---|---|---|
| 0 | Tier A triage of 18 SEC letters | ✅ 6 Tier A + 4 Tier B locked |
| 1 | Gold labels + validator; synthetic specs | ✅ 27/27 anchors validated; Tier B measure lists (Q12) |
| 2 | Document model + parser | ✅ |
| 3 | Tie-out engine | ✅ segmented chain, three-band tolerance, columnar tables, Q11 diagnosis (ADR-026) |
| 4 | Corpus download + anchor validation; model choice | ✅ 10 releases, sha256-pinned; deepseek-v4.1-flash (ADR-024) |
| 5 | Measure inventory + row-role labeller | ✅ |
| 6 | 9 deterministic rules + category resolver + verbatim rule excerpts | ✅ |
| 7 | 4 judge/hybrid rules (temperature 0, k=1, escalation-only) | ✅ |
| 8 | HTML/JSON memo, HC1/HC2 reviewer CLI, manifest, offline replay | ✅ fresh clone replays byte-identically |
| 9 | Full evaluation + HC1-gold run + baseline + adjudication | ✅ see results below |
| 10 | Optional cross-quarter recurrence enrichment | ⏹ Not built (ADR-016/028); listed as next step in the brief |

## Final results
| Metric | Target | System | Single-call baseline |
|---|---|---|---|
| SEC-raised issues detected (Tier A) | ≥ 70% | **17/19** | 9/19 |
| Known-clean items not flagged | 0 violations | **18/18** | 8/18 |
| Synthetic violations / traps | ≥ 90% | **20/20** | 8/19 |
| Evidence quotes verbatim | 0 failures | **1183/1183** | 330/333 |
| Inventory recall / precision | ≥ 90% recall | 73/73 · 79/85 | — |
| Precision on 100 real-release findings | — | 53% strict · 90% lenient (AI-adjudicated) | — |

## Log
- **2026-11-01** — Stage 1 research; human chose #2. Stage 2 design drafted.
- **2026-11-02** — Human review → ADR-014…019; design approved. Triage, gold labels, parser, tie-out built.
- **2026-11-02** — Corpus downloaded and validated; inventory + labeller on real files; columnar tie-out, guards, provenance (ADR-021…025).
- **2026-11-02/03** — Human decided Q11 (ADR-026) and Q12; git set up. Rules, judges, memo, synthetic cases and harness built. First full run: Tier A 14/19, synthetic 18/20. Ten general bugs fixed; both runs reported in `eval/results/README.md`.
- **2026-11-03** — HC1-confirmed mode, reviewer CLI, single-call baseline, AI adjudication of 83 unlabelled findings (3 more bugs fixed), brief, README. Fresh-clone replay verified (fixed a replay bug: cassettes now record their model id).
- **2026-11-03** — Final packaging: brief moved to the repository root; local working files untracked; confidential assignment PDF untracked; tracking records closed out.
