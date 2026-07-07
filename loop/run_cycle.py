#!/usr/bin/env python3
"""Autonomous Elite Skills improvement loop — executes exactly one cycle per invocation.

Designed to be fired hourly by a scheduler (GitHub Actions cron or launchd).
All state lives in version-controlled JSON files, so every run is idempotent:
re-invoking within the same cycle window, or while a previous cycle's PR is
still open, is a safe no-op.

Flow per cycle:
  1. Guard: active schedule? window elapsed? previous PR merged?
  2. Branch: skill-improvement/cycle-{NNN}-{timestamp}
  3. Per elite skill (max 3 attempts each):
       score before -> pick least-recently-improved dimension from memory ->
       generate improved SKILL.md -> sanity-check -> score after ->
       commit (feat) or revert on regression
  4. Persist memory store + audit log, commit (chore)
  5. Push, open PR from template, enable auto-merge
  6. On day 7 / cycle 168: generate summary report, arm the session reminder
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
AUDIT_DIR = ROOT / "audit-logs"
MEMORY_PATH = ROOT / "memory" / "store.json"
STATE_PATH = ROOT / "state" / "loop-state.json"
REMINDER_PATH = ROOT / "state" / "reminder.json"
PR_TEMPLATE = ROOT / "templates" / "pr-body.md"

MODEL = os.environ.get("ELITE_LOOP_MODEL", "claude-sonnet-5")
TOTAL_CYCLES = int(os.environ.get("ELITE_LOOP_TOTAL_CYCLES", "168"))
PERIOD_DAYS = int(os.environ.get("ELITE_LOOP_PERIOD_DAYS", "7"))
MAX_RETRIES = int(os.environ.get("ELITE_LOOP_MAX_RETRIES", "3"))
CLAUDE_TIMEOUT = int(os.environ.get("ELITE_LOOP_CLAUDE_TIMEOUT", "600"))
SKILL_FILTER = os.environ.get("ELITE_LOOP_SKILL_FILTER", "")  # comma-separated allowlist, for testing
MIN_CYCLE_GAP_MIN = 45  # idempotency window: hourly cron with jitter tolerance

# Improvement dimensions rotated per skill via memory, so consecutive cycles
# never repeat the same action on the same skill.
DIMENSIONS = [
    "currency",        # refresh tool/practice references to what's current
    "clarity",         # tighten wording, remove ambiguity and filler
    "actionability",   # convert abstract advice into concrete steps/commands
    "coverage",        # fill gaps in scenarios the skill should handle
    "examples",        # add or sharpen worked examples
    "anti-patterns",   # expand the anti-pattern catalogue
    "structure",       # improve organization, headings, scannability
]


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str) -> None:
    print(f"[{iso(now())}] {msg}", flush=True)


def sh(*cmd: str, check: bool = True, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, check=check, timeout=timeout,
                          capture_output=True, text=True)


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text())
    return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n")


# ---------------------------------------------------------------- LLM calls

def claude(prompt: str) -> str:
    """Single-shot claude CLI call. Uses local auth or ANTHROPIC_API_KEY in CI."""
    proc = subprocess.run(
        ["claude", "-p", prompt, "--model", MODEL],
        cwd=ROOT, capture_output=True, text=True, timeout=CLAUDE_TIMEOUT,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed ({proc.returncode}): {proc.stderr[:500]}")
    return proc.stdout.strip()


JUDGE_PROMPT = """You are a strict evaluator of Claude Code skill definitions.
Score the following SKILL.md on five dimensions, each 0-20 (total 0-100):
clarity, actionability, currency, coverage, structure.
Be consistent and conservative; reserve 18-20 for genuinely exceptional work.

Respond with ONLY a JSON object, no prose, no code fences:
{{"clarity": n, "actionability": n, "currency": n, "coverage": n, "structure": n, "total": n, "rationale": "one sentence"}}

SKILL.md to evaluate:
<<<SKILL
{skill_text}
SKILL>>>"""


def judge(skill_text: str) -> dict:
    raw = claude(JUDGE_PROMPT.format(skill_text=skill_text))
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"judge returned no JSON: {raw[:200]}")
    score = json.loads(match.group(0))
    for key in ("clarity", "actionability", "currency", "coverage", "structure", "total"):
        if not isinstance(score.get(key), (int, float)):
            raise ValueError(f"judge JSON missing numeric '{key}'")
    return score


IMPROVE_PROMPT = """You are improving a Claude Code skill definition (SKILL.md).

Target dimension for THIS revision: **{dimension}** — {dimension_hint}

Recent improvement actions already applied to this skill (do NOT repeat them):
{recent_actions}

Rules:
- Output the COMPLETE revised SKILL.md and NOTHING else — no commentary, no code fences around the whole document.
- Preserve the YAML frontmatter block (--- delimited) and keep its `name` and `description` fields intact; you may refine the description wording only if the {dimension} dimension demands it.
- Make focused, high-signal edits for the target dimension. Do not rewrite unrelated sections.
- Keep total length within 50%-150% of the original.

Current SKILL.md:
<<<SKILL
{skill_text}
SKILL>>>"""

DIMENSION_HINTS = {
    "currency": "update tool, framework, and practice references to what top practitioners use now",
    "clarity": "tighten wording, remove ambiguity, cut filler, make every sentence earn its place",
    "actionability": "convert abstract advice into concrete steps, commands, and checklists",
    "coverage": "fill gaps: scenarios, edge cases, or trigger phrases the skill should handle but doesn't",
    "examples": "add or sharpen short worked examples that show the persona's output standard",
    "anti-patterns": "expand the catalogue of mistakes to call out, each with the reason it fails",
    "structure": "improve organization, heading hierarchy, and scannability without losing content",
}


def improve(skill_text: str, dimension: str, recent_actions: list) -> str:
    recent = "\n".join(f"- {a}" for a in recent_actions) or "- (none yet)"
    out = claude(IMPROVE_PROMPT.format(
        dimension=dimension,
        dimension_hint=DIMENSION_HINTS[dimension],
        recent_actions=recent,
        skill_text=skill_text,
    ))
    # Strip a stray wrapping code fence if the model added one anyway.
    fenced = re.match(r"^```(?:markdown|md)?\n(.*)\n```$", out, re.DOTALL)
    if fenced:
        out = fenced.group(1)
    return out.strip() + "\n"


def sane(original: str, revised: str) -> bool:
    if not revised.startswith("---"):
        return False
    if revised.count("---") < 2:
        return False
    ratio = len(revised) / max(len(original), 1)
    return 0.5 <= ratio <= 1.5


# ---------------------------------------------------------------- discovery

def discover_elite_skills() -> list:
    """Elite tier = directory name prefixed 'elite-' or frontmatter 'tier: elite'."""
    found = []
    allow = {s.strip() for s in SKILL_FILTER.split(",") if s.strip()}
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        name = skill_md.parent.name
        head = skill_md.read_text()[:2000]
        if name.startswith("elite-") or re.search(r"^tier:\s*elite\s*$", head, re.M):
            if allow and name not in allow:
                continue
            found.append({"name": name, "path": skill_md})
    return found


# ------------------------------------------------------------------ memory

def default_memory() -> dict:
    return {"version": 1, "backend": "file-json", "updated_at": None, "skills": {}}


def skill_memory(store: dict, name: str) -> dict:
    return store["skills"].setdefault(name, {
        "category": name.replace("elite-", "").replace("-", " "),
        "history": [],
        "dimensions_covered": {},
        "cumulative_trend": {
            "first_score": None, "latest_score": None, "net_delta": 0,
            "improvements": 0, "regressions_reverted": 0, "failures": 0,
        },
    })


def pick_dimension(mem: dict) -> str:
    covered = mem["dimensions_covered"]
    return min(DIMENSIONS, key=lambda d: covered.get(d, 0))


def record_result(store: dict, name: str, entry: dict) -> None:
    mem = skill_memory(store, name)
    mem["history"].append(entry)
    trend = mem["cumulative_trend"]
    if entry["status"] == "improved":
        mem["dimensions_covered"][entry["dimension"]] = entry["cycle"]
        if trend["first_score"] is None:
            trend["first_score"] = entry["score_before"]
        trend["latest_score"] = entry["score_after"]
        trend["net_delta"] = round(trend["latest_score"] - trend["first_score"], 2)
        trend["improvements"] += 1
    elif entry["status"] in ("reverted-regression", "no-change"):
        mem["dimensions_covered"][entry["dimension"]] = entry["cycle"]
        if entry["status"] == "reverted-regression":
            trend["regressions_reverted"] += 1
    else:
        trend["failures"] += 1
    store["updated_at"] = iso(now())


# --------------------------------------------------------------------- git

def git_preflight() -> None:
    dirty = sh("git", "status", "--porcelain").stdout.strip()
    if dirty:
        raise RuntimeError(f"working tree not clean, refusing to run:\n{dirty}")
    sh("git", "fetch", "origin", timeout=180)
    sh("git", "checkout", "main")
    sh("git", "pull", "--ff-only", "origin", "main", timeout=180)


def open_cycle_pr_exists() -> bool:
    try:
        out = sh("gh", "pr", "list", "--state", "open", "--json", "headRefName",
                 timeout=60).stdout
        return any(pr["headRefName"].startswith("skill-improvement/")
                   for pr in json.loads(out or "[]"))
    except Exception as exc:  # gh unavailable -> fail safe, don't stack branches
        log(f"warning: could not query open PRs ({exc}); skipping cycle")
        return True


def commit(message: str, *paths: str) -> str:
    sh("git", "add", *paths)
    sh("git", "commit", "-m", message)
    return sh("git", "rev-parse", "HEAD").stdout.strip()


def push_and_pr(branch: str, title: str, body: str) -> None:
    """Push the current branch, open a PR against main, and arm auto-merge.
    No direct commits ever land on main; the validate check gates the merge."""
    sh("git", "push", "-u", "origin", branch, timeout=180)
    sh("gh", "pr", "create", "--base", "main", "--head", branch,
       "--title", title, "--body", body, timeout=120)
    try:
        sh("gh", "pr", "merge", branch, "--auto", "--squash", timeout=120)
        log("auto-merge armed (merges when required checks pass)")
    except subprocess.CalledProcessError as exc:
        log(f"warning: could not enable auto-merge: {exc.stderr[:300]} — PR left open")


# ------------------------------------------------------------------- cycle

def process_skill(skill: dict, cycle_num: int, store: dict,
                  dry_run: bool = False) -> dict:
    name, path = skill["name"], skill["path"]
    original = path.read_text()
    mem = skill_memory(store, name)
    dimension = pick_dimension(mem)
    recent = [f"cycle {h['cycle']}: {h['dimension']} — {h['action']}"
              for h in mem["history"][-5:] if h["status"] == "improved"]

    before = judge(original)
    revised = improve(original, dimension, recent)
    if not sane(original, revised):
        raise ValueError(f"{name}: revised SKILL.md failed sanity checks")
    after = judge(revised)

    entry = {
        "skill": name,
        "cycle": cycle_num,
        "timestamp": iso(now()),
        "dimension": dimension,
        "score_before": before["total"],
        "score_after": after["total"],
        "delta": round(after["total"] - before["total"], 2),
        "scores_before": before,
        "scores_after": after,
    }

    if after["total"] < before["total"]:
        entry["status"] = "reverted-regression"
        entry["action"] = (f"attempted {dimension} improvement; judge scored it lower "
                           f"({before['total']}->{after['total']}), change discarded")
        entry["commit"] = None
        log(f"  {name}: regression {before['total']}->{after['total']}, reverted")
    elif revised.strip() == original.strip():
        entry["status"] = "no-change"
        entry["action"] = f"{dimension} pass produced no textual change"
        entry["commit"] = None
        log(f"  {name}: {dimension} pass produced no change")
    elif dry_run:
        entry["status"] = "improved"
        entry["action"] = f"{dimension} revision generated (dry-run, not persisted)"
        entry["commit"] = None
        log(f"  {name}: {dimension} {before['total']}->{after['total']} "
            f"({entry['delta']:+.2f}) [dry-run]")
    else:
        path.write_text(revised)
        msg = (f"feat({name}): improve {dimension} "
               f"(score {before['total']}->{after['total']})\n\n"
               f"Skill: {name}\n"
               f"Action: automated {dimension} revision — {DIMENSION_HINTS[dimension]}\n"
               f"Performance delta: {before['total']} -> {after['total']} "
               f"({entry['delta']:+.2f})\n"
               f"Cycle: {cycle_num}")
        entry["status"] = "improved"
        entry["action"] = f"{dimension} revision applied"
        entry["commit"] = commit(msg, str(path.relative_to(ROOT)))
        log(f"  {name}: {dimension} {before['total']}->{after['total']} "
            f"({entry['delta']:+.2f}) @ {entry['commit'][:8]}")

    record_result(store, name, entry)
    return entry


def run_cycle(state: dict, dry_run: bool) -> int:
    started_at = datetime.fromisoformat(state["started_at"].replace("Z", "+00:00"))
    cycle_num = state["cycles_completed"] + 1
    ts = now()
    branch = f"skill-improvement/cycle-{cycle_num:03d}-{ts.strftime('%Y%m%dT%H%M')}"

    skills = discover_elite_skills()
    if not skills:
        log("no elite-tier skills found; nothing to do")
        return 0
    log(f"cycle {cycle_num}/{state['total_cycles']}: {len(skills)} elite skills, "
        f"branch {branch}{' (dry-run)' if dry_run else ''}")

    if not dry_run:
        git_preflight()
        if open_cycle_pr_exists():
            log("previous cycle PR still open; deferring this cycle")
            return 0
        sh("git", "checkout", "-b", branch)

    store = load_json(MEMORY_PATH, default_memory())
    results, errors = [], []

    for skill in skills:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                results.append(process_skill(skill, cycle_num, store, dry_run))
                break
            except Exception as exc:
                log(f"  {skill['name']}: attempt {attempt}/{MAX_RETRIES} failed: {exc}")
                sh("git", "checkout", "--", str(skill["path"].relative_to(ROOT)),
                   check=False)
                if attempt == MAX_RETRIES:
                    errors.append({"skill": skill["name"], "error": str(exc)[:500],
                                   "attempts": attempt, "timestamp": iso(now())})
                    record_result(store, skill["name"], {
                        "skill": skill["name"], "cycle": cycle_num,
                        "timestamp": iso(now()), "dimension": None,
                        "score_before": None, "score_after": None, "delta": 0,
                        "status": "failed", "action": f"failed after {attempt} attempts",
                        "commit": None,
                    })
                else:
                    time.sleep(10 * attempt)

    audit = {
        "cycle": cycle_num,
        "timestamp": iso(ts),
        "schedule": {"started_at": state["started_at"],
                     "total_cycles": state["total_cycles"],
                     "day": (ts - started_at).days + 1},
        "branch": branch,
        "model": MODEL,
        "elite_skills_processed": [s["name"] for s in skills],
        "results": results,
        "errors": errors,
        "memory_storage": {"backend": "file-json",
                           "path": str(MEMORY_PATH.relative_to(ROOT)),
                           "confirmed": True},
        "dry_run": dry_run,
    }
    audit_path = AUDIT_DIR / f"cycle-{cycle_num}-{ts.strftime('%Y-%m-%d-%H-%M')}.json"

    state["cycles_completed"] = cycle_num
    state["last_run_at"] = iso(ts)
    state["last_branch"] = branch

    if dry_run:
        print(json.dumps(audit, indent=2))
        log("dry-run complete; no files persisted, no git operations")
        return 0

    save_json(audit_path, audit)
    save_json(MEMORY_PATH, store)
    save_json(STATE_PATH, state)
    chore_hash = commit(
        f"chore(cycle-{cycle_num}): audit log, memory store, loop state\n\n"
        f"Skills processed: {', '.join(s['name'] for s in skills)}\n"
        f"Improved: {sum(1 for r in results if r['status'] == 'improved')}, "
        f"reverted: {sum(1 for r in results if r['status'] == 'reverted-regression')}, "
        f"failed: {len(errors)}",
        str(audit_path.relative_to(ROOT)),
        str(MEMORY_PATH.relative_to(ROOT)),
        str(STATE_PATH.relative_to(ROOT)),
    )
    log(f"audit + memory committed @ {chore_hash[:8]}")

    pr_body = PR_TEMPLATE.read_text().format(
        cycle=cycle_num, total=state["total_cycles"], timestamp=iso(ts),
        skills="\n".join(
            f"| {r['skill']} | {r['dimension'] or '—'} | {r['status']} "
            f"| {r['score_before']} | {r['score_after']} | {r['delta']:+.2f} |"
            for r in results),
        errors="\n".join(f"- **{e['skill']}**: {e['error']}" for e in errors) or "None",
        audit_file=audit_path.name,
    )
    push_and_pr(branch,
                f"skill-improvement: cycle {cycle_num}/{state['total_cycles']}",
                pr_body)
    return 0


# ------------------------------------------------------------- finalization

def finalize(state: dict) -> None:
    log("7-day schedule complete — generating summary report and arming reminder")
    git_preflight()
    branch = f"skill-improvement/finalize-{now().strftime('%Y%m%dT%H%M')}"
    sh("git", "checkout", "-b", branch)

    subprocess.run([sys.executable, str(ROOT / "loop" / "generate_summary.py")],
                   cwd=ROOT, check=True)
    save_json(REMINDER_PATH, {
        "active": True,
        "created_at": iso(now()),
        "message": ("7-day Elite Skills Improvement Schedule has completed. "
                    "Please review audit summary at /audit-logs/summary-report.json "
                    "and set a new improvement schedule."),
        "acknowledge_with": "loop/acknowledge.sh",
    })
    state["active"] = False
    state["completed_at"] = iso(now())
    save_json(STATE_PATH, state)

    commit("chore: finalize 7-day schedule — summary report + session reminder",
           "audit-logs/summary-report.json",
           str(STATE_PATH.relative_to(ROOT)),
           str(REMINDER_PATH.relative_to(ROOT)))
    push_and_pr(branch,
                "skill-improvement: 7-day schedule complete — summary report",
                "Automated finalization: summary report generated, session "
                "reminder armed. See `audit-logs/summary-report.json`.")


# -------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", action="store_true",
                    help="initialize a new 7-day schedule (commits state to main)")
    ap.add_argument("--stop", action="store_true", help="deactivate the schedule")
    ap.add_argument("--status", action="store_true", help="print schedule status")
    ap.add_argument("--dry-run", action="store_true",
                    help="run one cycle without git/PR operations or persistence")
    args = ap.parse_args()

    state = load_json(STATE_PATH, {"active": False})

    if args.status:
        print(json.dumps(state, indent=2))
        return 0

    if args.start or args.stop:
        git_preflight()
        verb = "start" if args.start else "stop"
        branch = f"skill-improvement/{verb}-{now().strftime('%Y%m%dT%H%M%S')}"
        sh("git", "checkout", "-b", branch)
        if args.start:
            state = {"active": True, "started_at": iso(now()),
                     "total_cycles": TOTAL_CYCLES, "period_days": PERIOD_DAYS,
                     "cycles_completed": 0, "last_run_at": None,
                     "last_branch": None}
            if REMINDER_PATH.exists():
                REMINDER_PATH.unlink()
        else:
            state["active"] = False
            state["stopped_at"] = iso(now())
        save_json(STATE_PATH, state)
        commit(f"chore: {verb} 7-day elite skills improvement schedule",
               str(STATE_PATH.relative_to(ROOT)))
        push_and_pr(branch,
                    f"skill-improvement: {verb} schedule",
                    f"Schedule administration: **{verb}**. Cycles begin/cease "
                    "once this merges to main (the hourly cron reads state "
                    "from main).")
        log(f"schedule {verb} PR opened; takes effect when merged to main")
        return 0

    if not state.get("active"):
        log("no active schedule (run with --start to begin); exiting")
        return 0

    # Idempotency: never run twice inside one cycle window.
    if state.get("last_run_at") and not args.dry_run:
        last = datetime.fromisoformat(state["last_run_at"].replace("Z", "+00:00"))
        if now() - last < timedelta(minutes=MIN_CYCLE_GAP_MIN):
            log(f"last cycle ran {iso(last)} (<{MIN_CYCLE_GAP_MIN}m ago); no-op")
            return 0

    started = datetime.fromisoformat(state["started_at"].replace("Z", "+00:00"))
    if (state["cycles_completed"] >= state["total_cycles"]
            or now() >= started + timedelta(days=state["period_days"])):
        finalize(state)
        return 0

    return run_cycle(state, args.dry_run)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        log(f"FATAL: {exc}")
        sys.exit(1)
