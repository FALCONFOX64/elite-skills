#!/usr/bin/env python3
"""Aggregate all cycle audit logs + memory store into audit-logs/summary-report.json.

Idempotent: safe to re-run at any time; the report is rebuilt from source data.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT_DIR = ROOT / "audit-logs"
MEMORY_PATH = ROOT / "memory" / "store.json"
OUT_PATH = AUDIT_DIR / "summary-report.json"


def main() -> None:
    cycles = []
    for path in sorted(AUDIT_DIR.glob("cycle-*.json"),
                       key=lambda p: int(re.match(r"cycle-(\d+)-", p.name).group(1))):
        cycles.append(json.loads(path.read_text()))

    memory = json.loads(MEMORY_PATH.read_text()) if MEMORY_PATH.exists() else {"skills": {}}

    all_results = [r for c in cycles for r in c.get("results", [])]
    improved = [r for r in all_results if r["status"] == "improved"]
    reverted = [r for r in all_results if r["status"] == "reverted-regression"]
    failed = [r for r in all_results if r["status"] == "failed"]

    per_skill = {}
    for name, mem in memory.get("skills", {}).items():
        trend = mem.get("cumulative_trend", {})
        per_skill[name] = {
            "first_score": trend.get("first_score"),
            "latest_score": trend.get("latest_score"),
            "net_delta": trend.get("net_delta"),
            "improvements_applied": trend.get("improvements", 0),
            "regressions_reverted": trend.get("regressions_reverted", 0),
            "failures": trend.get("failures", 0),
            "dimensions_covered": sorted(mem.get("dimensions_covered", {}).keys()),
        }

    report = {
        "report_type": "7-day-summary",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "schedule": cycles[0]["schedule"] if cycles else None,
        "cycles_executed": len(cycles),
        "first_cycle_at": cycles[0]["timestamp"] if cycles else None,
        "last_cycle_at": cycles[-1]["timestamp"] if cycles else None,
        "totals": {
            "skill_tasks_run": len(all_results),
            "improvements_applied": len(improved),
            "regressions_reverted": len(reverted),
            "failures": len(failed),
            "aggregate_score_delta": round(sum(r["delta"] for r in improved), 2),
        },
        "per_skill": per_skill,
        "errors": [e for c in cycles for e in c.get("errors", [])],
        "next_steps": ("Review per-skill trends above, acknowledge the session "
                       "reminder via loop/acknowledge.sh, and start a new schedule "
                       "with: python3 loop/run_cycle.py --start"),
    }

    OUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    print(f"summary written: {OUT_PATH} ({len(cycles)} cycles aggregated)")


if __name__ == "__main__":
    main()
