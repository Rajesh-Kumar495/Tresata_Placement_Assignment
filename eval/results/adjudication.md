# Adjudication of unlabelled findings on the 10 real releases

**Adjudicated by the AI assistant**, not a qualified reviewer, after reading the source text and SEC correspondence. Spot-check before relying on it.

- Findings (FLAG/NEEDS_REVIEW) on real releases: **100**, of which 17 match an SEC-raised gold label
- Unlabelled: 83: **TP 36 · DEBATABLE 37 · FP 10**
- Precision strict (gold + TP): **53%** · lenient (+ debatable): **90%**

| Rule | TP | DEBATABLE | FP |
|---|---|---|---|
| R-FWD-EXCEPTION | 5 | 1 | 0 |
| R-NORMAL-OPEX | 4 | 16 | 4 |
| R-PROM-HEADLINE | 3 | 0 | 0 |
| R-PROM-LANGUAGE | 1 | 0 | 1 |
| R-PROM-ORDER | 14 | 10 | 1 |
| R-RECON-PRESENT | 5 | 6 | 4 |
| R-RECON-START-GAAP | 2 | 4 | 0 |
| R-RECON-TIEOUT | 2 | 0 | 0 |

| Doc | Rule | Verdict | Subject | Label | Reason |
|---|---|---|---|---|---|
| A01 | R-RECON-PRESENT | FLAG | Net debt | **DEBATABLE** | Net debt / net cash / prior-year adjusted margin without an explicit reconciliation schedule |
| A01 | R-PROM-HEADLINE | FLAG | Adjusted EBITDA | **TP** | SEC c2 named adjusted EBITDA in the headline as well (gold anchor covered only the EPS line) |
| A01 | R-PROM-ORDER | FLAG | Adjusted EBITDA | **TP** | Highlight bullet presents (record) Adjusted EBITDA with no net income in the list (102.10(a)) |
| A01 | R-PROM-ORDER | FLAG | net debt position | **DEBATABLE** | Forward guidance or net debt in a bullet without the GAAP comparable |
| A01 | R-PROM-ORDER | FLAG | Net debt | **DEBATABLE** | Forward guidance or net debt in a bullet without the GAAP comparable |
| A01 | R-PROM-ORDER | FLAG | Full year Adjusted EBITDA | **DEBATABLE** | Forward guidance or net debt in a bullet without the GAAP comparable |
| A01 | R-NORMAL-OPEX | FLAG | Merger and acquisition and other expense | **FP** | Non-operating item; 100.01 concerns operating expenses |
| A01 | R-NORMAL-OPEX | FLAG | Restructuring charges | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| A01 | R-NORMAL-OPEX | NEEDS_REVIEW | Other expense (income), net | **FP** | Non-operating item; 100.01 concerns operating expenses |
| A02 | R-RECON-TIEOUT | NEEDS_REVIEW | Adjusted EBITDA | **TP** | Q11 diagnostic: the subtraction really is unlabelled; NEEDS_REVIEW naming the row is the designed outcome |
| A02 | R-RECON-TIEOUT | NEEDS_REVIEW | Adjusted EBITDA | **TP** | Q11 diagnostic: the subtraction really is unlabelled; NEEDS_REVIEW naming the row is the designed outcome |
| A02 | R-PROM-HEADLINE | FLAG | Adjusted EBITDA guidance | **TP** | Same header block the SEC raised in c4; guidance/target lines repeat the pattern |
| A02 | R-PROM-HEADLINE | FLAG | Adjusted EBITDA margin target | **TP** | Same header block the SEC raised in c4; guidance/target lines repeat the pattern |
| A02 | R-NORMAL-OPEX | NEEDS_REVIEW | Non-recurring business costs | **TP** | SEC c9 asked about exactly these adjustments (CEO separation, acquisition, non-recurring) |
| A02 | R-NORMAL-OPEX | NEEDS_REVIEW | Acquisition integration costs | **TP** | SEC c9 asked about exactly these adjustments (CEO separation, acquisition, non-recurring) |
| A02 | R-NORMAL-OPEX | NEEDS_REVIEW | CEO separation related costs | **TP** | SEC c9 asked about exactly these adjustments (CEO separation, acquisition, non-recurring) |
| A03 | R-RECON-PRESENT | FLAG | Net debt | **FP** | Components given inline (cash $182m, borrowings $1.71bn -> net debt $1.53bn): a clearly understandable reconciliation |
| A03 | R-NORMAL-OPEX | FLAG | Restructuring and Other Charges | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| A03 | R-NORMAL-OPEX | FLAG | ERP Implementation | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| A03 | R-NORMAL-OPEX | FLAG | Capri Transformation | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| A03 | R-NORMAL-OPEX | NEEDS_REVIEW | Merger Related Costs | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| A03 | R-NORMAL-OPEX | FLAG | Restructuring and Other Expense | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| A04 | R-PROM-ORDER | FLAG | EBITDA* | **DEBATABLE** | Forward guidance or net debt in a bullet without the GAAP comparable |
| A04 | R-PROM-LANGUAGE | FLAG | Ken Seipel, Chief Executive Officer said | **TP** | CEO quote characterises adjusted EBITDA as stronger than expected; SEC c2b raised non-GAAP discussion prominence |
| A05 | R-RECON-PRESENT | FLAG | Adjusted EBITDA Margin | **TP** | SEC c9/c10: modified metrics reconciled only on website; margin without GAAP margin |
| A05 | R-RECON-PRESENT | FLAG | Modified Adjusted EBITDA | **TP** | SEC c9/c10: modified metrics reconciled only on website; margin without GAAP margin |
| A05 | R-RECON-PRESENT | FLAG | Modified Revenue | **TP** | SEC c9/c10: modified metrics reconciled only on website; margin without GAAP margin |
| A05 | R-RECON-PRESENT | FLAG | Estimated Net Debt | **DEBATABLE** | Net debt / net cash / prior-year adjusted margin without an explicit reconciliation schedule |
| A05 | R-RECON-START-GAAP | NEEDS_REVIEW | Unlevered Cash Flow | **DEBATABLE** | Chained from a measure reconciled to GAAP elsewhere; routed to NEEDS_REVIEW by design |
| A05 | R-RECON-START-GAAP | NEEDS_REVIEW | Free Cash Flow excluding cash Special It | **DEBATABLE** | Chained from a measure reconciled to GAAP elsewhere; routed to NEEDS_REVIEW by design |
| A05 | R-RECON-START-GAAP | NEEDS_REVIEW | Unlevered Cash Flow excluding cash Speci | **DEBATABLE** | Chained from a measure reconciled to GAAP elsewhere; routed to NEEDS_REVIEW by design |
| A05 | R-RECON-START-GAAP | NEEDS_REVIEW | Adjusted EBITDA excluding Special Items | **DEBATABLE** | Chained from a measure reconciled to GAAP elsewhere; routed to NEEDS_REVIEW by design |
| A05 | R-PROM-ORDER | FLAG | Estimated Net Debt | **DEBATABLE** | Net debt bullet without total debt |
| A05 | R-PROM-ORDER | FLAG | Adjusted EBITDA | **FP** | Special-items detail table, not a presentation of a non-GAAP measure |
| A05 | R-NORMAL-OPEX | NEEDS_REVIEW | Exclude: Special Items | **TP** | SEC (10-K comment 2) asked Lumen to consider 100.01 for special items |
| A05 | R-NORMAL-OPEX | FLAG | Add back: Severance | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| A05 | R-NORMAL-OPEX | FLAG | Add back: Consumer and other litigation | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| A05 | R-NORMAL-OPEX | FLAG | Add back: Transaction and separation cos | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| A05 | R-NORMAL-OPEX | NEEDS_REVIEW | Add back: Real estate transactions | **FP** | Real-estate transaction gains/losses are not operating expenses |
| A05 | R-FWD-EXCEPTION | FLAG | Adjusted EBITDA Outlook | **TP** | Outlook table gives non-GAAP guidance; no unreasonable-efforts disclosure found in the release text |
| A05 | R-FWD-EXCEPTION | FLAG | Free Cash Flow Outlook | **TP** | Outlook table gives non-GAAP guidance; no unreasonable-efforts disclosure found in the release text |
| A05 | R-FWD-EXCEPTION | FLAG | Net Cash Interest | **DEBATABLE** | Unclear whether 'net cash interest' is a non-GAAP measure |
| A06 | R-RECON-PRESENT | FLAG | Adjusted EBIT margin | **TP** | Adjusted EBIT/EBITDA margins without GAAP margins; SEC c3 raised the same class of measures |
| A06 | R-RECON-PRESENT | FLAG | Adjusted EBITDA margin | **TP** | Adjusted EBIT/EBITDA margins without GAAP margins; SEC c3 raised the same class of measures |
| A06 | R-RECON-PRESENT | FLAG | Adjusted effective tax rate | **FP** | Table shows as-reported and adjusted effective tax rates side by side |
| A06 | R-RECON-START-GAAP | FLAG | Adjusted EBITDA Excluding Adjusted Equit | **TP** | Reconciliations start from adjusted EBITDA; SEC c2/c3 |
| A06 | R-RECON-START-GAAP | NEEDS_REVIEW | Free cash flow | **TP** | Reconciliations start from adjusted EBITDA; SEC c2/c3 |
| A06 | R-PROM-ORDER | FLAG | Adjusted EBIT | **TP** | Adjusted measures listed without/before GAAP comparables; SEC c3 asked for equal prominence across these measures |
| A06 | R-PROM-ORDER | FLAG | Adjusted EBIT margin | **TP** | Adjusted measures listed without/before GAAP comparables; SEC c3 asked for equal prominence across these measures |
| A06 | R-PROM-ORDER | FLAG | Adjusted EBITDA | **TP** | Highlight bullet presents (record) Adjusted EBITDA with no net income in the list (102.10(a)) |
| A06 | R-PROM-ORDER | FLAG | Adjusted EBITDA margin | **TP** | Adjusted measures listed without/before GAAP comparables; SEC c3 asked for equal prominence across these measures |
| A06 | R-PROM-ORDER | FLAG | Adjusted EBITDA excluding adjusted equit | **TP** | Adjusted measures listed without/before GAAP comparables; SEC c3 asked for equal prominence across these measures |
| A06 | R-PROM-ORDER | FLAG | Adjusted net income attributable to Adie | **TP** | Adjusted measures listed without/before GAAP comparables; SEC c3 asked for equal prominence across these measures |
| A06 | R-PROM-ORDER | FLAG | Adjusted earnings per share | **TP** | Adjusted measures listed without/before GAAP comparables; SEC c3 asked for equal prominence across these measures |
| A06 | R-PROM-ORDER | FLAG | Free cash flow | **DEBATABLE** | Cash-flow/debt measure in a list without its GAAP comparable; commonly accepted presentation |
| A06 | R-PROM-ORDER | FLAG | Net debt | **DEBATABLE** | Cash-flow/debt measure in a list without its GAAP comparable; commonly accepted presentation |
| A06 | R-PROM-ORDER | FLAG | Net leverage ratio | **TP** | Adjusted measures listed without/before GAAP comparables; SEC c3 asked for equal prominence across these measures |
| A06 | R-PROM-ORDER | FLAG | Adjusted EBITDA | **TP** | Highlight bullet presents (record) Adjusted EBITDA with no net income in the list (102.10(a)) |
| A06 | R-PROM-ORDER | FLAG | Adjusted EBITDA margin | **TP** | Adjusted measures listed without/before GAAP comparables; SEC c3 asked for equal prominence across these measures |
| A06 | R-PROM-ORDER | FLAG | Adjusted EBITDA | **TP** | Highlight bullet presents (record) Adjusted EBITDA with no net income in the list (102.10(a)) |
| A06 | R-PROM-ORDER | FLAG | Adjusted EBITDA excluding adjusted equit | **TP** | Adjusted measures listed without/before GAAP comparables; SEC c3 asked for equal prominence across these measures |
| A06 | R-NORMAL-OPEX | NEEDS_REVIEW | Adjustments | **FP** | Tax adjustment, not an operating expense |
| A06 | R-NORMAL-OPEX | NEEDS_REVIEW | Other items | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| B01 | R-RECON-PRESENT | FLAG | Net debt | **DEBATABLE** | Net debt / net cash / prior-year adjusted margin without an explicit reconciliation schedule |
| B01 | R-RECON-PRESENT | NEEDS_REVIEW | adjusted earnings | **FP** | Lexicon fragment of 'Adjusted earnings before interest, tax...' (= Adjusted EBITDA, which is reconciled) |
| B01 | R-PROM-ORDER | FLAG | Adjusted EBITDA | **TP** | Highlight bullet presents (record) Adjusted EBITDA with no net income in the list (102.10(a)) |
| B01 | R-PROM-ORDER | FLAG | Net debt | **DEBATABLE** | Forward guidance or net debt in a bullet without the GAAP comparable |
| B01 | R-PROM-ORDER | FLAG | Full year Adjusted EBITDA | **DEBATABLE** | Forward guidance or net debt in a bullet without the GAAP comparable |
| B01 | R-NORMAL-OPEX | FLAG | Merger and acquisition and other expense | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| B01 | R-NORMAL-OPEX | FLAG | Restructuring (charges) recovery | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| B01 | R-NORMAL-OPEX | FLAG | Restructuring charges (recovery) | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| B02 | R-RECON-PRESENT | FLAG | run-rate EBITDA | **FP** | Forward-looking run-rate; the release discloses why no reconciliation is provided |
| B02 | R-RECON-PRESENT | FLAG | Adjusted gross margin | **DEBATABLE** | Net debt / net cash / prior-year adjusted margin without an explicit reconciliation schedule |
| B02 | R-RECON-PRESENT | FLAG | Recurring operating expenses | **DEBATABLE** | Net debt / net cash / prior-year adjusted margin without an explicit reconciliation schedule |
| B02 | R-RECON-PRESENT | FLAG | Net cash position | **DEBATABLE** | Net debt / net cash / prior-year adjusted margin without an explicit reconciliation schedule |
| B02 | R-PROM-LANGUAGE | FLAG | “With our sharp focus on improvements in | **FP** | 'significantly' states a magnitude; not the 'record/exceptional' characterisation in 102.10(a) |
| B03 | R-NORMAL-OPEX | FLAG | Restructuring and Other Charges | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| B03 | R-NORMAL-OPEX | FLAG | ERP Implementation | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| B03 | R-NORMAL-OPEX | FLAG | Capri Transformation | **DEBATABLE** | Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments |
| B03 | R-FWD-EXCEPTION | FLAG | Adjusted operating income (guidance) | **TP** | Adjusted guidance with no reconciliation and no unreasonable-efforts disclosure (102.10(b) bullet 3) |
| B03 | R-FWD-EXCEPTION | FLAG | Adjusted operating margin (guidance) | **TP** | Adjusted guidance with no reconciliation and no unreasonable-efforts disclosure (102.10(b) bullet 3) |
| B03 | R-FWD-EXCEPTION | FLAG | Adjusted diluted earnings per share (gui | **TP** | Adjusted guidance with no reconciliation and no unreasonable-efforts disclosure (102.10(b) bullet 3) |
| B04 | R-PROM-ORDER | FLAG | Full year EBITDA* | **DEBATABLE** | Forward guidance or net debt in a bullet without the GAAP comparable |
