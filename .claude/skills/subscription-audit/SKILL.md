---
name: subscription-audit
description: >
  Run the Felstow Subscription & Spend Audit: take 3–6 months of business bank
  and credit-card statements (CSV or PDF), detect every recurring charge,
  classify each as keep / review / cancel, flag price creep and duplicate
  tools, and produce a polished visual HTML report with charts, savings math,
  and where-to-cancel instructions. Use whenever the user submits bank
  statements for a subscription audit, asks to "run the audit", "find
  subscriptions to cancel", or mentions the Subscription & Spend Audit.
---

# Subscription & Spend Audit

You are producing the paid deliverable for Felstow Bookkeeping & Consulting's
$149 Subscription & Spend Audit ("Rocket Money for your business"). The client
sent 3–6 months of statements; the promise is a ranked report of every
recurring charge — what to keep, what to question, what to cancel, where to
cancel it, and exactly how much they'll save. The deliverable must look like a
$149 product: the visual report template in `assets/report-template.html` is
the required output format.

## Workflow

### 1. Intake and parse statements

- Accept CSV (preferred) and PDF statements. For PDFs, extract the
  transaction tables (date, description, amount). For CSVs, identify the
  date / description / amount columns — bank exports vary, inspect the header.
- Write a small script (Python or Node) to normalize all files into one
  transaction list: `{date, description, amount, account}`. Do the analysis
  in code, not by eyeball — statements routinely have 500+ rows.
- Note the exact date window covered and every account analyzed; both appear
  in the report header. If the window is under 3 months or an account looks
  incomplete (a gap month), tell the user before proceeding — detection
  quality depends on it.
- Only debits/charges matter. Exclude transfers between the client's own
  accounts, payroll, taxes, and loan payments — those are not subscriptions.

### 2. Detect recurring charges

Group transactions by normalized merchant (strip store numbers, city/state
suffixes, `SP*`/`SQ*`/`PAYPAL*` prefixes — keep the payee after the prefix).
A merchant group is **recurring** when charges repeat at a regular interval:

| Cadence | Interval between charges | Minimum occurrences |
|---|---|---|
| weekly | 6–8 days | 4 |
| monthly | 27–33 days | 2 (3+ = high confidence) |
| quarterly | 85–100 days | 2 |
| annual | one charge, merchant is a known subscription vendor | 1 (flag as low confidence) |

- Amounts may vary ±20% (usage-based SaaS, per-seat billing). Same merchant,
  wildly different amounts (e.g. Amazon) = purchases, not a subscription —
  exclude unless the amount repeats exactly.
- A single charge from a known subscription vendor (see
  `references/methodology.md`) is likely an annual renewal — include it,
  marked low confidence, and say so in its reason.
- Record for each: merchant, category, cadence, current amount, first/last
  seen, occurrence count.

### 3. Classify with judgment — keep / review / cancel

Apply the heuristics in `references/methodology.md` (read it now), but the
final call on each charge is judgment, not rules. Every classification needs
a `reason` written in plain owner-facing language — one or two sentences,
specific to this business, never boilerplate. For every **review** item also
write `reviewQuestion`: the single question the owner must answer before the
next renewal (e.g. "Who logged into this in the last 30 days?").

Bias: the audit's value is found money, but a wrong cancel destroys trust.
When genuinely uncertain between cancel and review, choose review — the
walkthrough call resolves it.

### 4. Flag price creep and duplicates

- **Price creep**: same merchant's regular amount increased ≥5% inside the
  window (ignore usage-based variance — creep is a step change that then
  repeats). Record `priceCreep: {from, to, sinceMonth}`.
- **Duplicates**: two detected tools in the same job category (see the
  overlap map in `references/methodology.md`). Set `duplicateOf` on the one
  you'd cut, pointing at the one you'd keep.

### 5. Find where to cancel

Every **cancel** item requires `cancelUrl` + `cancelInstructions` (the actual
account page and click path, not "contact support"). Use the directory in
`references/methodology.md` first; for merchants not listed, search the web
for the current cancellation page. Review items get the same fields when
known. If a merchant can only be canceled by phone/email, say exactly that
with the number/address.

### 6. Build the report

1. Copy `assets/report-template.html` to the working output (e.g.
   `audit-report-<client>-<YYYY-MM>.html`).
2. Fill in **only** the `AUDIT_DATA` object between the marked comment lines
   — the schema is documented inline there. Everything else (KPI tiles, donut,
   bar chart, trend line, shortlists, flags, sortable appendix) renders
   itself from that object. Do not restyle or restructure the template.
3. Include `monthlyTotals` (total recurring spend per statement month) — it
   enables the trend chart, which is where price creep becomes visible.
4. Compute nothing by hand that the template computes (run-rates, savings,
   percentages) — supply raw per-charge data and let it render.
5. **Verify before delivering**: open the file (or screenshot it with the
   pre-installed browser) and check: no `undefined`/`NaN` anywhere, donut
   percentages sum sensibly, every cancel card has a working where-to-cancel
   line, merchant names not truncated misleadingly, and the dark-mode render
   is legible if you can check it.

### 7. Deliver

- Send the HTML report as the primary deliverable.
- Offer the companion spreadsheet (the full charge table as .xlsx/CSV) —
  the service promises "the full sortable spreadsheet behind it."
- Summarize in chat: total run-rate, the headline savings number, and the
  top 3 recommended cuts — the owner should get the punchline without
  opening anything.

## Quality bar (check every audit against this)

- [ ] Every statement month is accounted for; gaps disclosed to the user
- [ ] Every recurring charge appears exactly once (no duplicate merchant rows)
- [ ] Savings math: cancel-list annual savings = sum of those charges'
      annualized costs — spot-check two by hand
- [ ] Every cancel has a real cancellation path; no "contact support"
- [ ] Every reason is specific to this business — a reader can tell it wasn't
      copy-pasted
- [ ] Nothing essential (payment processing, payroll, insurance, the
      business's own website hosting) is on the cancel list
- [ ] Report opens clean: no NaN/undefined, charts render, appendix sorts
