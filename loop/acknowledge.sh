#!/bin/bash
# Acknowledge the 7-day completion reminder so it stops surfacing at session start.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMINDER="$REPO/state/reminder.json"

if [ ! -f "$REMINDER" ]; then
  echo "No reminder is armed."
  exit 0
fi

tmp="$(mktemp)"
jq '.active = false | .acknowledged_at = (now | todate)' "$REMINDER" > "$tmp"
mv "$tmp" "$REMINDER"
echo "Reminder acknowledged. Review: $REPO/audit-logs/summary-report.json"
echo "Start a new schedule with: python3 $REPO/loop/run_cycle.py --start"
