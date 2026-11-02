# Full evaluation: run `20261102T185847Z`

Model `deepseek/deepseek-v4.1-flash` · mode record · wall-clock 2.9 s · LLM calls 102 (cache hits 102, escalations 16, repairs 0, schema failures 0) · tokens 173,259 in / 38,295 out · HC1: gold

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

69 FLAG/NEEDS_REVIEW findings not covered by any gold label: R-PROM-ORDER 24, R-NORMAL-OPEX 24, R-RECON-PRESENT 8, R-RECON-START-GAAP 6, R-PROM-HEADLINE 2, R-RECON-TIEOUT 2, R-PROM-LANGUAGE 2, R-FWD-EXCEPTION 1

- A01 FLAG R-PROM-HEADLINE: Headline omits the most directly comparable GAAP measure (net income) for 'Adjusted EBITDA'
- A01 FLAG R-PROM-ORDER: Bullet presents 'adjusted EBITDA' before the comparable GAAP measure (net income) in the same list
- A01 FLAG R-PROM-ORDER: Bullet presents 'net debt' without the comparable GAAP measure (debt) in the same list
- A01 FLAG R-PROM-ORDER: Bullet presents 'Full year Adjusted EBITDA' without the comparable GAAP measure (net income) in the same list
- A01 FLAG R-NORMAL-OPEX: Adjustment 'Merger and acquisition and other expenses' may exclude a normal, recurring cash operating expense: M&A expenses recur and are cash operati
- A01 FLAG R-NORMAL-OPEX: Adjustment 'Restructuring charges' may exclude a normal, recurring cash operating expense: Restructuring charges can recur at irregular intervals; lab
- A01 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'Other expense (income), net' may exclude a normal, recurring cash operating expense: Label alone doesn't reveal whether it is a recurring 
- A02 NEEDS_REVIEW R-RECON-TIEOUT: t05 vertical reconciliation of 'Adjusted EBITDA': 0/1 period columns tie (Three Months Ended/June 30, 2023/Adj/EBITDA: NEEDS_REVIEW possible_unlabelle
- A02 NEEDS_REVIEW R-RECON-TIEOUT: t05 vertical reconciliation of 'Adjusted EBITDA': 0/1 period columns tie (Six Months Ended/June 30, 2023/Adj/EBITDA: NEEDS_REVIEW possible_unlabelled_
- A02 FLAG R-PROM-HEADLINE: Headline omits the most directly comparable GAAP measure (net margin) for 'Adjusted EBITDA Margin'
- A02 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'Non-recurring business costs' may exclude a normal, recurring cash operating expense: Label says non-recurring but no detail on nature; ca
- A02 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'Acquisition integration costs' may exclude a normal, recurring cash operating expense: Label alone; no description of nature or frequency 
- A02 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'CEO separation related costs' may exclude a normal, recurring cash operating expense: Label alone; cannot determine whether recurring cash
- A03 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Net debt'
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
- A05 NEEDS_REVIEW R-RECON-START-GAAP: Reconciliation of 'Unlevered Cash Flow' in t08 starts from 'Free Cash Flow', a non-GAAP figure that is itself reconciled from GAAP elsewhere in the re
- A05 NEEDS_REVIEW R-RECON-START-GAAP: Reconciliation of 'Free Cash Flow excluding cash Special Items' in t08 starts from 'Free Cash Flow', a non-GAAP figure that is itself reconciled from 
- A05 NEEDS_REVIEW R-RECON-START-GAAP: Reconciliation of 'Unlevered Cash Flow excluding cash Special Items' in t08 starts from 'Unlevered Cash Flow', a non-GAAP figure that is itself reconc
- A05 NEEDS_REVIEW R-RECON-START-GAAP: Reconciliation of 'Adjusted EBITDA excluding Special Items' in t09 starts from 'Adjusted EBITDA', a non-GAAP figure that is itself reconciled from GAA
- A05 FLAG R-PROM-ORDER: Bullet presents 'Net Debt' without the comparable GAAP measure (debt) in the same list
- A05 FLAG R-PROM-ORDER: Table t07: non-GAAP row 'Total Special Items impacting Adjusted EBITDA' appears without a preceding GAAP net income row
- A05 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'Exclude: Special Items' may exclude a normal, recurring cash operating expense: Label 'Special Items' is undefined; cannot determine if it
- A05 FLAG R-NORMAL-OPEX: Adjustment 'Add back: Severance' may exclude a normal, recurring cash operating expense: Severance is a cash operating expense that occurs repeatedly 
- A05 FLAG R-NORMAL-OPEX: Adjustment 'Add back: Consumer and other litigation' may exclude a normal, recurring cash operating expense: Litigation costs recur occasionally at ir
- A05 FLAG R-NORMAL-OPEX: Adjustment 'Add back: Transaction and separation costs' may exclude a normal, recurring cash operating expense: Transaction and separation costs are c
- A05 NEEDS_REVIEW R-NORMAL-OPEX: Adjustment 'Add back: Real estate transactions' may exclude a normal, recurring cash operating expense: Label alone does not reveal whether these are 
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
- B01 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Net debt'
- B01 FLAG R-PROM-ORDER: Bullet presents 'Adjusted EBITDA' before the comparable GAAP measure (net income) in the same list
- B01 FLAG R-PROM-ORDER: Bullet presents 'Net debt' without the comparable GAAP measure (debt) in the same list
- B01 FLAG R-PROM-ORDER: Bullet presents 'Adjusted EBITDA' without the comparable GAAP measure (net income) in the same list
- B01 FLAG R-NORMAL-OPEX: Adjustment 'Merger and acquisition and other expenses' may exclude a normal, recurring cash operating expense: M&A and other expenses recur and are ca
- B01 FLAG R-NORMAL-OPEX: Adjustment 'Restructuring (charges) recovery' may exclude a normal, recurring cash operating expense: Restructuring charges recur, including at irregu
- B01 FLAG R-NORMAL-OPEX: Adjustment 'Restructuring charges (recovery)' may exclude a normal, recurring cash operating expense: Restructuring charges recur, including at irregu
- B02 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'run-rate EBITDA'
- B02 FLAG R-RECON-PRESENT: No quantitative reconciliation to the most directly comparable GAAP measure found for 'Adjusted gross margin'
- B02 FLAG R-PROM-LANGUAGE: Language prominence: Characterizes non-GAAP adjusted EBITDA as increased significantly without equally prominent similar description of comparable GAA
- B03 FLAG R-NORMAL-OPEX: Adjustment 'Restructuring and Other Charges' may exclude a normal, recurring cash operating expense: Severance and store closure costs are cash operat
- B03 FLAG R-NORMAL-OPEX: Adjustment 'ERP Implementation' may exclude a normal, recurring cash operating expense: Multi-year ERP implementation costs are recurring cash operati
- B03 FLAG R-NORMAL-OPEX: Adjustment 'Capri Transformation' may exclude a normal, recurring cash operating expense: Multi-year transformation costs spanning operations are recu
- B03 FLAG R-FWD-EXCEPTION: Forward-looking non-GAAP 'Adjusted guidance (fiscal 2026)' has no reconciliation and no disclosed reliance on the unreasonable-efforts exception
- B04 FLAG R-PROM-ORDER: Bullet presents 'EBITDA*' without the comparable GAAP measure (net income) in the same list

## Measure inventory (10 real releases)

Recall LLM-only **73/73** · surfaced to HC1 **73/73** · precision **73/73** (predictions matching a gold measure)


## Tie-out on real releases

72 reconciliations · checks: PASS 351, NEEDS_REVIEW 2, NOT_EVALUATED 11 · reconciliations relying on an LLM-inferred sign: 0

## Tier C/D: synthetic mutations and traps

**0/0 pass**, 0 weak (NEEDS_REVIEW where FLAG expected), 0 fail · core set 0/0

| Case | Core | Result | Checks |
|---|---|---|---|

## Grounding of final evidence

396/396 evidence quotes found verbatim in the source (target: 0 failures)

## Verdicts by rule (all 30 documents)

| Rule | PASS | FLAG | NEEDS_REVIEW | NOT_EVALUATED |
|---|---|---|---|---|
| R-EBITDA-FROM-NI | 9 | 2 | 0 | 0 |
| R-EBITDA-LABEL | 10 | 0 | 0 | 0 |
| R-FWD-EXCEPTION | 18 | 1 | 0 | 0 |
| R-NORMAL-OPEX | 0 | 20 | 18 | 0 |
| R-PERSHARE-LIQ | 10 | 0 | 0 | 0 |
| R-PROM-HEADLINE | 3 | 5 | 0 | 4 |
| R-PROM-LANGUAGE | 6 | 4 | 0 | 0 |
| R-PROM-ORDER | 3 | 31 | 0 | 0 |
| R-PROM-STYLE | 6 | 0 | 0 | 4 |
| R-RECON-PRESENT | 2 | 15 | 0 | 0 |
| R-RECON-START-GAAP | 8 | 1 | 6 | 0 |
| R-RECON-TIEOUT | 47 | 0 | 2 | 8 |
| R-TAX-SEPARATE | 9 | 1 | 0 | 0 |
| R-USEFULNESS | 10 | 0 | 0 | 0 |
