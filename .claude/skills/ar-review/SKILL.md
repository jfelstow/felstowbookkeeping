---
name: ar-review
description: Run the weekly AR Command Center review — pull live A/R from QuickBooks, classify every open invoice against the dunning policy, draft (never send) collection emails, update the collections log, and produce the Monday AR Digest. Use when the user says "/ar-review", "run the AR review", "check receivables", or "who owes us money".
---

# AR Command Center — weekly review

You are running the collections review for Felstow Bookkeeping's AR clients. Read
`ar-system/README.md` for architecture if this is your first run in a session.

**Prime directive: NEVER send an email or contact a customer. You draft; Jake sends.**

## Steps

### 1. Load config
- Read `ar-system/dunning-policy.json` and `ar-system/clients.json`.
- If `clients.json` is missing (fresh cloud session), say so and fall back to
  `clients.example.json` structure with whatever the user provides; offer to rebuild it.

### 2. Pull live data (QuickBooks MCP)
For the connected client:
- `qbo_accounting_get_ar_aging_summary` and `qbo_accounting_get_ar_aging_detail` — the aging picture.
- `qbo_sales_get_invoices` (last 120 days, order by DueDate) — open balances, due dates, customers, line detail.
- If the QuickBooks connector needs re-authorization, stop and tell Jake to re-connect it
  in claude.ai connector settings — don't guess at balances from stale logs.

### 3. Reconcile against the log
- Read the client's log file in `ar-system/log/` (create `ar-system/log/<client-id>.md` if missing).
- Invoices in the log that now show PAID in QBO: mark collected, note days-to-pay.
- Promise-to-pay dates that passed without payment: mark BROKEN PROMISE.

### 4. Classify every open invoice
- Match the QBO customer to a profile via `customer_overrides` (default: client's `default_profile`).
- Compute days relative to due date; find the highest stage whose `trigger_days` has passed.
- Skip stages already actioned per the log (`one_touch_per_invoice_per_run`, no repeats of the same stage).
- Apply global rules: broken promise → advance a stage + flag call; disputes frozen;
  balances under the small-balance floor roll to monthly statement.

### 5. Draft the touches
For each invoice due a touch this run:
- Fill the stage's template from `ar-system/templates/` with real values (invoice #, amounts,
  PO, contact name, pay link if known). Match the client's voice and signature from config.
- Create a **Gmail draft** (`mcp__Gmail__create_draft`) addressed to the right contact.
  If Gmail is unavailable, write the ready-to-paste email into the digest instead.
- Stage 4+: the deliverable is a call brief (who to call, number, script points, ask) — the
  email is only the paper trail to send after the call.

### 6. Update the log
Append to `ar-system/log/<client-id>.md` — one dated entry per invoice per action:
`| date | invoice | customer | balance | days past due | stage | action taken | promise/next date |`

### 7. Produce the Monday AR Digest
Write `ar-system/reports/<date>-<client-id>.md` and give Jake the digest in chat:
- **Headline numbers**: total AR, current vs overdue, change since last run.
- **Collected since last run** (wins first).
- **Action queue**: each draft created, one line each — customer, amount, stage, what the touch says.
- **Calls to make**: stage 4+ and broken promises, with phone numbers.
- **Watch list**: current invoices approaching due.
- **Flags**: disputes, missing AP contact info, invoices missing PO numbers for district customers.
- End with: what Jake needs to do (review drafts → send; make N calls) — nothing else.

## Guardrails
- `ar-system/clients.json`, `log/`, and `reports/` are gitignored. Never commit, publish, or
  include real customer names, amounts, or contacts in anything committed to this public repo.
- Never create, modify, send, or delete invoices in QBO during a review — read-only.
- Tone check on drafts: firm is fine, hostile never; school districts always get the
  process-failure-assumption tone, not the deadbeat-assumption tone.
