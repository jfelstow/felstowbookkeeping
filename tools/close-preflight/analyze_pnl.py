#!/usr/bin/env python3
"""Close Pre-Flight P&L anomaly analyzer.

Reads the JSON saved from the QuickBooks MCP profit_loss_quickbooks_account
tool (pulled for a range ending at the close month, e.g. Jan 1 - Jun 30) and
flags, for the close month vs. the prior months in the range:

  SPIKE          account is way above its prior-month average
  DROP           account is way below its prior-month average
  MISSING        recurring account (active in most prior months) posted $0
  NEW            account posted for the first time in the close month
  NEGATIVE       income/COGS/expense line with a negative balance
  UNCATEGORIZED  any "Uncategorized" / "Ask My Accountant" balance in range

Usage:
  python3 analyze_pnl.py <pnl_json_file> [--spike-pct 50] [--min-dollars 250]

Output: markdown to stdout, ready to paste into the pre-flight report.
"""

import argparse
import json
import sys
from statistics import mean

SECTION_KEYS = [
    ("incomeAccounts", "Income"),
    ("cogsAccounts", "COGS"),
    ("expenseAccounts", "Expenses"),
]

UNCAT_MARKERS = ("uncategorized", "ask my accountant", "ask accountant")


def is_leaf(name: str) -> bool:
    """Skip QBO subtotal/header rows like 'Total for 61000 ...' and bare parents."""
    return not name.startswith("Total for ")


def load_months(data: dict):
    """Return ordered list of (label, {section: {account: amount}})."""
    months = sorted(data.get("monthlyBreakdown", {}).items())
    out = []
    for label, body in months:
        sections = {}
        for key, title in SECTION_KEYS:
            accounts = body.get(key) or {}
            sections[title] = {
                name: amt
                for name, amt in accounts.items()
                if is_leaf(name) and isinstance(amt, (int, float))
            }
        out.append((label, sections, body))
    return out


def fmt(n: float) -> str:
    return f"-${abs(n):,.2f}" if n < 0 else f"${n:,.2f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pnl_json")
    ap.add_argument("--spike-pct", type=float, default=50.0,
                    help="flag when close month exceeds prior average by this %%")
    ap.add_argument("--min-dollars", type=float, default=250.0,
                    help="ignore variances smaller than this many dollars")
    args = ap.parse_args()

    with open(args.pnl_json) as f:
        data = json.load(f)

    months = load_months(data)
    if len(months) < 2:
        print("Need at least 2 months in the P&L range to compare.", file=sys.stderr)
        return 1

    *prior, close = months
    close_label, close_sections, close_body = close
    prior_labels = [m[0] for m in prior]

    print(f"## P&L anomaly scan — close month: {close_label}")
    print(f"Baseline: {len(prior)} prior month(s) ({prior_labels[0][:10]} … {prior_labels[-1][:10]})")
    print(f"Thresholds: ±{args.spike_pct:.0f}% vs prior average, minimum {fmt(args.min_dollars)} variance\n")

    # Headline
    pri_net = [m[2].get("netIncome") for m in prior if m[2].get("netIncome") is not None]
    close_net = close_body.get("netIncome")
    if close_net is not None and pri_net:
        print(f"**Net income {close_label[:10][:7]}: {fmt(close_net)}** "
              f"(prior-month avg {fmt(mean(pri_net))})\n")

    findings = []
    for title in [t for _, t in SECTION_KEYS]:
        close_accts = close_sections[title]
        all_names = set(close_accts)
        for _, sections, _ in prior:
            all_names |= set(sections[title])

        for name in sorted(all_names):
            history = [m[1][title].get(name, 0.0) for m in prior]
            now = close_accts.get(name, 0.0)
            avg = mean(history) if history else 0.0
            active_months = sum(1 for v in history if abs(v) >= 0.01)

            if any(marker in name.lower() for marker in UNCAT_MARKERS):
                total = now + sum(history)
                if abs(total) >= 0.01:
                    findings.append(("UNCATEGORIZED", title, name,
                                     f"{fmt(total)} sitting in an uncategorized bucket across the range"))
                continue

            if now < -0.01:
                findings.append(("NEGATIVE", title, name,
                                 f"negative balance {fmt(now)} in the close month — misposting or refund?"))

            variance = now - avg
            if abs(variance) < args.min_dollars:
                continue

            if active_months == 0 and abs(now) >= args.min_dollars:
                findings.append(("NEW", title, name,
                                 f"first activity in range: {fmt(now)} — new vendor/category or misposting?"))
            elif active_months >= max(2, round(0.6 * len(prior))) and abs(now) < 0.01 and abs(avg) >= args.min_dollars:
                findings.append(("MISSING", title, name,
                                 f"recurring (avg {fmt(avg)}/mo, {active_months}/{len(prior)} months) but $0 this month — missing bill/entry?"))
            elif avg > 0 and now > avg * (1 + args.spike_pct / 100):
                findings.append(("SPIKE", title, name,
                                 f"{fmt(now)} vs avg {fmt(avg)} (+{(now / avg - 1) * 100:,.0f}%)"))
            elif avg > 0 and now < avg * (1 - args.spike_pct / 100) and abs(now) >= 0.01:
                findings.append(("DROP", title, name,
                                 f"{fmt(now)} vs avg {fmt(avg)} ({(now / avg - 1) * 100:,.0f}%)"))

    order = {"UNCATEGORIZED": 0, "NEGATIVE": 1, "MISSING": 2, "NEW": 3, "SPIKE": 4, "DROP": 5}
    findings.sort(key=lambda x: (order[x[0]], x[1], x[2]))

    if not findings:
        print("No anomalies above thresholds. Clean scan.")
        return 0

    for flag, section, name, detail in findings:
        print(f"- **[{flag}]** ({section}) `{name}` — {detail}")
    print(f"\n{len(findings)} finding(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
