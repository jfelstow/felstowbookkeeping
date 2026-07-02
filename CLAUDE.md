# Felstow Bookkeeping & Consulting — working conventions

Jake Felstow's practice repo: the public site (root `*.html`), automation tools
(`tools/`), Claude skills (`.claude/skills/`), and generated reports (`reports/`).
The automation roadmap lives in `AUTOMATION-IDEAS.md`.

## Email routing (applies to every Gmail draft, always)

Jake has two email identities. Route by business, never mix them:

- **Felstow Bookkeeping & Consulting** (clients, closes, monthly check-ins, leads,
  the Kit, the Subscription Audit) → draft from **jake.felstow@gmail.com**
- **Provision and Company** → draft from **jake@provisionandcompany.com**

Each identity is its own Gmail connector; the connector authenticated as
jake.felstow@gmail.com is the bookkeeping one. If the Provision and Company
connector is not attached to the session and a Provision email is needed, say so
and stop — do not draft Provision mail from the bookkeeping account (or vice versa).

## Email ground rules

- **Draft only, never send.** Jake reviews and sends everything himself.
- Client-facing drafts follow the voice rules in `.claude/skills/client-email/SKILL.md`
  (plain English, verdict first, one watch item, no internal bookkeeping errors mentioned).

## Monthly rhythm per client

1. `/close-preflight` — pull QBO data, scan, write the fix-first report
2. Jake fixes the books in QBO
3. `/client-email` — draft the check-in from the refreshed numbers
