# Full evaluation: run `20261102T184705Z`

Model `deepseek/deepseek-v4.1-flash` · mode replay · wall-clock 15.5 s · LLM calls 200 (cache hits 200, escalations 18, repairs 0, schema failures 0) · tokens 411,839 in / 109,830 out

## Tier A: SEC-raised issues (recall)

**17/19 detected** (16 with the expected verdict, 1 as NEEDS_REVIEW where FLAG was expected; 2 'offsite' = same rule raised elsewhere in the document but not at the SEC's location, NOT counted) · pre-registered target ≥ 70% · NOT_EVALUATED expectations: 2/2

| Doc | Rule | Expected | Result | Got | SEC comment |
|---|---|---|---|---|---|
| A01 aviat | R-PROM-HEADLINE | FLAG | **hit** | FLAG | c2: adjusted EBITDA and non-GAAP diluted EPS in the headline without t |
| A01 aviat | R-RECON-PRESENT | FLAG | **hit** | FLAG | c3: non-GAAP total operating expenses discussed with no reconciliation |
| A02 turtlebeach | R-PROM-HEADLINE | FLAG | **hit** | FLAG | c4: header gives % change in Adjusted EBITDA without the GAAP % change |
| A02 turtlebeach | R-TAX-SEPARATE | FLAG | **hit** | FLAG | c5: Table 4 adjustments presented net of tax (102.11) |
| A02 turtlebeach | R-EBITDA-FROM-NI | FLAG | **hit** | FLAG | c7: Table 5 does not reconcile Adjusted EBITDA to net income (starts a |
| A02 turtlebeach | R-NORMAL-OPEX | NEEDS_REVIEW | **hit** | NEEDS_REVIEW | c9: asks how CEO separation, inventory, acquisition, non-recurring and |
| A03 capri | R-PROM-ORDER | FLAG | **hit** | FLAG | c4a: highlight bullets present adjusted operating margin and adjusted  |
| A03 capri | R-PROM-ORDER | FLAG | **hit** | FLAG | c4a (second measure) |
| A03 capri | R-RECON-PRESENT | FLAG | **hit** | FLAG | c4b: no reconciliation of adjusted operating margin |
| A03 capri | R-RECON-PRESENT | FLAG | **hit** | FLAG | c5: free cash flow not identified as non-GAAP and lacks Item 10(e) dis |
| A04 cititrends | R-PROM-HEADLINE | FLAG | **hit** | FLAG | c2a: adjusted EBITDA in the headline block without net income at equal |
| A04 cititrends | R-RECON-PRESENT | FLAG | **hit** | FLAG | c2b: provide all Item 10(e) disclosures for the flowthrough measure |
| A04 cititrends | R-NORMAL-OPEX | NEEDS_REVIEW | **hit** | NEEDS_REVIEW | c1/c2c: break out 'other non-recurring expenses', consider 100.01 |
| A05 lumen | R-PROM-ORDER | FLAG | **hit** | FLAG | c10: non-GAAP measures listed before the GAAP comparable on 'Financial |
| A05 lumen | R-RECON-PRESENT | FLAG | **offsite** | - | c9: 'Modified' metrics; reconciliation only on the company website, no |
| A06 adient | R-RECON-START-GAAP | FLAG | **weak** | NEEDS_REVIEW | c2: adjusted EBITDA reconciled to adjusted results rather than to GAAP |
| A06 adient | R-RECON-PRESENT | FLAG | **offsite** | - | c3: adjusted equity income etc. lack the most directly comparable GAAP |
| A06 adient | R-RECON-PRESENT | FLAG | **hit** | FLAG | c3: net leverage ratio without GAAP comparable |
| A06 adient | R-NORMAL-OPEX | NEEDS_REVIEW | **hit** | FLAG, NEEDS_REVIEW | c4: whether restructuring-type costs are normal, recurring, cash opera |
| A06 adient | R-PROM-HEADLINE | NOT_EVALUATED | **hit** | FLAG, NOT_EVALUATED |  |
| A06 adient | R-PROM-STYLE | NOT_EVALUATED | **hit** | NOT_EVALUATED |  |

## Must-not-flag checks (Tier A + B precision)

**18/18 clean** (violations = FLAG where the gold says no issue)

- 2 NEEDS_REVIEW finding(s) on must-not-flag rules (not violations; a reviewer looks)

## Unlabelled findings on real documents (need manual adjudication)

86 FLAG/NEEDS_REVIEW findings not covered by any gold label: R-PROM-ORDER 27, R-NORMAL-OPEX 24, R-RECON-PRESENT 16, R-RECON-START-GAAP 6, R-FWD-EXCEPTION 6, R-PROM-HEADLINE 3, R-RECON-TIEOUT 2, R-PROM-LANGUAGE 2

- A01 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Adjusted earnings before interest, tax, depreciation and amorti
- A01 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Net debt'
- A01 FLAG R-PROM-HEADLINE: Headline omits the most directly comparable GAAP measure (net income) for 'Adjusted EBITDA'
- A01 FLAG R-PROM-ORDER: Bullet presents 'adjusted EBITDA' before the comparable GAAP measure (net income) in the same list
- A01 FLAG R-PROM-ORDER: Bullet presents 'net debt position' without the comparable GAAP measure (debt) in the same list
- A01 FLAG R-PROM-ORDER: Bullet presents 'Full year Adjusted EBITDA' without the comparable GAAP measure (net income) in the same list
- A01 FLAG R-PROM-ORDER: Table t03: non-GAAP row 'Non-GAAP research and development expenses' appears without a preceding GAAP opex row
- A01 FLAG R-NORMAL-OPEX: Adjustment 'Merger and acquisition and other expenses' may exclude a normal, recurring cash operating expense: M&A expenses recur and are cash operati
- A01 FLAG R-NORMAL-OPEX: Adjustment 'Restructuring charges' may exclude a normal, recurring cash operating expense: Restructuring charges can recur at irregular intervals; lab
- A01 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'Other expense (income), net' may exclude a normal, recurring cash operating expense: Label alone doesn't reveal whether it is a recurring 
- A02 NEEDS_REVIEW R-RECON-TIEOUT: t05 vertical reconciliation of 'Adjusted EBITDA': 0/1 period columns tie (Three Months Ended/June 30, 2023/Adj/EBITDA: NEEDS_REVIEW possible_unlabelle
- A02 NEEDS_REVIEW R-RECON-TIEOUT: t05 vertical reconciliation of 'Adjusted EBITDA': 0/1 period columns tie (Six Months Ended/June 30, 2023/Adj/EBITDA: NEEDS_REVIEW possible_unlabelled_
- A02 FLAG R-PROM-HEADLINE: Headline omits the most directly comparable GAAP measure (net income) for 'Adjusted EBITDA Guidance'
- A02 FLAG R-PROM-HEADLINE: Headline omits the most directly comparable GAAP measure (net margin) for 'Adjusted EBITDA Margin Target'
- A02 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'Non-recurring business costs' may exclude a normal, recurring cash operating expense: Label says non-recurring but no detail on nature; ca
- A02 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'Acquisition integration costs' may exclude a normal, recurring cash operating expense: Label alone; no description of nature or frequency 
- A02 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'CEO separation related costs' may exclude a normal, recurring cash operating expense: Label alone; cannot determine whether recurring cash
- A03 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Net debt'
- A03 FLAG R-PROM-ORDER: Bullet presents 'free cash flow' without the comparable GAAP measure (cash ops) in the same list
- A03 FLAG R-NORMAL-OPEX: Adjustment 'Restructuring and Other Charges' may exclude a normal, recurring cash operating expense: Restructuring and store closure costs recur at ir
- A03 FLAG R-NORMAL-OPEX: Adjustment 'ERP Implementation' may exclude a normal, recurring cash operating expense: Multi-year ERP implementation is a recurring operating expense
- A03 FLAG R-NORMAL-OPEX: Adjustment 'Capri Transformation' may exclude a normal, recurring cash operating expense: Multi-year transformation program covering operations is a r
- A03 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'Merger Related Costs' may exclude a normal, recurring cash operating expense: Label alone does not reveal whether costs are recurring cash
- A03 FLAG R-NORMAL-OPEX: Adjustment 'Restructuring and Other Expense' may exclude a normal, recurring cash operating expense: Restructuring and store closure costs recur at ir
- A04 FLAG R-PROM-ORDER: Bullet presents 'EBITDA*' without the comparable GAAP measure (net income) in the same list
- A04 FLAG R-PROM-LANGUAGE: Language prominence: Characterizes non-GAAP adjusted EBITDA as 'stronger-than-expected' without equally prominent similar description of comparable GA
- A05 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Adjusted EBITDA Margin'
- A05 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Modified Adjusted EBITDA'
- A05 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Modified Revenue'
- A05 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Estimated Net Debt'
- A05 NEEDS_REVIEW R-RECON-START-GAAP: Reconciliation of 'Unlevered Cash Flow' in t08 starts from 'Free Cash Flow', a non-GAAP figure that is itself reconciled from GAAP elsewhere in the re
- A05 NEEDS_REVIEW R-RECON-START-GAAP: Reconciliation of 'Free Cash Flow excluding cash Special Items' in t08 starts from 'Free Cash Flow', a non-GAAP figure that is itself reconciled from 
- A05 NEEDS_REVIEW R-RECON-START-GAAP: Reconciliation of 'Unlevered Cash Flow excluding cash Special Items' in t08 starts from 'Unlevered Cash Flow', a non-GAAP figure that is itself reconc
- A05 NEEDS_REVIEW R-RECON-START-GAAP: Reconciliation of 'Adjusted EBITDA excluding Special Items' in t09 starts from 'Adjusted EBITDA', a non-GAAP figure that is itself reconciled from GAA
- A05 FLAG R-PROM-ORDER: Bullet presents 'Estimated Net Debt' without the comparable GAAP measure (debt) in the same list
- A05 FLAG R-PROM-ORDER: Table t07: non-GAAP row 'Total Special Items impacting Adjusted EBITDA' appears without a preceding GAAP net income row
- A05 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'Exclude: Special Items' may exclude a normal, recurring cash operating expense: Label 'Special Items' is undefined; cannot determine if it
- A05 FLAG R-NORMAL-OPEX: Adjustment 'Add back: Severance' may exclude a normal, recurring cash operating expense: Severance is a cash operating expense that occurs repeatedly 
- A05 FLAG R-NORMAL-OPEX: Adjustment 'Add back: Consumer and other litigation' may exclude a normal, recurring cash operating expense: Litigation costs recur occasionally at ir
- A05 FLAG R-NORMAL-OPEX: Adjustment 'Add back: Transaction and separation costs' may exclude a normal, recurring cash operating expense: Transaction and separation costs are c
- A05 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'Add back: Real estate transactions' may exclude a normal, recurring cash operating expense: Label alone does not reveal whether these are 
- A05 FLAG R-FWD-EXCEPTION: Forward-looking non-GAAP 'Adjusted EBITDA Outlook' has no reconciliation and no disclosed reliance on the unreasonable-efforts exception
- A05 FLAG R-FWD-EXCEPTION: Forward-looking non-GAAP 'Free Cash Flow Outlook' has no reconciliation and no disclosed reliance on the unreasonable-efforts exception
- A05 FLAG R-FWD-EXCEPTION: Forward-looking non-GAAP 'Net Cash Interest' has no reconciliation and no disclosed reliance on the unreasonable-efforts exception
- A06 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Adjusted EBIT margin'
- A06 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Adjusted EBITDA margin'
- A06 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Adjusted effective tax rate'
- A06 FLAG R-RECON-START-GAAP: Reconciliation of 'Adjusted EBITDA Excluding Adjusted Equity Income' in t09 starts from 'Adjusted EBITDA', a non-GAAP figure
- A06 NEEDS_REVIEW R-RECON-START-GAAP: Reconciliation of 'Free cash flow' in t15 starts from 'Adjusted EBITDA excluding adjusted equity income', a non-GAAP figure that is itself reconciled 
- A06 FLAG R-PROM-ORDER: Bullet presents 'Adjusted EBIT' before the comparable GAAP measure (net income) in the same list
- A06 FLAG R-PROM-ORDER: Bullet presents 'Adjusted EBIT margin' without the comparable GAAP measure (net margin) in the same list
- A06 FLAG R-PROM-ORDER: Bullet presents 'Adjusted EBITDA' before the comparable GAAP measure (net income) in the same list
- A06 FLAG R-PROM-ORDER: Bullet presents 'Adjusted EBITDA margin' without the comparable GAAP measure (net margin) in the same list
- A06 FLAG R-PROM-ORDER: Bullet presents 'Adjusted EBITDA excluding adjusted equity income' before the comparable GAAP measure (net income) in the same list
- A06 FLAG R-PROM-ORDER: Bullet presents 'Adjusted net income attributable to Adient' before the comparable GAAP measure (net income) in the same list
- A06 FLAG R-PROM-ORDER: Bullet presents 'Adjusted earnings per share' without the comparable GAAP measure (eps) in the same list
- A06 FLAG R-PROM-ORDER: Bullet presents 'Free cash flow' before the comparable GAAP measure (cash ops) in the same list
- A06 FLAG R-PROM-ORDER: Bullet presents 'Net debt' without the comparable GAAP measure (debt) in the same list
- A06 FLAG R-PROM-ORDER: Bullet presents 'Net leverage ratio' without the comparable GAAP measure (debt) in the same list
- A06 FLAG R-PROM-ORDER: Table t07: non-GAAP row 'Adjusted EBITDA' appears without a preceding GAAP net income row
- A06 FLAG R-PROM-ORDER: Table t08: non-GAAP row 'Adjusted EBITDA margin' appears without a preceding GAAP net margin row
- A06 FLAG R-PROM-ORDER: Table t13: non-GAAP row 'LTM Adjusted EBITDA' appears without a preceding GAAP net income row
- A06 FLAG R-PROM-ORDER: Table t15: non-GAAP row 'Adjusted EBITDA excluding adjusted equity income' appears without a preceding GAAP net income row
- A06 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'Adjustments' may exclude a normal, recurring cash operating expense: Tax-related adjustments are not operating expenses, but generic label
- A06 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'Other items' may exclude a normal, recurring cash operating expense: Generic 'Other items' label with no detail; cannot assess whether rec
- B01 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Adjusted earnings before interest, tax, depreciation and amorti
- B01 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Net debt'
- B01 FLAG R-PROM-ORDER: Bullet presents 'Adjusted EBITDA' before the comparable GAAP measure (net income) in the same list
- B01 FLAG R-PROM-ORDER: Bullet presents 'Net debt' without the comparable GAAP measure (debt) in the same list
- B01 FLAG R-PROM-ORDER: Bullet presents 'Full year Adjusted EBITDA' without the comparable GAAP measure (net income) in the same list
- B01 FLAG R-NORMAL-OPEX: Adjustment 'Merger and acquisition and other expenses' may exclude a normal, recurring cash operating expense: M&A and other expenses recur and are ca
- B01 FLAG R-NORMAL-OPEX: Adjustment 'Restructuring (charges) recovery' may exclude a normal, recurring cash operating expense: Restructuring charges recur, including at irregu
- B01 FLAG R-NORMAL-OPEX: Adjustment 'Restructuring charges (recovery)' may exclude a normal, recurring cash operating expense: Restructuring charges recur, including at irregu
- B02 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'run-rate EBITDA'
- B02 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Adjusted gross margin'
- B02 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Recurring operating expenses'
- B02 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Net cash position'
- B02 FLAG R-PROM-LANGUAGE: Language prominence: Characterizes non-GAAP adjusted EBITDA as increasing significantly without equally prominent similar description of comparable GA
- B03 FLAG R-PROM-ORDER: Bullet presents 'free cash flow' without the comparable GAAP measure (cash ops) in the same list
- B03 FLAG R-NORMAL-OPEX: Adjustment 'Restructuring and Other Charges' may exclude a normal, recurring cash operating expense: Severance and store closure costs are cash operat
- B03 FLAG R-NORMAL-OPEX: Adjustment 'ERP Implementation' may exclude a normal, recurring cash operating expense: Multi-year ERP implementation costs are recurring cash operati
- B03 FLAG R-NORMAL-OPEX: Adjustment 'Capri Transformation' may exclude a normal, recurring cash operating expense: Multi-year transformation costs spanning operations are recu
- B03 FLAG R-FWD-EXCEPTION: Forward-looking non-GAAP 'Adjusted operating income (guidance)' has no reconciliation and no disclosed reliance on the unreasonable-efforts exception
- B03 FLAG R-FWD-EXCEPTION: Forward-looking non-GAAP 'Adjusted operating margin (guidance)' has no reconciliation and no disclosed reliance on the unreasonable-efforts exception
- B03 FLAG R-FWD-EXCEPTION: Forward-looking non-GAAP 'Adjusted diluted earnings per share (guidance)' has no reconciliation and no disclosed reliance on the unreasonable-efforts 
- B04 FLAG R-PROM-ORDER: Bullet presents 'Full year EBITDA*' without the comparable GAAP measure (net income) in the same list

## Measure inventory (10 real releases)

Recall LLM-only **73/73** · surfaced to HC1 **73/73** · precision **79/85** (predictions matching a gold measure)

- A01-aviat-2025-02-04: missed []; unmatched predictions ['Net debt']
- A05-lumen-2023-02-07: missed []; unmatched predictions ['Estimated Net Debt', 'Net Cash Interest']
- A06-adient-2024-02-07: missed []; unmatched predictions ['Net debt']
- B02-turtlebeach-2023-11-07: missed []; unmatched predictions ['Recurring operating expenses', 'Net cash position']

## Tie-out on real releases

72 reconciliations · checks: PASS 351, NEEDS_REVIEW 2, NOT_EVALUATED 11 · reconciliations relying on an LLM-inferred sign: 0

## Tier C/D: synthetic mutations and traps

**20/20 pass**, 0 weak (NEEDS_REVIEW where FLAG expected), 0 fail · core set 17/17

| Case | Core | Result | Checks |
|---|---|---|---|
| M01 | ✓ | **pass** | R-PROM-HEADLINE=FLAG → pass |
| M02 | ✓ | **pass** | R-RECON-TIEOUT=FLAG → pass |
| M03 | ✓ | **pass** | R-RECON-TIEOUT=FLAG → pass |
| M04 | ✓ | **pass** | R-PROM-LANGUAGE=FLAG → pass |
| M05 | ✓ | **pass** | R-PROM-STYLE=FLAG → pass |
| M06 | ✓ | **pass** | R-PERSHARE-LIQ=FLAG → pass |
| M07 | ✓ | **pass** | R-EBITDA-LABEL=FLAG → pass |
| M10 | ✓ | **pass** | R-USEFULNESS=FLAG → pass |
| M11 |  | **pass** | R-FWD-EXCEPTION=FLAG → pass |
| M13 | ✓ | **pass** | R-RECON-TIEOUT=PASS → pass |
| M14 | ✓ | **pass** | R-RECON-TIEOUT=PASS → pass |
| C00 | ✓ | **pass** | no R-PROM-HEADLINE FLAG → pass; no R-RECON-TIEOUT FLAG → pass; no R-PROM-STYLE FLAG → pass; no R-PERSHARE-LIQ FLAG → pass; no R-EBITDA-LABEL FLAG → pass; no R-USEFULNESS FLAG → pass |
| D01 | ✓ | **pass** | R-RECON-TIEOUT=FLAG → pass; injected text never used as evidence → pass |
| D04 | ✓ | **pass** | R-RECON-TIEOUT=FLAG → pass; exactly one period column non-PASS → pass |
| D05 | ✓ | **pass** | R-RECON-PRESENT=FLAG → pass; 'cash earnings' inventoried or surfaced → pass |
| D06 | ✓ | **pass** | no FLAG at all → pass; inventory empty → pass |
| D08 | ✓ | **pass** | R-RECON-TIEOUT=PASS → pass |
| D09 |  | **pass** | no R-PROM-LANGUAGE FLAG → pass |
| D10 |  | **pass** | no R-RECON-PRESENT FLAG → pass |
| D13 | ✓ | **pass** | R-RECON-TIEOUT=NEEDS_REVIEW(possible_subtotal_misclassified) → pass |

## Grounding of final evidence

1209/1209 evidence quotes found verbatim in the source (target: 0 failures)

## Verdicts by rule (all 30 documents)

| Rule | PASS | FLAG | NEEDS_REVIEW | NOT_EVALUATED |
|---|---|---|---|---|
| R-EBITDA-FROM-NI | 29 | 2 | 0 | 0 |
| R-EBITDA-LABEL | 29 | 1 | 0 | 0 |
| R-FWD-EXCEPTION | 34 | 7 | 0 | 0 |
| R-NORMAL-OPEX | 1 | 77 | 19 | 0 |
| R-PERSHARE-LIQ | 29 | 1 | 0 | 0 |
| R-PROM-HEADLINE | 22 | 7 | 0 | 4 |
| R-PROM-LANGUAGE | 7 | 24 | 0 | 0 |
| R-PROM-ORDER | 3 | 91 | 0 | 0 |
| R-PROM-STYLE | 25 | 1 | 0 | 4 |
| R-RECON-PRESENT | 3 | 63 | 0 | 0 |
| R-RECON-START-GAAP | 28 | 1 | 6 | 0 |
| R-RECON-TIEOUT | 194 | 4 | 3 | 8 |
| R-TAX-SEPARATE | 29 | 1 | 0 | 0 |
| R-USEFULNESS | 29 | 1 | 0 | 0 |
