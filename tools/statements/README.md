# Statement tracking & chasing

Getting bank/credit-card statements every month, per client, without it living in
Jake's head. Three tiers — use the highest one each account supports:

1. **Auto-fetch (best, costs money):** Hubdoc or Dext log into bank portals with
   bank-grade connections and pull PDFs automatically into a per-client folder.
   Worth it once client count makes portal-hopping painful. Also check QBO itself —
   some bank feeds now surface actual statements. Direct DIY scraping of bank
   logins is deliberately NOT part of this tooling (credentials/MFA/ToS risk).
2. **Email-delivery (free):** switch each account's delivery preference to email
   where offered, or have clients auto-forward. The `/statement-chase` skill
   watches the bookkeeping Gmail and labels arrivals `Statements/<Client>`.
3. **Manual with a system (this folder):** a registry of every account and its
   cycle, recurring calendar reminders, and a monthly chase run.

## Files

- `registry.csv` — the source of truth: every client account, when its statement
  becomes available (`available_day`, day of month), and how it's retrieved
  (`portal` / `client-sends` / `email-delivery` / `hubdoc` / `TBD`).
- `make_calendar.py` — generates `statement-calendar.ics` from the registry:
  one recurring monthly Google Calendar event per client+institution, with a
  reminder alarm. Import once (Google Calendar → Settings → Import & export);
  rerun + re-import after registry edits (stable UIDs update in place).
- `statement-calendar.ics` — the generated calendar (committed so it's grabbable
  from anywhere).

## Monthly rhythm

Calendar pings you on statement days → `/statement-chase` in Claude Code lists
what to grab, labels what already arrived in Gmail, and drafts nudges to clients
who send their own → grab, file, reconcile.

The registry is seeded from Fresh Dry Snacks' QBO chart of accounts (June 2026
balance sheet). Rows with `available_day=TBD` need the real cycle day read off
the last statement; zero-balance accounts need an open/closed check.
