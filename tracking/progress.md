# Progress

## Stage status
| Stage | Status | Gate |
|---|---|---|
| 1. Research & problem ranking | ✅ Done (2026-11-01) | Human picked #2 (primary), #1 (secondary) |
| 2. Architecture & test plan (primary) | ✅ Approved 2026-11-02 (ADR-014…019) | — |
| 3. Implementation + eval (primary) | ✅ Done 2026-11-03: system, HC1-gold run, single-call baseline, adjudication | — |
| 4. Brief (4 pages + appendix) | ✅ Drafted 2026-11-03 → docs/brief/brief.pdf | **Human: rewrite appendix 'What came from me' / 'stand behind' in own words; push; export logs (SUBMISSION_CHECKLIST.md)** |
| 5. Secondary target (#1 withholding) | Not built (by decision: time spent on evaluation quality) | — |

## Build order (architecture §16)
| Step | Item | Status |
|---|---|---|
| 0 | Tier A triage | ✅ 6 Tier A + 4 Tier B |
| 1 | Gold labels + validator; synthetic specs | ✅ incl. Tier B measure lists (Q12) |
| 2 | Document model + parser | ✅ |
| 3 | Tie-out engine | ✅ incl. Q11 unlabelled-flip diagnosis (ADR-026) |
| 4 | Corpus download + anchor validation; model | ✅ |
| 5 | Inventory + row-role labeller | ✅ |
| 6 | 9 deterministic rules + category resolver + verbatim rule excerpts | ✅ |
| 7 | 4 judge/hybrid rules (k=1, escalation) | ✅ |
| 8 | Static HTML/JSON memo, HC1/HC2 files, manifest, replay | ✅ (replay byte-identical) |
| 9 | Full evaluation (10 real + 20 synthetic) | ✅ Tier A 17/19, synthetic 20/20, must-not-flag 18/18, grounding 1209/1209 |
| 10 | Optional cross-period recurrence enrichment | ⏸ Not built (ADR-016/028) |

## Remaining work (estimate)
| Item | Why it matters | Effort |
|---|---|---|
| Manually adjudicate the 86 unlabelled findings on real releases | Real-document precision is currently unmeasured; alert volume is the main weakness | ~1.5 h |
| Single-LLM-call baseline on the same 30 documents | The strongest evidence that the architecture beats "just ask the model" | ~1 h |
| HC1-confirmed evaluation mode (inventory from gold) | Separates inventory errors from rule errors (test_plan §8) | ~0.5 h |
| CLI for HC1/HC2 dispositions (files exist; no command yet) | Completes the human-in-the-loop story | ~0.5 h |
| **4-page brief + 1-page AI appendix + architecture diagram** | The main graded deliverable | ~3–4 h |
| README polish, final replay check, export chat logs | Submission | ~0.5 h + human |
| Optional: recurrence enrichment; Stage 5 secondary target | Nice-to-have | skip unless time remains |

## Log
- **2026-11-01** — Stage 1 research; human chose #2. Stage 2 design drafted.
- **2026-11-02** — Human review → ADR-014…019; design approved. Triage, labels, parser, tie-out built.
- **2026-11-02** — Corpus downloaded and validated; inventory + labeller on real files; columnar tie-out, guards, provenance (ADR-021…025).
- **2026-11-02/03** — Q11 (ADR-026) and Q12 decided by the human; git committed. Rules, judges, report, synthetic cases and harness built. First full run: Tier A 14/19, synthetic 18/20. Ten general bugs fixed → 17/19, 20/20, 18/18 clean, 1209/1209 grounded (both runs reported in eval/results/README.md).
- **2026-11-03** — Human: "finish all the work". Added HC1-confirmed mode, reviewer CLI (review/hc1/hc2), single-call baseline (Tier A 9/19, must-not-flag 8/18, synthetic 8/19 vs system 17/19, 18/18, 20/20), AI adjudication of 83 unlabelled findings (precision 53% strict / 90% lenient; 3 more bugs fixed), brief (4 pp + appendix, PDF), README and submission checklist.
