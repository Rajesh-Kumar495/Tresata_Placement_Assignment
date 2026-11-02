# Architecture Decision Records

Format: Context → Decision → Consequences (pros / cons). Status moves to `Accepted` only on human sign-off.

---

### ADR-001 — Primary target: SEC non-GAAP earnings-release review; withholding is secondary
- **Status:** Accepted (human decision, 2026-11-01)
- **Context:** Stage 1 ranked treaty withholding (#1, 26/30) slightly above SEC non-GAAP (#2, 24/30).
- **Decision:** Build #2 fully first. Park #1 as a separate system ([secondary-target_withholding.md](secondary-target_withholding.md)).
- **Why:** The human's stated reason was that both problems are interesting; the human should record their own rationale. The AI's supporting observations: #2 has an external, regulator-written answer key (SEC comment letters), which de-risks the evaluation, and a lower domain ramp-up than Indian international tax mid-way through an Act transition.
- **Consequences:** We give up #1's statutory sign-off story and its "why now" (the Act renumbering). We gain objective recall labels. #2's deterministic core is thinner, so the architecture must push it as far as possible (ADR-004, ADR-005, ADR-012).

### ADR-002 — Fixed DAG workflow with bounded LLM steps, not an autonomous multi-agent system
- **Status:** Accepted (human sign-off 2026-11-02)
- **Context:** The brief asks whether one LLM call, retrieval, rules, calculators or "several cooperating agents" fit. The workflow here is known in advance: parse → inventory → reconcile → evaluate rules → report.
- **Decision:** A static DAG. Each LLM use is a typed function (schema in, schema out) with no tool loop and no self-directed planning.
- **Pros:** Reproducible; every step is unit-testable; easy to audit (a fixed set of calls per document); bounded cost; prompt-injection blast radius is small.
- **Cons:** Less flexible on unusual documents. A new kind of check needs code and rule-pack changes rather than "the agent figuring it out".
- **Why the cons are acceptable:** In a regulated review, "the agent figured it out" is not an auditable explanation. Flexibility is provided through the rule pack (ADR-003), which is governed.

### ADR-003 — Rules as a versioned YAML rule pack injected into prompts; no vector RAG
- **Status:** Accepted (human sign-off 2026-11-02)
- **Context:** The relevant corpus is small: about 25 C&DIs plus Item 10(e) and Reg G, roughly 60k characters.
- **Decision:** A curated rule pack. Each rule carries a verbatim excerpt, citation, URL, source date, effective dates, applicability and check type. Prompts get the exact rule text for the rule being judged.
- **Pros:** Zero retrieval misses; citation correct by construction; diffable by counsel; effective dating allows historical evaluation; supports staleness detection.
- **Cons:** Manual curation, and someone must own updates (HC3). Doesn't scale to thousands of rules unchanged.
- **Revisit when:** The rule corpus exceeds what fits in a scoped prompt, for example adding all SEC comment-letter precedents as "case law". Then add retrieval as an *evidence* source, never as the rule source.

### ADR-004 — Grounding gate: every LLM claim must carry a verbatim quote, verified by exact match
- **Status:** Accepted (human sign-off 2026-11-02)
- **Decision:** Exact substring match after normalising whitespace and Unicode. No fuzzy matching. Claims that fail are dropped and logged.
- **Pros:** Hallucinated evidence cannot reach the reviewer, and it gives a measurable metric.
- **Cons:** Some true claims are dropped when the model paraphrases. Raises the `NEEDS_REVIEW` rate.
- **Trade-off accepted:** In finance review, a missing citation is recoverable (a human looks); a fabricated one destroys trust in the tool.

### ADR-005 — The LLM never produces numbers used in computation; Decimal arithmetic in code
- **Status:** Accepted (human sign-off 2026-11-02)
- **Decision:** The LLM returns row and column IDs and roles only. Values come from the deterministic cell parser. The tie-out uses `Decimal` with a scale-aware rounding tolerance.
- **Pros:** Tie-out correctness depends only on parsing (testable) and not on the model.
- **Cons:** Parser quality becomes the bottleneck for messy HTML.

### ADR-006 — Human checkpoint HC1 at the measure inventory
- **Status:** Accepted (human sign-off 2026-11-02)
- **Decision:** A reviewer confirms the inventory (measures, kind, comparable GAAP measure) before any rule runs.
- **Why there and not only at the end:** It is the highest-leverage point. Every downstream check depends on the inventory, and errors there are silent (FMEA F1). It is cheap: 3–8 items, about 2 minutes.
- **Cons:** Adds a human wait in the workflow, which needs resumable orchestration in production. For unattended evaluation, HC1 is pre-filled from gold labels, and the no-HC1 score is reported separately.

### ADR-007 — Tri-state verdicts (+ NOT_EVALUATED), recall-biased routing, composed confidence
- **Status:** Accepted (human sign-off 2026-11-02). **Amended by ADR-015:** self-consistency is escalation-only, not default k=3.
- **Decision:** `PASS / FLAG / NEEDS_REVIEW / NOT_EVALUATED`. Confidence is composed from schema validity, grounding, self-consistency, lineage and HC1 status. The model's self-reported confidence is logged but not used.
- **Pros:** Honest uncertainty; abstention is visible and measured.
- **Cons:** Risk of over-abstaining. Mitigated by reporting the abstention rate next to recall.

### ADR-008 — Run manifest + record/replay of LLM responses
- **Status:** Accepted (human sign-off 2026-11-02)
- **Decision:** Pin and hash the inputs, rule pack, model, params and prompts; store raw responses. A `ReplayClient` makes reruns byte-identical.
- **Pros:** Auditability (an auditor can reproduce exactly what a reviewer saw); deterministic CI; graders can rerun without an API key.
- **Cons:** Storage of document text in logs inherits its confidentiality classification.

### ADR-009 — Applicability resolver by document type and effective date
- **Status:** Accepted (human sign-off 2026-11-02). **Amended by ADR-017:** the downgrade-to-`ADVISORY` idea is replaced by an explicit two-category taxonomy.
- **Context:** The C&DIs say the 10(e)(1)(i) prominence requirement applies to 8-K Item 2.02 earnings releases (102.10(a)). The text does not say the 10(e)(1)(ii) prohibitions do; 10(e)(1) refers to "a filing" (open question Q1).
- **Decision:** Rules declare `applies_to` and effective dates. The resolver can downgrade out-of-scope rules to `ADVISORY`, and the report lists the rules not applied and why.
- **Why this matters:** Treating every rule as universally applicable would generate legally wrong "violations". This was found by reading the primary text, not suggested up-front.

### ADR-010 — Provider-agnostic LLM interface with a data-classification policy (MNPI)
- **Status:** Accepted (human sign-off 2026-11-02)
- **Decision:** Inputs are tagged `public` or `confidential-mnpi`. MNPI inputs can be routed only to allow-listed providers (zero-retention, VPC or on-prem). The prototype uses public EDGAR filings only, on the OpenRouter free tier.
- **Why:** Draft earnings releases are material non-public information. A design that ignores this is unusable in practice regardless of accuracy.

### ADR-011 — HTML-only input for the prototype
- **Status:** Accepted (human sign-off 2026-11-02, Q6)
- **Decision:** EDGAR Ex 99.1 HTML only. PDF, images and charts return `NOT_EVALUATED`.
- **Pros:** Style and table structure are available directly, with no OCR error source.
- **Cons:** Excludes chart-prominence checks (102.10(a) bullet 6) and PDF drafts.

### ADR-012 — Deterministic cross-period evidence for "recurring" judgments
- **Status:** Accepted (human sign-off 2026-11-02). **Re-scoped by ADR-016:** optional enrichment, built after the core harness passes.
- **Decision:** When prior releases are supplied, match adjustment labels across quarters deterministically and give the recurrence evidence to the 100.01 judge.
- **Why:** "Recurring" (which 100.01 extends to "occasionally, including at irregular intervals") cannot be judged from one document. This turns an LLM guess into evidence-weighing.
- **Cons:** Needs N prior documents per case; label drift across quarters ("restructuring" vs "restructuring and other") needs normalisation.

### ADR-013 — Eval-first with pre-registered targets; four document tiers including mutation testing
- **Status:** Accepted (human sign-off 2026-11-02)
- **Decision:** Gold labels and target metrics are fixed before code. Tiers: A (SEC-flagged real), B (post-fix real), C (single-violation mutations), D (adversarial traps), plus E (component tests).
- **Why:** SEC letters give recall labels only (no letter ≠ compliant). Mutations give exact per-rule labels. Traps target the FMEA.
- **Cons:** Tiers C and D are synthetic and must be disclosed as such. Mutation realism depends on our edits.

---

## Stage 2 review amendments (human review, 2026-11-02)

### ADR-014 — Tie-out handles intermediate subtotals and sign polarity explicitly
- **Status:** Accepted (human-originated change, 2026-11-02)
- **Context:** The human reviewer flagged that `gaap_start + Σadj + tax == result` breaks on real tables in two ways: (1) intermediate subtotal rows get double counted if they are misclassified or summed; (2) subtracted items printed as positive numbers under labels like "Less: gain on sale". Triage then confirmed both in our own Tier A documents:
  - Turtle Beach 2023-08-07, Table 5: an "Operating income (loss)" subtotal mid-table, and a positive-printed "Other non-operating expense, net" that is subtracted.
  - Adient 2024-02-07: "Less: Adjusted Equity Income 25" is printed positive and subtracted.
  - Citi Trends 2025-06-03: interest income printed negative and subtracted.
  - Aviat 2025-02-04: positive add-backs in some blocks, parenthesised subtractions in others.
- **Decision:**
  1. The row-role labeller emits `role ∈ {gaap_start, adjustment, tax_effect, subtotal, nongaap_result, memo, other}`, plus `sign_hint ∈ {as_printed, subtract}`, where `subtract` means the label carries an explicit subtraction cue ("Less:", "Deduct:", "Minus", "Excluding"…).
  2. `subtotal` rows are **never** in the main sum. Each subtotal is checked as an **intermediate checkpoint**: the running sum since the previous anchor must equal the subtotal, and the subtotal then becomes the new anchor. A chain of segments must tie end to end.
  3. Sign resolution is deterministic. The effective value is `printed` unless `sign_hint=subtract` *and* the printed value is non-negative, in which case it is `−printed`. A **deterministic label lexicon** independently detects subtraction cues, and if it disagrees with the LLM's sign_hint, the disagreement is surfaced.
  4. **Polarity diagnosis, not polarity repair:** if a segment fails, the engine tests whether flipping exactly one cue-bearing row closes the diff within tolerance. If it does, the result is `NEEDS_REVIEW` with reason `sign_ambiguous` and names the row. It is never silently passed. Flips are restricted to cue-bearing rows so the search can't "explain away" a real error by finding some row whose sign change happens to fit.
- **Why not auto-accept the flip:** a flip that happens to close the gap could mask a genuine error of 2× that row's value. The reviewer sees the exact row and both sums.
- **Consequences:** More `NEEDS_REVIEW` on messy tables, but zero silent passes from sign games. New cases M13 (positive "Less:" row), M14 (intermediate subtotal) and D13 (misclassified subtotal).
- **Addendum (2026-11-02, found during implementation; AI-identified, pending human review): three-band tolerance.**
  - **Problem:** the v0.1 spec used one tolerance, `0.5 × unit × addends`. That is the *worst-case* rounding bound, so it grows with table length: with 6 adjustments it accepts a 3-unit error as PASS. That contradicts test M03 ("perturb → FLAG") and is a silent pass of a real error.
  - **Change:** `|diff| ≤ 1 unit` → PASS; `1 unit < |diff| ≤ worst-case bound` → `NEEDS_REVIEW (rounding_band)`; beyond the bound → FLAG (or a diagnosis). M03's spec now perturbs beyond the bound (≥ +10 units).
  - **Why:** in the band between "typical rounding" and "worst-case rounding", the engine honestly cannot tell rounding from error, so a human decides. Mutation-tested: a copy with the loose tolerance is caught by the property test.
  - **Also added:** the double-count diagnosis only fires if the removed row equals the running total before it, or its label looks like a subtotal. That is the same anti-masking restriction the human set for sign flips (test D14).

### ADR-015 — LLM judges: temperature 0, k=1 default; extra samples only on escalation
- **Status:** Accepted (human-originated change, 2026-11-02). Amends ADR-007.
- **Context:** k=3 across 19+ documents × ~4 judge rules would exhaust OpenRouter free-tier rate limits.
- **Decision:** `temperature=0`, k=1. Escalation means one schema-repair retry, then **at most 2 additional samples**, and only when a judge returns `UNCERTAIN` or fails schema validation or the grounding gate. If the escalated samples disagree, the verdict is `NEEDS_REVIEW` (confidence = agreement ratio).
- **Consequences:** Confidence on k=1 verdicts comes from schema, grounding, lineage and HC1, not agreement. Mitigation: the eval reports per-rule precision and recall, so an over-confident judge shows up as errors.

### ADR-016 — Cross-period recurrence diff is an optional enrichment, built last
- **Status:** Accepted (human-originated change, 2026-11-02). Re-scopes ADR-012.
- **Decision:** R-NORMAL-OPEX (C&DI 100.01) first runs on the single release, using the adjustment label, footnote description and C&DI text. The multi-quarter recurrence diff is added later as an enrichment pass on 1–2 Tier A cases, only after the main harness passes.
- **Why:** Fetching and parsing 4–8 prior releases per company is a schedule risk that doesn't block the core thesis.
- **Consequences:** Single-document 100.01 judgments are weaker. The eval reports 100.01 results with and without enrichment on the enriched cases, which quantifies the feature's value.

### ADR-017 — Finding category: `REQUIREMENT` vs `STAFF_COMMENT_RISK` (not a vague "advisory")
- **Status:** Accepted (human-originated change, 2026-11-02; legal basis verified 2026-11-02; closes Q1)
- **Verified basis:**
  - Form 8-K **Item 2.02, Instruction 2**: "The requirements of paragraph (e)(1)(i) of Item 10 of Regulation S-K … shall apply to disclosures under this Item 2.02" [VERIFIED: sec.gov/files/form8-k.pdf p.15].
  - **General Instruction B.2**: Item 2.02 information is not deemed "filed" for Section 18 purposes [VERIFIED: p.3].
  - **Reg G 244.100(a)/(b)** applies to any public disclosure of material information containing a non-GAAP measure [VERIFIED: Cornell LII].
  - **Item 10(e)(1)(ii)** prohibitions are framed as "in a filing", so they are not directly imposed on furnished releases. The staff nonetheless comments on them through Reg G 100(b) ("misleading") and the C&DIs (e.g. 102.05 says "filed or furnished"), and our 18-letter triage shows that in practice.
- **Decision:** Every finding carries:
  - `category: REQUIREMENT | STAFF_COMMENT_RISK`, plus `legal_basis[]` and an independent `severity`.
  - `REQUIREMENT` covers Reg G 100(a)(1)–(2) (GAAP comparable presented, reconciliation) and 10(e)(1)(i)(A)–(D) via Instruction 2 (prominence, reconciliation, usefulness and purpose statements).
  - `STAFF_COMMENT_RISK` covers Reg G 100(b) "misleading" interpretations (C&DI 100.01–100.06) and the 10(e)(1)(ii) / C&DI 102.05, 102.07, 102.11, 103.01, 103.02 positions.
  - Category is set by rule × document type in the rule pack. It is never inferred by the LLM.
- **Consequence:** The report tells counsel "required" vs "the SEC staff historically comments on this", which is the distinction they actually reason with.

### ADR-018 — Review UI: self-contained static HTML memo + CLI/JSON for HC1/HC2
- **Status:** Accepted (human decision, 2026-11-02; closes Q3)
- **Decision:** One HTML file with inline CSS and JS and no network calls, showing highlighted source spans. HC1 and HC2 are JSON files edited or produced through CLI commands. No Streamlit.

### ADR-019 — Configuration and secrets via environment (.env), nothing personal in git
- **Status:** Accepted (human decision, 2026-11-02; closes Q4 and Q7)
- **Decision:**
  - `OPENROUTER_API_KEY`, `LLM_MODEL_ID` and `SEC_EDGAR_USER_AGENT` come from the environment or `.env`.
  - `.env` is git-ignored; `.env.example` has placeholders.
  - EDGAR fetching refuses to run if `SEC_EDGAR_USER_AGENT` is unset. There is no default contact string.
  - The model is chosen by a bake-off on 2 sample tables during setup.

### ADR-020 — Gold-label anchors are validated against the downloaded bytes
- **Status:** Accepted (2026-11-02; AI-proposed, follows from ADR-004)
- **Context:** Tier A/B anchors were captured by reading EDGAR pages through a fetch tool. Some long-document tails (e.g. Lumen's) came back only as tool summaries.
- **Decision:** A label validator checks that every `evidence_contains` anchor occurs verbatim in the ingested document text. Labels whose anchors fail are `provisional` and excluded from scoring until fixed. The labels are held to the same grounding standard as the model.
