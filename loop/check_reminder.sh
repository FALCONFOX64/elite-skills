#!/bin/bash
# Surface the 7-day completion reminder if it is armed and unacknowledged.
# Wired into Claude Code's SessionStart hook so the reminder persists across
# sessions until loop/acknowledge.sh is run. Silent (exit 0) otherwise.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMINDER="$REPO/state/reminder.json"

if [ -f "$REMINDER" ] && jq -e '.active == true' "$REMINDER" >/dev/null 2>&1; then
  echo "⏰ REMINDER: $(jq -r '.message' "$REMINDER")"
  echo "   (acknowledge with: $REPO/loop/acknowledge.sh)"
fi
