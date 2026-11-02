# Open Questions

Items that need a human decision, or verification against a primary source.

## Closed (human review 2026-11-02)

| # | Question | Resolution |
|---|---|---|
| Q1 | Do Item 10(e)(1)(ii) prohibitions apply to furnished 8-K Item 2.02 releases? | **Closed → ADR-017.** Verified in the Form 8-K PDF: Instruction 2 to Item 2.02 applies only 10(e)(1)(i), and B.2 says Item 2.02 information is furnished, not filed. Reg G 100(a)/(b) applies regardless. Findings are categorised `REQUIREMENT` (Reg G 100(a), 10(e)(1)(i)) vs `STAFF_COMMENT_RISK` (Reg G 100(b) interpretations in C&DI 100.x; 10(e)(1)(ii)-based C&DIs). |
| Q2 | Verify C&DIs 104.x / 105.x. | **Closed.** Verbatim 104.02–105.07 retrieved (105.04 withdrawn). Relevant to us: 104.01–104.04 (segment measures, which are not non-GAAP only when ASC 280-conformant and inside the footnote), 104.06 (constant currency *is* non-GAAP; historical + constant-currency amounts plus a process description satisfies reconciliation), 105.06 (adjusted earnings for a completed period falls under Item 2.02). None of 105.x states whether 10(e)(1)(ii) applies to Item 2.02, which is consistent with ADR-017. 106.x out of scope. |
| Q3 | Review UI | **Closed → ADR-018.** Self-contained static HTML memo + CLI/JSON for HC1/HC2. No Streamlit. |
| Q4 | Which OpenRouter free model? | **Closed → ADR-019.** Bake-off on 2 sample tables during setup; `LLM_MODEL_ID` in `.env`. |
| Q5 | Are SEC letters valid labels for earnings releases? | **Closed.** All 18 letters triaged. 6 Tier A cases locked (each with ≥1 comment that targets an 8-K Ex 99.1 directly) and 4 Tier B post-fix releases identified. See test_plan.md §4. |
| Q6 | PDF/image support? | **Closed → ADR-011.** HTML only. Image/PDF tables → `NOT_EVALUATED`. A real instance exists: Adient's headline and highlights are JPG-only. |
| Q7 | EDGAR User-Agent | **Closed → ADR-019.** `SEC_EDGAR_USER_AGENT` from `.env`; `.env.example` has a placeholder; the fetcher refuses to run if it is unset. **The human must set it locally before the corpus download step.** |

## Open

| # | Question | Why it matters | Owner | Status |
|---|---|---|---|---|
| Q8 | Lumen's response letter (CORRESP 2023-04-25) returned HTTP 503. Did Lumen agree to revise? | Needed only to promote Lumen to a Tier B pair. Tier A labels don't depend on it. | Claude, retry later | Open |
| Q9 | Reg G Notes reference "(a)(1)(i)/(ii)" while the printed text has (a)(1)/(a)(2). Is the Cornell LII rendering current? | Citation precision in the rule pack. | Claude, check eCFR | Open |
| Q10 | Adient headline and highlights are images. Do we keep Adient in Tier A? | It is a natural real-world `NOT_EVALUATED` case for prominence, while its reconciliation issues remain scorable. | Proposed: keep | Proposed |
