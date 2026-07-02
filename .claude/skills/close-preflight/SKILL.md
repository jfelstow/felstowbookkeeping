---
name: close-preflight
description: Run the month-end close pre-flight for the connected QuickBooks client — pull P&L/balance sheet/agings, scan for anomalies, and produce the fix-first report before opening QBO. Use when asked to run a close pre-flight, month-end prep, or "what needs fixing before I close the books".
---

# Month-End Close Pre-Flight

Produce a one-page "fix-first" brief for the close month so Jake opens QBO already knowing
what needs attention. The close month is the most recent *completed* calendar month unless
the user names one.

## Step 1 — Pull the data (QuickBooks MCP)

1. `company_info` first (establishes the connection; gives the client name).
2. `profit_loss_quickbooks_account` for a range from **5–6 months before** the close month
   through the **last day of the close month** (monthly breakdown is needed for baselines).
   The result is usually saved to a file — keep that path.
3. `qbo_accounting_get_balance_sheet` with start_date = end_date = last day of close month.
4. `qbo_accounting_get_ar_aging_detail` and `qbo_accounting_get_ap_aging_detail`
   with as_of_date = last day of close month.

## Step 2 — Run the P&L anomaly scan

```
python3 tools/close-preflight/analyze_pnl.py <saved_pnl_json_file>
```

Flags produced: UNCATEGORIZED, NEGATIVE, MISSING (recurring account posted $0), NEW,
SPIKE, DROP. Defaults: ±50% vs prior-month average, $250 minimum variance
(override with `--spike-pct` / `--min-dollars` for very small or very large clients).

Don't dump the raw scan into the report — apply judgment. Group related findings into
stories (e.g. production labor DROP + payroll-tax MISSING + payroll clearing balance
= "payroll partially booked"). Cross-check flags against each other and the balance
sheet before calling something an error; some "anomalies" tie out (an annual accrual,
a new revenue channel).

## Step 3 — Balance sheet checklist

Check each and note only exceptions:

- **Undeposited Funds** ≠ 0 → deposits not applied
- **Clearing accounts** (payroll/merchant/transfer) ≠ 0 → stuck entries
- **Wrong-sign balances**: negative liabilities, negative expense lines, contra-sign equity
- **Loan balances vs. activity**: financing that should amortize but hasn't moved
  (repayments miscoded), new draws, balances that don't change month to month
- **Payables sanity**: A/P of exactly $0 at a business that gets bills → bills likely not entered
- **Accrual ties**: large one-time expenses vs. matching payable/prepaid (do they tie to the penny?)
- **Net income tie-out**: balance sheet Net Income vs. P&L net for the fiscal YTD —
  a mismatch usually means a non-calendar fiscal year (and possibly a year-end close)

## Step 4 — A/R & A/P

- New or growing 60+ day receivables; anything worth a nudge email
- Bills overdue or due within 14 days

## Step 5 — Write the report

Save to `reports/close-preflight/YYYY-MM-<client-slug>.md`. Structure
(see `reports/close-preflight/2026-06-fresh-dry-snacks.md` as the reference):

1. Header: client, close month, baseline range, data pulled, and any headline warning
   (e.g. fiscal year-end)
2. **Fix-first list** — numbered, worst first, each with the evidence and the likely cause
3. **Verified — no action needed** — checks that passed or tied out (builds trust in the list)
4. **Anomalies to review while categorizing** — table of remaining SPIKE/DROP/MISSING items
5. **Month in numbers** — monthly income/COGS/expenses/net table with one sentence of context
6. **Client-conversation flags** — advisory material, not close blockers (cash position,
   personal-card spend, financing costs). These feed the monthly client email and are
   upsell surface for the cash-flow dashboard.
7. **Manual checklist** — what the API can't see: reconciliation status, stale checks,
   bank-feed review queue

Numbers in the fix-first list must come from the pulled data, never from memory.
Round to whole dollars in prose; keep cents in tie-outs (ties "to the penny" are the point).
