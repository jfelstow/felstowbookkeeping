---
name: client-email
description: Draft the plain-English monthly check-in email for a bookkeeping client after their close — the numbers that matter, what moved, one thing to watch, and an advisory hook when the data warrants it. Creates a Gmail draft for Jake to review and send. Use when asked to draft the monthly client email or client check-in.
---

# Monthly Client Check-In Email

Draft the email Jake sends each client when their books are closed. This is the retention
engine: it's what makes a flat monthly fee feel obviously worth it. Jake edits and sends —
**never send; only create a draft.**

## Step 1 — Gather the numbers

Prefer data already in hand: if a close pre-flight ran this session (or exists in
`reports/close-preflight/` for the month), reuse its data and findings. Otherwise pull via
the QuickBooks MCP: `company_info`, trailing-6-month P&L (monthly breakdown), balance sheet
as of month-end, A/R aging detail.

If the pre-flight has unresolved fix-first items, still draft — but add an internal
`> DRAFT NOTE` banner above the email (never inside it) saying which numbers may shift,
and say so in chat.

## Step 2 — Decide the story (before writing a word)

Every month has one headline. Find it: best month of the year? A one-time item distorting
the bottom line? A new revenue channel? A cash squeeze forming? The email is built around
that single story — everything else supports or gets cut.

## Step 3 — Write it

**Voice rules (Jake's brand is plain English):**
- 150–250 words. Short paragraphs. No accounting jargon — if an accrual matters, say
  "the annual bill landed all in one month," not "accrual."
- Address the owner by first name (from QBO records or the onboarding file).
- Lead with the verdict in the first sentence — the thing they'd want to know if they
  read nothing else.
- At most 3 numbers per paragraph. Round to whole dollars ("about $12K" beats "$11,932.84").
- Compare to something human: last month, the spring average, same month last year.
- Exactly **one thing to watch** — the forward-looking sentence that proves someone is
  actually reading their numbers.
- Never blame the client; never mention internal bookkeeping errors or fixes. What they
  see is a finished close.
- End with one concrete, answerable question or offer (a nudge on a late invoice, a
  20-minute call) — not "let me know if you have questions."

**Advisory hook (only when the data warrants):** if cash is tight (negative working
capital, rising debt service, < 6 weeks of runway), close with one sentence connecting the
pain to the weekly 18-week cash flow dashboard — an offer, not a pitch. One sentence, once.
Skip it entirely for healthy months.

**Structure:**
1. Verdict + headline number
2. What moved and why (the story)
3. One thing to watch
4. Housekeeping if any (late invoices, documents needed) — one line
5. The question/offer + sign-off ("— Jake")

## Step 4 — Deliver

1. Save to `reports/client-emails/YYYY-MM-<client-slug>.md` (subject line + body, plus any
   internal draft-note banner above the email).
2. Create a Gmail draft (`create_draft`) **on the bookkeeping connector — the one
   authenticated as jake.felstow@gmail.com** (see the email-routing rules in CLAUDE.md;
   never draft client mail from the Provision and Company account). Subject
   `<Client> — <Month> books + <hook>`, plain-text body only (no HTML — personal beats
   polished). Leave `to` empty unless the client's email is on file or provided; Jake
   fills it in when he reviews.
3. In chat: give the one-line story chosen, and note anything Jake should verify before
   sending.
