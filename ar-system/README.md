# AR Command Center

A managed accounts receivable system for bookkeeping clients. QuickBooks Online stays the
system of record — invoices, payments, and aging live there. This layer adds the thing QBO
doesn't have: a disciplined, escalating collections workflow that runs mostly on its own,
with you (the bookkeeper) approving every outbound touch.

First client: a wholesale food producer selling to school districts starting fall 2026.
The policy ships with a `school_district` profile tuned for how district AP offices
actually pay (POs, net 30–45, shared AP inboxes, board-cycle check runs).

## Why not just QuickBooks?

QBO already does — use these, don't rebuild them:

- **Invoicing, payment recording, deposits, A/R aging reports** — the ledger.
- **Automatic invoice reminders** (Settings → Account and Settings → Sales → Reminders):
  up to 3 generic nudges before/on/after the due date. Turn them ON as a safety net.
- **QuickBooks Payments** — pay-now links with ACH. Turn on ACH; districts won't pay by card.
- **Late fee settings** — configure even if you rarely enforce; it changes payer behavior.

What QBO can't do — this is the gap this system fills:

- **Escalation.** QBO sends the same polite template forever. Real collections is a ladder:
  courtesy → reminder → firm → escalate to a human with authority → credit hold.
- **School-district reality.** Generic auto-reminders land in a shared AP inbox and die.
  Districts need the PO number on everything, invoices submitted the way *they* require
  (portal, email alias, or paper), and follow-ups addressed to a named AP clerk.
- **Promise-to-pay tracking.** "Check run is on the 15th" needs a follow-up date and a
  broken-promise flag, not a memo field nobody reads.
- **A collections log.** Who was contacted, when, what they said, what happens next.
- **The bookkeeper view.** When this runs for multiple clients, you need one Monday digest
  across all of them, not five QBO logins.

## Architecture

```
QuickBooks Online (system of record)
        │  read: A/R aging, open invoices, payments   (QuickBooks MCP connector)
        ▼
/ar-review skill (Claude Code, this repo)
        │  classifies every open invoice into a dunning stage (dunning-policy.json)
        │  drafts stage-appropriate emails (templates/) as Gmail DRAFTS — never sends
        │  updates the collections log, tracks promises-to-pay
        ▼
Monday AR Digest (local report)  ──►  you review, tweak, hit send, make the calls
```

**Autonomy model:** the machine does 100% of the watching, aging math, drafting, and
logging. A human does 100% of the sending and phoning. That's the product: clients aren't
buying software, they're buying "a professional runs my receivables."

## Files

| Path | Committed? | What it is |
|---|---|---|
| `dunning-policy.json` | yes | The escalation ladder: stages, triggers, actions, per-profile timing |
| `templates/` | yes | Email templates per stage, with school-district variants |
| `clients.example.json` | yes | Structure for per-client config |
| `clients.json` | **no — gitignored** | Real client data: customers, AP contacts, PO rules, notes |
| `log/` | **no — gitignored** | Collections log + promise-to-pay tracker, one file per client |
| `reports/` | **no — gitignored** | Generated Monday digests |
| `../.claude/skills/ar-review/` | yes | The skill that runs the whole routine |

This repo is a public website. Nothing identifying a client, customer, amount, or contact
ever gets committed. Local-only data survives on your machine; in cloud sessions,
re-seed `clients.json` from your local copy or keep it in the session environment.

## One-time QBO setup per client (do this before fall)

1. **Terms**: create/confirm `Net 30` (and `Net 45` if a district demands it). Set the
   default per customer, not per invoice.
2. **Custom field "PO Number"** on invoices, set to show on print/email. A district invoice
   without a PO number doesn't get paid — it gets ignored.
3. **Automatic reminders ON** (3-touch generic schedule) as the backstop under this system.
4. **QuickBooks Payments** with ACH enabled; put the pay link on every invoice.
5. **Late fees** configured (e.g., 1.5%/mo after 15 days grace) — even if waived for
   districts, it anchors the conversation with commercial accounts.
6. Per district customer record: AP contact name + direct email, invoice submission method
   (portal / AP inbox / mail), PO required (almost always yes), check-run schedule if known.

## The weekly routine (you, ~15 minutes per client)

1. Open this repo in Claude Code and run `/ar-review`.
2. Read the digest: what's current, what moved stages, what's flagged.
3. Open the Gmail drafts it prepared. Edit tone if needed. Send.
4. Make any phone calls the digest says are due (stage 4+ is always a call, not an email).
5. Done. The log and promise tracker are already updated.

## Escalation ladder (summary — the machine-readable version is dunning-policy.json)

| Stage | Standard wholesale | School district | Action |
|---|---|---|---|
| 0 · Sent | invoice day | invoice day + PO ref | Invoice + cover note via required channel |
| 1 · Courtesy | due − 5 days | due − 7 days | Friendly heads-up, pay link |
| 2 · Past due | due + 3 | due + 7 | Reminder, restate PO + due date |
| 3 · Firm | due + 14 | due + 21 | Firm notice, ask for a pay date, get a promise |
| 4 · Escalate | due + 30 | due + 35 | **Phone call** + email to AP supervisor / business manager, statement attached |
| 5 · Final | due + 45 | due + 60 | Final notice: credit hold on future orders, owner looped in |

Broken promise-to-pay: jump straight to the next stage and flag for a call.

## Roadmap

- [ ] Foundation: policy, templates, skill, log format *(this commit)*
- [ ] Fresh client onboarded end-to-end through one full billing cycle
- [ ] Scheduled Monday trigger so the review runs before you open your laptop
- [ ] Multi-client digest (one report across all AR clients)
- [ ] Client-facing AR health page (aging trend, DSO) — same encrypted-static pattern as the Cash Flow Dashboard
- [ ] Productize as a kit for other bookkeepers (sibling product to the Cash Flow Dashboard Kit)
