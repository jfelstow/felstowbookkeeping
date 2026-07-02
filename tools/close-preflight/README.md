# Close Pre-Flight

Item #1 from [AUTOMATION-IDEAS.md](../../AUTOMATION-IDEAS.md): a per-client "close readiness"
brief generated *before* opening QBO each month.

## How to run

In a Claude Code session with the QuickBooks connector attached to the client's company:

```
/close-preflight
```

That skill (defined in `.claude/skills/close-preflight/SKILL.md`) pulls the trailing-six-month
P&L, close-date balance sheet, and A/R + A/P aging detail, runs the anomaly scan below, applies
the balance-sheet checklist, and writes the report to `reports/close-preflight/`.

To close a specific month: `/close-preflight May 2026`.
To switch clients, switch the QuickBooks connection to that client's company first.

## What's in here

- `analyze_pnl.py` — deterministic P&L anomaly scanner. Takes the JSON saved from the
  `profit_loss_quickbooks_account` MCP tool and flags, for the close month vs. prior months:
  spikes, drops, missing recurring bills, first-time accounts, negative balances, and
  uncategorized buckets. Thresholds: `--spike-pct` (default 50) and `--min-dollars`
  (default 250).

## What it can't see (stays manual in QBO)

Reconciliation status, uncleared checks, and the bank-feed review queue aren't exposed by the
QuickBooks reporting tools — the generated report ends with a manual checklist for those.

## Pilot

First live run: `reports/close-preflight/2026-06-fresh-dry-snacks.md` (June 2026,
22 raw findings → 5 fix-first items, 1 fiscal-year-end catch, 1 to-the-penny tie-out).
