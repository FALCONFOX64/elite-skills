#!/bin/bash
# launchd entrypoint for running the loop locally on macOS (alternative to
# GitHub Actions). Uses the local `claude` login — no API key required.
set -uo pipefail
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="$REPO/state/local-runner.log"
mkdir -p "$REPO/state"

{
  echo "=== local run $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  python3 "$REPO/loop/run_cycle.py"
  echo "=== exit $? ==="
} >> "$LOG" 2>&1
