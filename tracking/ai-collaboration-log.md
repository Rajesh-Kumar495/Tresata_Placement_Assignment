# AI Collaboration Log (source material for the brief's appendix)

The assignment asks for:
1. where AI helped, with key prompts;
2. what was rejected or corrected;
3. what came from me;
4. one thing I would defend without AI.

Sections 3–4 are the text used in the brief's appendix. The full conversation with the AI assistant (Claude) is in `Claude_chat_logs.zip` at the repository root.

## 1. Where AI helped
| Date | Stage | Use | Key prompt (my words, excerpt) |
|---|---|---|---|
| 2026-11-01 | 1 | Read the PDF; researched and ranked 5 candidate problems with public sources | "Research and propose 4 to 5 specific, niche problems… Rank them strictly by feasibility to build a demonstrable prototype within 48 hours… point me to the exact, publicly available open-source documents" |
| 2026-11-01 | 2 | Verified C&DI and Item 10(e) text; found SEC letters on EDGAR; drafted architecture, ADRs and test plan | "Think like a senior engineer building an industry-standard AI/agentic finance system… take an eval-first approach and map out our 10+ test cases (including the edge cases that might break it)" |
| 2026-11-02 | 3 | Triage of 18 SEC letters and company responses; parser, tie-out engine, gold labels; corpus download | "Start Stage 3 following your build order… starting with triaging the Tier A cases, writing the gold labels, and building the document model and tie-out engine with unit tests" |
| 2026-11-02 | 3 | Measure inventory and row-role labeller on real files | "Make sure that even if the LLM hints that the row has negative polarity and the math ties out, the tie-out result still logs a provenance warning" |
| 2026-11-03 | 3–4 | Rules, judges, memo, evaluation harness, baseline, adjudication, brief | "Proceed to Steps 5, 6, and 7… Pause and show me the full evaluation numbers and failure breakdown"; "Finish all the work" |

## 2. What was rejected or corrected (AI output that was wrong, generic or unsafe)
| Date | What the AI / sources said | Problem | Resolution |
|---|---|---|---|
| 2026-11-01 | Secondary blogs gave conflicting section numbers for the Income-tax Act 2025 (s.393 / 395 / 397) | Unverified, conflicting claims; dangerous to cite | Marked `[UNVERIFIED]`; primary text required before use |
| 2026-11-01 | A fetch tool's summary said C&DIs 100.x–103.x were "missing" from the page | Contradicted by the verbatim text it had retrieved | Disregarded the summary and used the verbatim text |
| 2026-11-01 | Default framing: "apply all non-GAAP rules to the earnings release" | Item 10(e)(1)(ii) refers to filings; furnished 8-Ks may differ | Applicability resolver (ADR-009), then ADR-017 |
| 2026-11-01 | "Agentic" framing invited a multi-agent design | Not auditable or reproducible for a known workflow | Fixed pipeline of typed LLM calls (ADR-002) |
| 2026-11-02 | AI's v0.1 tie-out spec: `gaap_start + Σadj + tax == result` | **I caught it:** intermediate subtotals get double counted, and "Less:" rows printed positive break a flat sum. Later confirmed in 4 of 6 real Tier A releases. | ADR-014 (segmented chain, polarity diagnosis) |
| 2026-11-02 | AI's v0.1: k=3 self-consistency for judges | **I rejected it:** would exhaust rate limits; use k=1 and escalate only on uncertainty or failure | ADR-015 |
| 2026-11-02 | AI's v0.1: multi-quarter recurrence inside the 100.01 check | **I deferred it:** schedule risk; make it optional, after the core harness | ADR-016 |
| 2026-11-02 | AI's v0.1: downgrade inapplicable rules to "ADVISORY" | **I rejected it:** too vague; split statutory requirement vs staff-comment risk. Then verified in Form 8-K Item 2.02 Instruction 2. | ADR-017 |
| 2026-11-02 | AI's v0.1 tolerance `0.5 × unit × addends` | Would auto-pass a 3-unit discrepancy on a 6-line table. I agreed with the three-band fix: the old tolerance was "way too loose for financial tie-outs". | ADR-014 addendum |
| 2026-11-02 | Fetch agent could not decode the Form 8-K PDF and declined to answer from memory | Correct behaviour, but it left Q1 unverified | Read the PDF pages directly; quoted Instruction 2 |
| 2026-11-02 | Triage agent described Turtle Beach Table 5 as a row-wise chain; a test fixture was built from that | **Wrong:** the downloaded bytes show a columnar table | Real-bytes tests added; columnar tie-out (ADR-021) |
| 2026-11-02 | Tolerance let Lumen non-GAAP EPS 0.51 "tie" to GAAP EPS 0.50 with no adjustments | False pass, found on real data | `no_adjustment_values` guard (ADR-023) |
| 2026-11-02 | **My requirement:** inferred signs must be visible in provenance even when the math ties | The AI design kept the sign source only in internal data | ADR-022 |
| 2026-11-02 | **My decision (Q11):** single-row 2× discrepancies on unlabelled rows → NEEDS_REVIEW with the row named; never auto-PASS; don't tune the prompt to Turtle Beach or feed the diff back to the LLM | The AI had left it as FLAG (alert fatigue) | ADR-026 |
| 2026-11-03 | First rule implementation trusted LLM "aliases" | The LLM lumped distinct measures as aliases, hiding an SEC-raised unreconciled measure (Aviat) | Alias consistency check |
| 2026-11-03 | First scorer matched only the first occurrence of a gold anchor | Under-counted detections on documents with repeated captions | All occurrences; mismatched locations reported as "offsite", not hits |
| 2026-11-03 | Forward-looking check treated a disclosure about Adjusted EBITDA as covering Adjusted EPS | False PASS, caught by planted case M11 | Specific-measure coverage + core-word matching |
| 2026-11-03 | Replay depended on the model id in `.env` | A fresh clone (no `.env`) could not replay | Cassettes record their model id; fresh-clone replay verified |
| 2026-11-03 | The assignment PDF had been committed to the repository | It is marked "Confidential & Proprietary" | Untracked and git-ignored going forward |

## 3. What came from me
- **Picking problem #2 over the AI's top-ranked #1**, and parking #1 as a separate system rather than mixing the two.
- **The working method:** eval-first, human checkpoints between stages, and this tracking folder, so the brief could be written from evidence.
- **The tie-out traps:** intermediate subtotals being double-counted, and subtractions printed as positive numbers without "Less:". Both were raised before any real data was seen and confirmed in 4 of 6 real SEC releases.
- **The unlabelled-subtraction policy (ADR-026):** a discrepancy of exactly 2× one unlabelled row goes to NEEDS_REVIEW with the row named, never auto-pass. A hard FLAG causes alert fatigue; passing hides ambiguity. Also: don't tune the prompt to the one document, and don't feed the arithmetic gap back to the LLM.
- **Requiring inferred signs to be disclosed** to an auditor even when the numbers tie (ADR-022).
- **The requirement vs staff-comment-risk split** instead of a vague "advisory" (ADR-017).
- **Escalation-only sampling** for rate-limit cost (ADR-015), and deferring the cross-quarter feature so the core pipeline shipped first (ADR-016).
- **Adding gold measure lists for the post-fix releases** so precision, not only recall, could be measured (Q12).
- **Keeping personal contact details and API keys out of the repository** (ADR-019).

## 4. One thing I'd stand behind without AI

**The reconciliation tie-out logic.** A reconciliation is a chain, not a sum:
- Subtotals are checkpoints, never added again.
- Every number comes from a parsed cell, never from the model.
- The result has three bands: within one unit of the last printed digit passes; up to the worst-case rounding bound (0.5 × unit × number of terms) goes to review, because rounding and error can't be told apart there; beyond that is flagged.
- When a gap is exactly explained by one row's sign or by a subtotal counted twice, the system names that row and sends it to a human. It never "fixes" the table into passing.

Worked real examples:
- Turtle Beach: 396 = 2 × 198.
- Adient: a "Less:" row printed as a positive number.
- Lumen: GAAP EPS 0.50 vs non-GAAP 0.51 with nothing reconciled.
