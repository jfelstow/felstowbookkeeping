---
name: statement-chase
description: Monthly statement round-up — from the statement registry, list which client bank/card statements are available to grab now, check Gmail for statements that already arrived, and draft chase emails for clients who send their own. Use when asked what statements to grab, to chase statements, or to prep for reconciliations.
---

# Statement Chase

Answer one question: **which statements can Jake grab or chase right now** so
reconciliations aren't waiting on documents. Runs any time; most useful in the
first week of the month.

## Step 1 — Read the registry

`tools/statements/registry.csv` — one row per account:
`client, account, institution, type, available_day, method, notes`

`method` values: `portal` (Jake logs in), `client-sends` (chase the client),
`email-delivery` (bank emails it), `hubdoc`/`feed` (auto-fetched), `TBD`.

An account is **due** this run if `available_day` ≤ today's day-of-month
(i.e., this month's statement should exist by now). `TBD` rows are always
listed separately as "cycle unknown — confirm."

## Step 2 — Check what already arrived (Gmail, bookkeeping account)

On the connector authenticated as jake.felstow@gmail.com (see CLAUDE.md routing):

- Search this month for statement traffic, e.g.
  `newer_than:31d (statement OR "statement is ready" OR "eStatement")` plus
  searches for each institution name and each client-sends client's email.
- Label hits `Statements/<Client>` (create labels as needed) so the inbox
  becomes the filing record.
- Anything found counts as **arrived** for its account this month.

## Step 3 — Draft the chases

For every `client-sends` account that is due but not arrived: draft (never send)
a short, friendly nudge from the bookkeeping account — one email per client
covering all their missing accounts, plain text, one line per account, no
attachment lecture. Subject: `<Month> statements — <account list>`.

## Step 4 — Report

Reply in chat with three short lists:

1. **Grab now** — portal/email accounts due this month (with institution and notes)
2. **Chasing** — client-sends accounts, with drafts created
3. **Unknown cycle** — TBD rows to confirm (and any zero-balance accounts to
   verify open/closed so the registry stays honest)

If the registry changed (new client, confirmed cycle days), remind Jake to rerun
`python3 tools/statements/make_calendar.py` and re-import the .ics so calendar
reminders stay in sync.
