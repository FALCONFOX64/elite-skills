#!/usr/bin/env python3
"""CI validation gate — the required check behind PR auto-merge.

Validates:
  1. Every audit log conforms to schemas/audit-log.schema.json
  2. memory/store.json conforms to schemas/memory.schema.json
  3. Every skill retains intact YAML frontmatter with name + description
  4. state/loop-state.json (if present) is well-formed JSON

Uses `jsonschema` when available (installed in CI); falls back to structural
checks locally so the script never passes vacuously.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILURES = []


def fail(msg: str) -> None:
    FAILURES.append(msg)
    print(f"FAIL: {msg}")


def check_schema(instance, schema_path: Path, label: str) -> None:
    schema = json.loads(schema_path.read_text())
    try:
        import jsonschema
        try:
            jsonschema.validate(instance, schema)
        except jsonschema.ValidationError as exc:
            fail(f"{label}: schema violation — {exc.message}")
    except ImportError:
        # Structural fallback: required top-level keys must exist.
        for key in schema.get("required", []):
            if key not in instance:
                fail(f"{label}: missing required key '{key}'")


def main() -> int:
    audit_schema = ROOT / "schemas" / "audit-log.schema.json"
    memory_schema = ROOT / "schemas" / "memory.schema.json"

    for path in sorted((ROOT / "audit-logs").glob("cycle-*.json")):
        if not re.match(r"cycle-\d+-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}\.json", path.name):
            fail(f"{path.name}: filename does not match cycle-{{n}}-YYYY-MM-DD-HH-MM.json")
        try:
            check_schema(json.loads(path.read_text()), audit_schema, path.name)
        except json.JSONDecodeError as exc:
            fail(f"{path.name}: invalid JSON — {exc}")

    mem_path = ROOT / "memory" / "store.json"
    if mem_path.exists():
        try:
            check_schema(json.loads(mem_path.read_text()), memory_schema, "memory/store.json")
        except json.JSONDecodeError as exc:
            fail(f"memory/store.json: invalid JSON — {exc}")

    state_path = ROOT / "state" / "loop-state.json"
    if state_path.exists():
        try:
            json.loads(state_path.read_text())
        except json.JSONDecodeError as exc:
            fail(f"state/loop-state.json: invalid JSON — {exc}")

    for skill_md in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = skill_md.read_text()
        fm = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not fm:
            fail(f"{skill_md.parent.name}/SKILL.md: missing YAML frontmatter")
            continue
        for field in ("name:", "description:"):
            if field not in fm.group(1):
                fail(f"{skill_md.parent.name}/SKILL.md: frontmatter missing '{field}'")
        if len(text) < 500:
            fail(f"{skill_md.parent.name}/SKILL.md: suspiciously short ({len(text)} chars)")

    if FAILURES:
        print(f"\nvalidation failed: {len(FAILURES)} issue(s)")
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
