# Close Pre-Flight — Fresh Dry Snacks
**Close month:** June 2026 · **Prepared:** July 2, 2026 · **Baseline:** Jan–May 2026 (5 months)
**Data pulled:** P&L (monthly, Jan 1 – Jun 30), Balance Sheet as of 6/30, A/R + A/P aging detail as of 6/30

> ⚠️ **This appears to be the fiscal year-end close, not just a month close.** The balance sheet's
> Net Income line (-$534,229 FYTD) far exceeds Jan–Jun P&L net (~-$415,634), which is consistent
> with a July–June fiscal year. Confirm FY start in QBO settings — if June 30 is FYE, add the
> year-end steps (depreciation, loan interest splits, accruals) to this close.

---

## Fix-first list (work top to bottom)

1. **Payroll is only partially booked for June.** Production Labor posted $52.60 vs a $5,962/mo
   average, Production Payroll Taxes posted $0 (nonzero all 5 prior months) — yet Admin Wages
   ($12,000) and Sales Wages ($2,000) posted as suspiciously round numbers, and **Payroll Clearing
   is stuck at $2,935.23** on the balance sheet (a clearing account should flush to zero).
   Likely one or more June payroll runs never made it out of clearing / never got split to
   production accounts.
2. **Uncategorized Expense holds $803.81** (account 99999, accumulated across the range).
   Reclassify before issuing statements.
3. **Business insurance posted $0 in June** (avg $1,887/mo, active 4 of 5 prior months).
   Missing bill or a lapsed policy — either way, chase it.
4. **Shopify Capital Loan 2 ($66,000, Apr 2026) shows zero repayments in 3 months.** Shopify
   Capital remits from daily sales, so the balance should be declining. Repayments are probably
   sitting in the wrong account — note Interest Paid spiked to $7,643.62 (+71% vs avg), and
   website sales may be recorded net of remittance. Trace the Shopify payouts.
5. **Three wrong-sign balances:** Shareholder Loan (long-term liability) at **-$169.89**,
   Owner Contribution (equity) at **-$4,673.75**, Miscellaneous Expense at **-$21.01**.
   Small dollars, but wrong-sign accounts always mean a misposting.

## Verified — no action needed

- **Property taxes tie out to the penny:** $33,045.00 expense + $2,516.83 Penalties & Late Fees
  = the $35,561.83 Property Taxes Payable. The annual accrual (with late penalties) was booked in
  June. Only remaining check: confirm whether the payment has since gone out.
- **Undeposited Funds: $0.00** ✓
- **A/R is nearly clean:** one open invoice — The Corner Store, $386.71, due 6/24, 6 days past
  due. Worth a nudge, not a worry. (First wholesale revenue in the range — new channel ✓.)
- **A/P: $0 outstanding.** For a manufacturer this may mean bills aren't being entered (expenses
  hitting on payment instead) — fine if intentional/cash-basis habits, but confirm.

## Anomalies to review while categorizing

| Flag | Account | June | Prior avg | Note |
|---|---|---:|---:|---|
| SPIKE | 66100 R&M – Facilities | $1,328.25 | $122.18 | +987% — one-off repair? |
| SPIKE | 62450 Computer Software | $825.51 | $386.77 | +113% — new subscription? (audit candidate) |
| SPIKE | 53400 COGS – Packaging | $1,367.93 | $789.60 | +73% |
| SPIKE | 66120 R&M – Equipment | $363.64 | $109.00 | +234% |
| DROP | 53200 COGS – Ingredients | $1,399.21 | $4,729.86 | −70% — consistent with unbooked production month |
| DROP | 66150 R&M – Vehicles | $354.71 | $2,627.49 | −87% |
| DROP | 67400 Lodging | $176.28 | $1,043.83 | −83% |
| DROP | 61200 Email Marketing | $150.00 | $622.83 | −76% — Klaviyo bill missing? |
| MISSING | 67100 Airfare | $0 | $572.44 | active 5/5 prior months |
| MISSING | 62300 Charitable Contributions | $0 | $264.80 | active 5/5 prior months |

*(Full 22-finding scan: run `tools/close-preflight/analyze_pnl.py` against the saved P&L JSON.)*

## Month in numbers

| Month | Income | COGS | Expenses | Net income |
|---|---:|---:|---:|---:|
| Jan | $16,889 | $20,483 | $75,528 | −$79,121 |
| Feb | $19,540 | $22,611 | $66,881 | −$69,952 |
| Mar | $15,543 | $24,948 | $61,902 | −$71,307 |
| Apr | $27,362 | $20,787 | $66,686 | −$60,110 |
| May | $9,963 | $13,172 | $53,990 | −$57,199 |
| **Jun** | **$11,933** | **$4,187** | **$85,691** | **−$77,945** |

June's swing is mostly the $33K property-tax accrual plus under-booked COGS/payroll — the
operating picture is closer to May than the raw number suggests. Once items 1–4 above are fixed,
rerun the P&L before drafting the client email.

## Client-conversation flags (not close blockers)

- **Working capital is −$42,537 (current ratio 0.44)** with $25,893 cash against $37,970 of
  credit-card balances and heavy debt service. This client is a textbook candidate for the
  18-week cash flow dashboard.
- $22,342 of business spend is running through the owner's personal AMEX (booked as shareholder
  loan) — flag for cleanliness and for the tax preparer.
- Interest expense is now ~$7.6K/mo and climbing with the second Shopify Capital draw —
  worth a financing-cost conversation.

## Not checkable via API — manual in QBO

- [ ] Bank & credit-card reconciliations through 6/30 (all accounts, incl. the two AMEX cards)
- [ ] Uncleared/stale checks on the bank recs
- [ ] Bank-feed "For review" queue emptied
