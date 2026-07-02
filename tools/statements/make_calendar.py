#!/usr/bin/env python3
"""Generate a recurring statement-pickup calendar from the statement registry.

Reads registry.csv and emits statement-calendar.ics: one monthly recurring
event per (client, institution, available_day) group, listing every account
to grab that day, with a same-morning reminder alarm.

Rows with available_day = TBD are skipped and reported to stderr so the
gaps are visible — fill them in as you confirm each account's cycle.

Usage:
  python3 make_calendar.py [registry.csv] [-o statement-calendar.ics]

Import the .ics into Google Calendar once (Settings -> Import & Export).
Re-running after registry edits regenerates the file; re-importing updates
events because UIDs are stable per group.
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

CAL_HEADER = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Felstow Bookkeeping//Statement Calendar//EN
CALSCALE:GREGORIAN
X-WR-CALNAME:Client Statements
"""


def slug(text: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in text.lower()).strip("-")


def make_event(client: str, institution: str, day: int, accounts: list) -> str:
    uid = f"{slug(client)}-{slug(institution)}-d{day}@felstowbookkeeping"
    acct_list = "\\n".join(f"- {a['account']} ({a['method']})" for a in accounts)
    notes = "\\n".join(f"- {a['account']}: {a['notes']}" for a in accounts if a["notes"])
    description = f"Grab statements for {client} / {institution}:\\n{acct_list}"
    if notes:
        description += f"\\n\\nNotes:\\n{notes}"
    # Anchor DTSTART in a past month that contains every valid day (Jan has 31).
    start = f"202601{day:02d}"
    return (
        "BEGIN:VEVENT\n"
        f"UID:{uid}\n"
        f"DTSTAMP:20260101T000000Z\n"
        f"DTSTART;VALUE=DATE:{start}\n"
        f"RRULE:FREQ=MONTHLY;BYMONTHDAY={day}\n"
        f"SUMMARY:📄 Statements: {client} — {institution}\n"
        f"DESCRIPTION:{description}\n"
        "BEGIN:VALARM\n"
        "TRIGGER:PT9H\n"
        "ACTION:DISPLAY\n"
        f"DESCRIPTION:Grab {institution} statements for {client}\n"
        "END:VALARM\n"
        "END:VEVENT\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("registry", nargs="?", default=str(Path(__file__).parent / "registry.csv"))
    ap.add_argument("-o", "--output", default=str(Path(__file__).parent / "statement-calendar.ics"))
    args = ap.parse_args()

    groups = defaultdict(list)
    skipped = []
    with open(args.registry, newline="") as f:
        for row in csv.DictReader(f):
            day = row["available_day"].strip()
            if not day.isdigit() or not 1 <= int(day) <= 31:
                skipped.append(row)
                continue
            groups[(row["client"].strip(), row["institution"].strip(), int(day))].append(row)

    body = CAL_HEADER
    for (client, institution, day), accounts in sorted(groups.items()):
        body += make_event(client, institution, day, accounts)
    body += "END:VCALENDAR\n"

    Path(args.output).write_text(body)
    print(f"Wrote {args.output}: {len(groups)} recurring event(s) covering "
          f"{sum(len(v) for v in groups.values())} account(s).")

    if skipped:
        print(f"\nSkipped {len(skipped)} account(s) with unknown cycle day (available_day=TBD):",
              file=sys.stderr)
        for row in skipped:
            print(f"  - {row['client']} / {row['account']}: {row['notes']}", file=sys.stderr)
        print("Fill in available_day in registry.csv and rerun.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
