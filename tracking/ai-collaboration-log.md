# AI Collaboration Log (source material for the brief's appendix)

The assignment asks for:
1. where AI helped, with key prompts;
2. what was rejected or corrected;
3. what came from the human;
4. one thing the human would defend without AI.

Sections 1–2 are filled in as we go. **Sections 3–4 must be written by the human.** The AI should not author claims about what the human contributed.

## 1. Where AI helped
| Date | Stage | Use | Key prompt (excerpt) |
|---|---|---|---|
| 2026-11-01 | 1 | Read the PDF; researched and ranked 5 candidate problems with public sources | "Research and propose 4 to 5 specific, niche problems… Rank them strictly by feasibility to build a demonstrable prototype within 48 hours… point me to the exact, publicly available open-source documents" |
| 2026-11-01 | 2 | Verified C&DI and Item 10(e) text; found SEC letters on EDGAR; drafted architecture, ADRs and test plan | "Think like a senior engineer building an industry-standard AI/agentic finance system… take an eval-first approach and map out our 10+ test cases (including the edge cases that might break it)" |

## 2. What was rejected or corrected (AI output that was wrong, generic or unsafe)
| Date | What the AI / sources said | Problem | Resolution |
|---|---|---|---|
| 2026-11-01 | Secondary blogs gave conflicting section numbers for the Income-tax Act 2025 (s.393 / 395 / 397) | Unverified, conflicting claims; dangerous to cite | Marked `[UNVERIFIED]`; primary text required before use |
| 2026-11-01 | A fetch tool's summary said C&DIs 100.x–103.x were "missing" from the page | Contradicted by the verbatim text it had retrieved | Disregarded the summary and used the verbatim text; 104.03+ marked unverified |
| 2026-11-01 | Default framing: "apply all non-GAAP rules to the earnings release" | Item 10(e)(1)(ii) refers to filings; furnished 8-Ks may differ | Applicability resolver (ADR-009); open question Q1 |
| 2026-11-01 | "Agentic" framing in the brief invited a multi-agent design | Not auditable or reproducible for a known workflow | Fixed DAG (ADR-002), with the reasoning recorded |
| 2026-11-02 | AI's v0.1 tie-out spec: `gaap_start + Σadj + tax == result` | **Human caught it:** intermediate subtotals get double counted, and "Less:" rows printed positive break a flat sum. Later confirmed in 4 of our 6 real Tier A releases. | ADR-014 (segmented chain, polarity diagnosis) |
| 2026-11-02 | AI's v0.1: k=3 self-consistency for judges in evaluation | **Human:** this would exhaust free-tier rate limits; use k=1 and escalate only on uncertainty or failure | ADR-015 |
| 2026-11-02 | AI's v0.1: multi-quarter recurrence as part of the 100.01 check | **Human:** schedule risk; make it an optional enrichment after the core harness passes | ADR-016 |
| 2026-11-02 | AI's v0.1: downgrade inapplicable rules to "ADVISORY" | **Human:** too vague; split statutory requirement vs staff-comment risk. Verified against the Form 8-K Item 2.02 Instruction 2. | ADR-017 |
| 2026-11-02 | AI's own v0.1 tolerance `0.5×unit×addends` | **AI found during implementation:** the worst-case bound grows with table length and would silently pass a 3-unit error | Three-band tolerance (ADR-014 addendum), pending human review |
| 2026-11-02 | Fetch agent could not decode the Form 8-K PDF and declined to answer from memory | Correct behaviour, but it left Q1 unverified | Read the saved PDF pages directly; quoted Instruction 2 |
| 2026-11-02 | Triage agent described Turtle Beach Table 5 as a row-wise chain; I built a fixture from that description | **Wrong:** the downloaded bytes show a columnar table. Caught by running on real files. | Fixture relabelled synthetic; real-bytes tests added; ADR-021 |
| 2026-11-02 | AI's tolerance alone let Lumen non-GAAP EPS 0.51 "tie" to GAAP EPS 0.50 with no adjustments | False pass, found on real data | `no_adjustment_values` guard (ADR-023) |
| 2026-11-02 | **Human requirement:** inferred signs must be visible in provenance even when the math ties | AI design surfaced sign source only in the term data, not as an auditor-facing message | ADR-022 |
| _human to add_ | | | |

## 3. What came from the human  ← **human to write**
- Decision to pick #2 over the AI's top-ranked #1, and the reasoning: _…_
- _…_

## 4. One thing I'd stand behind without AI  ← **human to write**
_…_
