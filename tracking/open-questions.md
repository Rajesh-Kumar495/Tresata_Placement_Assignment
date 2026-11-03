# Open Questions

All questions are closed as of 2026-11-03. Each row records how it was resolved, or why it was deliberately not pursued.

| # | Question | Resolution |
|---|---|---|
| Q1 | Do Item 10(e)(1)(ii) prohibitions apply to furnished 8-K Item 2.02 releases? | **Closed → ADR-017.** Verified in the Form 8-K PDF: Instruction 2 to Item 2.02 applies only 10(e)(1)(i), and B.2 says Item 2.02 information is furnished, not filed. Reg G 100(a)/(b) applies regardless. Findings are categorised `REQUIREMENT` vs `STAFF_COMMENT_RISK` (human's framing). |
| Q2 | Verify C&DIs 104.x / 105.x | **Closed.** Verbatim 104.02–105.07 retrieved; 104.04 (segment totals) and 104.06 (constant currency) shaped R-RECON-PRESENT. 106.x out of scope. |
| Q3 | Review UI | **Closed → ADR-018** (human). Static self-contained HTML memo + CLI/JSON (`python -m ngr.cli review/hc1/hc2`). |
| Q4 | Which LLM model? | **Closed → ADR-024** (human). `deepseek/deepseek-v4.1-flash` via an OpenAI-compatible endpoint (`GOEDEL_*` in `.env`). 0 schema failures across the evaluation. |
| Q5 | Are SEC letters valid labels for earnings releases? | **Closed.** All 18 letters triaged; 6 Tier A + 4 Tier B locked. Letters are positive-only labels, so precision is measured separately (Tier B, must-not-flag, adjudication). |
| Q6 | PDF/image support? | **Closed → ADR-011** (human). HTML only; images → `NOT_EVALUATED`. Real instance: Adient's image-only headline. |
| Q7 | EDGAR User-Agent | **Closed → ADR-019** (human). `SEC_EDGAR_USER_AGENT` read from the git-ignored `.env`; nothing personal in git. |
| Q8 | Did Lumen agree to revise (its CORRESP returned HTTP 503)? | **Closed: not pursued.** Only needed to make Lumen a Tier B pair; 4 Tier B pairs already exceeded the human's minimum of 2. Lumen stays Tier A only. |
| Q9 | Reg G Notes cross-reference "(a)(1)(i)/(ii)" vs printed (a)(1)/(a)(2) | **Closed: not pursued.** No rule depends on the Notes; the rule pack cites Reg G 100(a)(1)/(a)(2) as printed. |
| Q10 | Keep Adient (image-only headline) in Tier A? | **Closed: kept.** It provides a real `NOT_EVALUATED` case (2/2 correct) while its reconciliation issues remain scorable. |
| Q11 | Turtle Beach unlabelled subtraction: FLAG or NEEDS_REVIEW? | **Closed → ADR-026** (human). A single-row 2× discrepancy on an unlabelled row → `NEEDS_REVIEW (possible_unlabelled_subtraction)` naming the row; never auto-PASS. |
| Q12 | Inventory precision unmeasured (no Tier B measure lists) | **Closed** (human). Gold measure lists added for B01–B04 from the documents themselves; final inventory precision 79/85 (73/73 with HC1). |
