# Stage 1 — Problem Research & Feasibility Ranking

**Status:** Draft for human review. No architecture locked, no code written.
**Date:** 2026-11-01
**Excluded on purpose (per the assignment PDF):** regulator-circular impact tracking for banks; FTA rules-of-origin for exporters.

---

## 0. What the assignment actually rewards (from the PDF)

Reading the brief closely, the grading weight is on:

1. **One narrow problem** with a clear who / what / how often / what it costs today, plus explicit out-of-scope.
2. **Architecture reasoning** — specifically the split between *exact & auditable* parts (a tax amount, a cited clause) and *probabilistic* parts, traceability to source, where knowledge lives and **what happens when it goes stale**, the weakest point, and rejected alternatives.
3. **"Why AI and not a simpler non-AI approach"** — this is a trap for problems that are really just lookups. A good problem must have a genuinely unstructured, judgment-heavy step.
4. **Prototype is optional** but 10+ test cases with honest failure reporting is a strong signal.
5. **Legal/advice liability** must be part of the design (who signs, where a qualified human is required by law).

So the ranking criteria below are not just "can we build it in 48h" but "can we build it in 48h **and** defend every one of those six questions."

### Ranking criteria (each scored 1–5, higher = better for us)

| Criterion | Why it matters for this assignment |
|---|---|
| **Ground truth** | Can we score 10 test cases objectively, ideally against an answer someone else (a regulator, a table) wrote? |
| **Deterministic core** | Is there real math / rule logic to separate from the LLM? (The architecture story depends on it.) |
| **AI necessity** | Is there a step a regex/lookup genuinely can't do? Otherwise "why AI" collapses. |
| **Doc tractability** | Size/complexity of source docs we must parse in 48h. |
| **Domain ramp-up** | How fast can we learn enough to not say something wrong in the brief? |
| **Built-in HITL story** | Does the law already name a qualified human who signs? (Makes liability section easy and honest.) |

---

## 1. Ranked shortlist (summary)

| Rank | Problem | Jurisdiction | Ground truth | Det. core | AI need | Docs | Ramp-up | HITL | **Total /30** |
|---|---|---|---|---|---|---|---|---|---|
| **1** | Treaty withholding-rate determination for outbound cross-border payments (CA certificate, Form 146 / ex-15CB) | India (alt: US W-8BEN-E) | 4 | 5 | 5 | 4 | 3 | 5 | **26** |
| **2** | Non-GAAP earnings-release pre-filing compliance check (Reg G / Item 10(e)) | US (SEC) | 5 | 3 | 5 | 4 | 4 | 3 | **24** |
| **3** | Lease abstraction + ASC 842 lease classification | US GAAP (alt: IFRS 16) | 3 | 5 | 4 | 3 | 4 | 3 | **22** |
| **4** | OFAC 50% Rule — aggregate indirect ownership by blocked persons | US (OFAC) | 2 | 5 | 3 | 4 | 4 | 3 | **21** |
| **5** | Debt covenant compliance computation from credit agreements | US (EDGAR filings) | 3 | 5 | 4 | 2 | 3 | 3 | **20** |

Scores are my judgment, not measured. Section 3 lists the assumptions most likely to be wrong.

---

## 2. Problem detail

### #1 — Treaty withholding rate on outbound cross-border payments (India, CA certificate)

**Who / what / how often.** When an Indian company pays a non-resident (software licence, technical services, interest, dividends, royalty), it must withhold tax at the correct rate. Above the ₹5 lakh threshold, a Chartered Accountant must issue a certificate (historically **Form 15CB**, now **Form 146** for remittances from 1 April 2026) stating: the nature of the payment, the domestic-law section, the applicable DTAA article, the treaty rate, and why treaty benefit applies. Banks will not release the remittance without it. Mid-size CA firms do this for many clients every month.

**The manual cross-referencing today.** For *each* payment the CA reads the invoice/agreement and decides:
1. **Characterisation** — is this "royalty", "fees for technical services (FTS)", or "business profits" (not taxable without a PE)? This is the expensive judgment step, and it differs *by treaty*: e.g. India–US and India–UK FTS articles have a **"make available"** condition; many other treaties do not.
2. **Domestic rate** — Act rate + surcharge + cess.
3. **Treaty rate** — from the specific DTAA article (and protocol).
4. **MFN clauses** — some treaties (Netherlands, France, Switzerland) promise lower rates granted to later OECD treaty partners. After the **Supreme Court's *Nestlé SA* ruling (19 Oct 2023)** these only apply if separately notified by the government — a classic "rule changed, old spreadsheets now wrong" trap.
5. **Conditions** — Tax Residency Certificate, Form 10F (now renumbered), beneficial ownership, no PE in India.
6. **Rate applied = more beneficial of Act vs treaty** (old s.90(2)).

**Why now.** The **Income-tax Act, 2025 replaced the 1961 Act from 1 April 2026**, renumbering sections and forms (15CA→145, 15CB→146). Every template, checklist and precedent memo a CA firm uses now cites dead section numbers. This is a *live* "knowledge went stale" event — exactly the risk the PDF asks about — and we can demonstrate the system handling it.

**Why AI (and not just a lookup table).** Steps 2, 3, 6 are pure lookup + math (deterministic). Step 1 (characterising a free-text invoice / agreement clause as royalty vs FTS vs business profits, and testing "make available") is semantic judgment that tax tribunals argue about. That is the *only* place the LLM belongs, and its output must cite the treaty clause it relied on.

**Natural LLM / deterministic split (preview, not a locked design).**
- LLM: classify payment nature from the document → candidate treaty article + quoted supporting clause + confidence.
- Deterministic: rate table lookup, surcharge/cess math, "lower of" rule, condition checklist (TRC/10F present?), MFN only if a notification ID exists in the knowledge base.
- Human: CA signs Form 146 — the law already requires it. Clean liability story.

**Public sources to pull today.**
| Source | What we use it for | Verified? |
|---|---|---|
| Income Tax Dept DTAA index — `https://incometaxindia.gov.in/pages/international-taxation/dtaa.aspx` | Full treaty texts (India–USA, India–UK, India–Netherlands, India–Singapore, India–Mauritius) incl. protocols | Index URL confirmed via secondary sources; individual PDF links to pull manually |
| Income-tax Act, 2025 + Income-tax Rules, 2026 (bare text on incometaxindia.gov.in) | New section numbers for withholding on non-residents and Form 145/146 rule | **Must verify** — secondary blogs disagree (s.393 vs s.395 vs s.397) |
| Form 15CA/CB → 145/146 mapping — e.g. [Taxscan old-vs-new forms mapping](https://www.taxscan.in/top-stories/income-tax-act-2025-forms-full-old-vs-new-comparison-mapping-guide-1445284), [ClearTax Form 145](https://cleartax.in/s/form-145-income-tax) | Old→new crosswalk (secondary; confirm against notification) | Found |
| *AO v. Nestlé SA*, SC, Civil Appeal 1420/2023 — summaries: [Taxmann](https://www.taxmann.com/post/blog/dtaa-mfn-analysis-of-supreme-courts-judgment-in-nestle-sa/), [ELP alert](https://elplaw.in/wp-content/uploads/2023/09/ELP-Tax-Alert-SC-ruling-on-MFN-clause-.pdf) | MFN rule for the engine + a "trap" test case | Found |
| ITAT rulings on "make available" (e.g. via indiankanoon.org) | Realistic characterisation edge cases | To pull |

**US alternative (same problem shape, cleaner ground truth).** US withholding agents validate treaty claims on **Form W-8BEN-E**. IRS publishes **[Tax Treaty Table 1](https://www.irs.gov/pub/irs-lbi/tax-treaty-table-1.pdf)** (rates by country × Form 1042-S income code, with article citations) — an official answer key. Weaker on "why AI" because inputs are more structured. Worth keeping as fallback or as the deterministic rate source to compare against.

**10+ test cases we can construct (synthetic invoices/agreements, real treaty clauses):**
1. US SaaS subscription (no source code transfer) → business profits vs royalty
2. US consulting with training that transfers know-how → FTS "make available" satisfied
3. US consulting without knowledge transfer → "make available" fails → not FTS
4. Same consulting service from a Germany vendor (no make-available clause) → FTS
5. Netherlands dividend claiming MFN reduction → post-*Nestlé*: denied absent notification
6. Singapore interest payment, TRC present → treaty rate
7. Same, TRC missing → falls back to domestic rate
8. Payee with no PAN → higher domestic-rate rule interacting with treaty
9. Mixed contract (licence + support) → must split, flag for human
10. Invoice citing old 1961 Act section → system flags stale citation
11. Payment to a non-treaty country → domestic rate only
12. Ambiguous description ("services") → low confidence → must route to CA, not guess

**Risks to this pick.** Highest domain ramp-up of the five (Indian international tax is deep). New-Act section numbers are still being reported inconsistently by secondary sources — we must cite primary text only. No "official answer key" for characterisation; our labels are our own reading of treaty text + tribunal rulings, which must be stated in the brief.

---

### #2 — Non-GAAP earnings-release pre-filing compliance check (US SEC)

**Who / what / how often.** Every quarter, SEC-reporting companies publish earnings releases (8-K Exhibit 99.1) containing non-GAAP measures (Adjusted EBITDA, adjusted EPS, free cash flow). SEC reporting teams, outside counsel and auditors check each release against **Regulation G, Item 10(e) of Reg S-K and the staff's Non-GAAP C&DIs**. Non-GAAP is consistently among the **top SEC comment-letter topics** (Deloitte's Nov 2025 roadmap still lists it in the top areas).

**Manual cross-referencing today.** Reviewer reads the release and checks: is every non-GAAP measure reconciled to the most comparable GAAP measure? Is GAAP presented with **equal or greater prominence** (C&DI 102.10 — headlines, quotes, ordering, bullet lists)? Are adjustments excluding **normal, recurring cash operating expenses** (C&DI 100.01)? Is a liquidity measure presented per share? Does the reconciliation actually add up?

**Why this ranks high: a regulator-written answer key.** The SEC publicly releases its comment letters (EDGAR form types **UPLOAD** = SEC letter, **CORRESP** = company response). We can pull 10+ real earnings releases that the SEC *actually flagged* and the exact comment text — objective, external ground truth. Few problems offer that.

**Why AI.** "Prominence" and "normal recurring operating expense" are semantic judgments over prose and layout. Deterministic part: the reconciliation arithmetic (non-GAAP − adjustments = GAAP), presence/ordering checks.

**Weakness.** The deterministic core is thinner than #1 — most of the value is the LLM judgment, so the "separate exact from probabilistic" story is less dramatic. Also the C&DIs are staff guidance, not law, and the release is reviewed by lawyers — HITL is real but not statutorily named.

**Public sources.**
| Source | Use | Verified? |
|---|---|---|
| [SEC Non-GAAP C&DIs (updated 12/13/2022)](https://www.sec.gov/rules-regulations/staff-guidance/corporation-finance-interpretations/non-gaap-financial-measures) | The rule set (100.01, 100.04–06, 102.10(a)–(c)) | Found |
| [SEC FRM Topic 8: Non-GAAP](https://www.sec.gov/about/divisions-offices/division-corporation-finance/financial-reporting-manual/frm-topic-8) | Supporting guidance | Found |
| EDGAR full-text search (UI: efts / `https://efts.sec.gov/LATEST/search-index`, unofficial JSON) filtered to UPLOAD/CORRESP + "non-GAAP" "prominence" | Find flagged companies → pair with the original 8-K Ex 99.1 | Endpoint undocumented; [SEC help on UPLOAD/CORRESP](https://www.sec.gov/answers/edgarletters.htm) |
| [Deloitte Non-GAAP Roadmap, App. C — SEC comments](https://dart.deloitte.com/USDART/home/accounting/sec/sec-reporting-interpretations-manual/roadmap-non-gaap-financial-measures/appendix-c-sec-comments-non-gaap/appendix-c-sec-comments-non-gaap) | Sample comment patterns | Found (some sections paywalled) |

**Test cases:** 6–8 real releases flagged by SEC (positive cases, with the SEC's exact comment as label) + 3–4 releases from the *same* companies after they fixed it (negative cases) + 2 synthetic edge cases (forward-looking non-GAAP without reconciliation; non-GAAP income statement).

---

### #3 — Lease abstraction + ASC 842 classification

**Who / what.** Corporate accounting teams (and outsourced "lease abstraction" vendors) read every real-estate/equipment lease, extract term, payments, escalations, renewal/purchase options, then classify finance vs operating under **ASC 842-10-25-2** (five tests: ownership transfer, purchase option reasonably certain, major part of economic life, PV ≥ substantially all of fair value, specialised asset).

**Fit.** Excellent LLM/deterministic split: LLM extracts terms with clause citations; a deterministic calculator does PV-of-payments and the five tests. **Weakness:** ground truth is ours (no regulator answer key); "reasonably certain" option exercise and fair value are often *not in the contract* → many cases become "insufficient information", which is honest but makes for a less crisp demo. Also a well-trodden problem (many commercial lease tools exist) — harder to be "a fit others might not have thought of".

**Public sources.** Real leases filed as EDGAR exhibits (Exhibit 10.x "Lease Agreement" via EDGAR full-text search); [PwC Leases guide PDF (Jan 2024)](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/leases/assets/pwcleasesguide0124.pdf), §3.3 classification; [Deloitte DART Roadmap 8.3 Lease Classification](https://dart.deloitte.com/USDART/home/codification/broad-transactions/asc842-10/roadmap-leasing/chapter-8-lessee-accounting/8-3-lease-classification). ASC text itself requires free FASB registration.

**Test cases:** 5 real EDGAR leases + 5–7 synthetic variants (add bargain purchase option; change term to 80% of life; specialised asset; missing discount rate; conflicting renewal clause).

---

### #4 — OFAC 50% Rule: aggregate indirect ownership by blocked persons

**Who / what.** Bank / payments compliance analysts must decide whether an *unlisted* counterparty is blocked because SDNs own ≥50% **in aggregate, directly or indirectly** ([OFAC FAQs 398–402](https://ofac.treasury.gov/faqs/topic/1521); [FAQ 401 on "indirect"](https://ofac.treasury.gov/faqs/401)). They trace ownership chains through registry filings and annual reports by hand.

**Fit & strategic note.** The deterministic core is crisp (graph traversal + aggregation rule — note it's *not* multiplicative through chains, which is a classic analyst mistake and a great test case). Strong alignment with Tresata's own business (entity resolution / AML data). **Weakness:** the hard AI step is entity resolution + extracting ownership from heterogeneous registry documents; our test cases would be almost entirely synthetic ownership trees, so evaluation is self-graded. "Control" vs "ownership" (FAQ 398) is a nice nuance.

**Public sources.** [OFAC Sanctions List Service — SDN CSV](https://sanctionslist.ofac.treas.gov/Home/static/sdn.html) (SDN.CSV, ALT.CSV, ADD.CSV); OFAC FAQs above; UK Companies House PSC (beneficial ownership) bulk data (free) for realistic structure shapes; [OpenSanctions us_ofac_sdn](https://opensanctions.org/datasets/us_ofac_sdn/) as cleaned mirror.

---

### #5 — Debt covenant compliance from credit agreements

**Who / what.** Borrower finance teams and lender agents compute quarterly leverage / fixed-charge ratios using the credit agreement's bespoke "Consolidated EBITDA" definition (add-backs, caps, pro-forma adjustments), then sign a compliance certificate.

**Fit.** Strongest "finance math" story; some companies publish the answer (e.g. NPC Restaurant Holdings 10-K reconciles Adjusted EBITDA → "Covenant EBITDA"; American Media, Standard Aero disclose actual vs required ratios) — partial ground truth. **Weakness:** credit agreements are 100–250 pages with nested defined terms; extracting the full definition tree reliably in 48h is the riskiest parsing task of the five. Inputs to add-backs (e.g. "run-rate cost savings") often aren't public.

**Public sources.** Credit agreements as EDGAR exhibits; 10-Ks with covenant disclosure, e.g. [NPC Restaurant Holdings FY2016 10-K](https://www.sec.gov/Archives/edgar/data/0001548621/000154862117000009/npci-20161227x10k.htm), [American Media FY2016 10-K](https://www.sec.gov/Archives/edgar/data/0000880555/000088055516000055/ami-20160331x10k.htm), [Standard Aero FY2006 10-K](https://www.sec.gov/Archives/edgar/data/0001323739/000095013307001063/w31592e10vk.htm).

---

## 3. Assumptions you should challenge

1. **I ranked #1 over #2 mainly on the deterministic core and the statutory HITL (CA must sign).** If you weight *external ground truth* highest, #2 wins — the SEC literally wrote our labels.
2. **I assumed an India focus is an advantage** (you're likely closer to that context, and the 2025 Act transition is a strong "why now"). If you'd rather avoid a jurisdiction mid-transition, the US W-8BEN-E variant of #1 is cleaner but weaker on "why AI".
3. **New-Act section numbers are unverified.** Secondary sources conflict on which section of the Income-tax Act 2025 replaces old s.195 and which governs Form 145. We must pull the primary bare Act + Rules before citing anything.
4. **Domain ramp-up for #1 is the real schedule risk.** Characterisation (royalty vs FTS vs business profits) is genuinely contested; we'd scope to 3–4 treaties and 4 payment types, and say so.
5. **"Make up realistic examples" is allowed by the brief**, but for #1 nearly all invoice inputs are synthetic (real ones are confidential). The *rules* are real; the *inputs* are made up — we must label that clearly.
6. I have **not** opened every source end-to-end; the "Verified?" column says which URLs I confirmed exist vs. need pulling.

## 4. Decision needed from you

Pick one problem (and for #1, India vs US variant). Then we move to Stage 2: architecture, rejected alternatives, failure modes — still no app code until you sign off.

---

### Sources consulted
- Assignment PDF: `TRESATA_TAKE HOME ASSIGNMENT.pdf` (this folder)
- [IRS Tax Treaty Tables](https://www.irs.gov/individuals/international-taxpayers/tax-treaty-tables) · [Table 1 PDF](https://www.irs.gov/pub/irs-lbi/tax-treaty-table-1.pdf)
- [SEC Non-GAAP C&DIs](https://www.sec.gov/rules-regulations/staff-guidance/corporation-finance-interpretations/non-gaap-financial-measures) · [FRM Topic 8](https://www.sec.gov/about/divisions-offices/division-corporation-finance/financial-reporting-manual/frm-topic-8) · [SEC UPLOAD/CORRESP help](https://www.sec.gov/answers/edgarletters.htm)
- [Deloitte Non-GAAP Roadmap App. C](https://dart.deloitte.com/USDART/home/accounting/sec/sec-reporting-interpretations-manual/roadmap-non-gaap-financial-measures/appendix-c-sec-comments-non-gaap/appendix-c-sec-comments-non-gaap) · [Deloitte SEC Comment Letter Roadmap](https://dart.deloitte.com/USDART/home/publications/roadmap/sec-comment-letter-considerations)
- [OFAC 50% Rule FAQs](https://ofac.treasury.gov/faqs/topic/1521) · [FAQ 401](https://ofac.treasury.gov/faqs/401) · [OFAC SLS SDN downloads](https://sanctionslist.ofac.treas.gov/Home/static/sdn.html)
- [Taxscan: IT Act 2025 forms mapping](https://www.taxscan.in/top-stories/income-tax-act-2025-forms-full-old-vs-new-comparison-mapping-guide-1445284) · [ClearTax Form 145](https://cleartax.in/s/form-145-income-tax) · [Business Today, Apr 2026](https://www.businesstoday.in/amp/personal-finance/tax/story/sending-money-overseas-new-tax-rules-could-delay-transfers-if-done-wrong-527194-2026-04-23)
- [Taxmann on Nestlé SA](https://www.taxmann.com/post/blog/dtaa-mfn-analysis-of-supreme-courts-judgment-in-nestle-sa/) · [ELP alert](https://elplaw.in/wp-content/uploads/2023/09/ELP-Tax-Alert-SC-ruling-on-MFN-clause-.pdf)
- [PwC Leases Guide](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/leases/assets/pwcleasesguide0124.pdf) · [Deloitte Lease Classification 8.3](https://dart.deloitte.com/USDART/home/codification/broad-transactions/asc842-10/roadmap-leasing/chapter-8-lessee-accounting/8-3-lease-classification)
