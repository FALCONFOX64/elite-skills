# elite-skills

A living library of elite Claude Code skill definitions for DevOps/SRE, software engineering, validation, and technical writing — continuously improved by a fully autonomous agentic loop with PR-based change management, a persistent memory store, and a structured audit trail.

## What's in here

| Path | Purpose |
|---|---|
| `skills/elite-*/SKILL.md` | The five elite-tier skill personas (DevOps, software engineering, validation, viral tech writing, viral marketing) |
| `loop/run_cycle.py` | The agentic loop runner — executes exactly one improvement cycle per invocation |
| `loop/generate_summary.py` | Aggregates all audit logs into the 7-day summary report |
| `loop/validate.py` | CI validation gate (schemas + skill frontmatter) that gates PR auto-merge |
| `loop/check_reminder.sh` / `loop/acknowledge.sh` | Session-start completion reminder and its acknowledgement |
| `loop/run_local.sh` + `loop/com.falconfox.skill-improvement.plist` | Local macOS launchd scheduler (alternative to GitHub Actions) |
| `.github/workflows/skill-improvement.yml` | Hourly cron workflow that drives the loop in CI |
| `.github/workflows/validate.yml` | Required `validate` check for every PR |
| `schemas/` | JSON Schemas for the audit log and memory store |
| `templates/` | PR body template and summary report template |
| `audit-logs/` | One structured JSON audit file per cycle + final `summary-report.json` |
| `memory/store.json` | File-based JSON memory layer (created on first cycle) |
| `state/loop-state.json` | Schedule state: active flag, cycle counter, last-run timestamp |

## System architecture

```
           ┌────────────────────────────────────────────────────────┐
 hourly    │ Scheduler (pick one)                                   │
 trigger   │  A. GitHub Actions cron (skill-improvement.yml)        │
──────────▶│  B. macOS launchd (com.falconfox.skill-improvement)    │
           └───────────────────────┬────────────────────────────────┘
                                   ▼
           ┌────────────────────────────────────────────────────────┐
           │ loop/run_cycle.py — ONE idempotent cycle               │
           │                                                        │
           │ 1. Guards: schedule active? ≥45 min since last run?    │
           │    previous cycle PR merged? working tree clean?       │
           │ 2. Branch: skill-improvement/cycle-{NNN}-{timestamp}   │
           │ 3. Per elite skill (≤3 retries, exponential backoff):  │
           │      judge (score 0-100, 5 dimensions)                 │
           │      → pick least-recently-improved dimension (memory) │
           │      → generate revised SKILL.md (claude CLI)          │
           │      → sanity checks → re-judge                        │
           │      → commit `feat(skill): improve X (score a→b)`     │
           │        or discard on regression                        │
           │ 4. Persist memory + audit log + state → `chore` commit │
           │ 5. Push branch → PR from template → auto-merge armed   │
           └───────────────────────┬────────────────────────────────┘
                                   ▼
           ┌────────────────────────────────────────────────────────┐
           │ PR gate: `validate` check (schemas, frontmatter)       │
           │ passes → auto-merge → main advances → next cycle       │
           │ pulls fresh state. No direct commits to main.          │
           └───────────────────────┬────────────────────────────────┘
                                   ▼
           ┌────────────────────────────────────────────────────────┐
           │ Cycle 168 or day 7 reached → finalize:                 │
           │ summary-report.json + state/reminder.json armed →      │
           │ SessionStart hook surfaces reminder every session      │
           │ until loop/acknowledge.sh is run                       │
           └────────────────────────────────────────────────────────┘
```

**Elite-tier detection:** a skill is targeted if its directory name starts with `elite-` or its frontmatter contains `tier: elite`.

**Memory layer:** version-controlled file-based JSON store at `memory/store.json` (schema: `schemas/memory.schema.json`). Every result is stored with skill name/category, action taken, timestamp, before/after scores, and a cumulative trend. Each cycle queries `dimensions_covered` to pick the least-recently-improved dimension per skill, so consecutive cycles never repeat the same action — the "avoid redundant work" guarantee. Query it directly:

```bash
jq '.skills["elite-devops-engineer"].cumulative_trend' memory/store.json
jq '[.skills[].history[] | select(.status=="improved")] | length' memory/store.json
```

**Audit trail:** every cycle writes `audit-logs/cycle-{n}-{YYYY-MM-DD-HH-MM}.json` (schema: `schemas/audit-log.schema.json`) containing the cycle number, ISO 8601 timestamp, skills processed, per-skill actions and score deltas, memory-write confirmation, commit hashes, branch name, and any errors.

## Setup (GitHub Actions — recommended)

1. **Secrets** (Settings → Secrets and variables → Actions):
   - `ANTHROPIC_API_KEY` — required; consumed by the Claude Code CLI in CI. Never hardcoded.
   - `LOOP_PAT` — optional fine-grained PAT (contents + pull-requests: write). Without it the workflow uses `GITHUB_TOKEN`, whose PRs **won't trigger the `validate` workflow** (GitHub blocks workflow-triggering by `GITHUB_TOKEN` to prevent loops), so auto-merge would wait forever. A PAT is effectively required for hands-off operation.
2. **Allow auto-merge**: Settings → General → check *Allow auto-merge*.
3. **Branch protection on `main`**: require the `validate` status check and block direct pushes:
   ```bash
   gh api -X PUT repos/FALCONFOX64/elite-skills/branches/main/protection \
     -f 'required_status_checks[strict]=false' \
     -f 'required_status_checks[checks][][context]=validate' \
     -F 'enforce_admins=false' \
     -F 'required_pull_request_reviews=null' \
     -F 'restrictions=null' --input - <<'EOF'
   {"required_status_checks":{"strict":false,"checks":[{"context":"validate"}]},
    "enforce_admins":false,"required_pull_request_reviews":null,"restrictions":null,
    "allow_force_pushes":false,"allow_deletions":false}
   EOF
   ```
4. **Start the 7-day schedule**: Actions → *Skill Improvement Loop* → Run workflow → `start`. The next hourly cron fire begins cycle 1. Stop early anytime with `stop`.

From that point the system runs 168 hourly cycles over 7 days with zero human input, then finalizes itself.

### Cost warning

Each cycle makes ~3 model calls per skill (judge, improve, judge) × 5 skills × 168 cycles ≈ **2,500 API calls over the week**, each carrying a full SKILL.md (~2-4k tokens). Budget accordingly, pick a cheaper model via the `ELITE_LOOP_MODEL` repo variable, or shrink the run with `ELITE_LOOP_TOTAL_CYCLES`.

### A note on auto-merge

Auto-merging AI-generated PRs is an explicit design requirement of this system, gated on the `validate` check. Be aware this trades away human review — the elite-devops-engineer skill in this very repo flags that as an anti-pattern. The mitigations here: the judge-score regression guard, schema validation, frontmatter integrity checks, and a fully reconstructable audit trail. If you want a human gate, simply skip step 2 (don't allow auto-merge); cycles will stack one open PR and pause until you merge.

## Setup (local launchd — no API key needed)

Runs on this Mac using your existing `claude` login and `gh` auth:

```bash
cp loop/com.falconfox.skill-improvement.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.falconfox.skill-improvement.plist
python3 loop/run_cycle.py --start
```

Logs land in `state/local-runner.log`. Unload with `launchctl unload …` to stop the scheduler. Don't run both schedulers at once — the open-PR and last-run guards make it safe, but it wastes runs.

## Configuration

| Env var / repo variable | Default | Purpose |
|---|---|---|
| `ELITE_LOOP_MODEL` | `claude-sonnet-5` | Model for judge + improvement calls |
| `ELITE_LOOP_TOTAL_CYCLES` | `168` | Cycles in a schedule |
| `ELITE_LOOP_PERIOD_DAYS` | `7` | Hard wall-clock cap |
| `ELITE_LOOP_MAX_RETRIES` | `3` | Per-skill attempts per cycle |
| `ELITE_LOOP_CLAUDE_TIMEOUT` | `600` | Seconds per model call |
| `ELITE_LOOP_SKILL_FILTER` | *(empty)* | Comma-separated skill allowlist (testing) |

## Operations

```bash
python3 loop/run_cycle.py --status    # schedule state
python3 loop/run_cycle.py --dry-run   # one full cycle, no git/PR/persistence
python3 loop/run_cycle.py --stop      # deactivate
python3 loop/generate_summary.py      # (re)build summary-report.json anytime
python3 loop/validate.py              # run the CI gate locally
./loop/acknowledge.sh                 # clear the 7-day completion reminder
```

**Failure handling:** each skill task retries up to 3× with backoff; a skill that exhausts retries is recorded in the audit log's `errors` array and the cycle continues. A cycle whose PR can't merge simply defers subsequent cycles (open-PR guard) rather than stacking branches. Everything is resumable: state, memory, and audit logs are all in git.

**Completion reminder:** when the schedule finishes, `state/reminder.json` is armed and a Claude Code `SessionStart` hook prints the review reminder at the start of every session until you run `loop/acknowledge.sh`.

## Quick install of the skills themselves

```bash
cp -R skills/* ~/.claude/skills/
```

Restart Claude Code, then invoke: `/elite-devops-engineer`, `/elite-software-engineer`, `/elite-validation-engineer`, `/elite-viral-tech-writer`, `/elite-viral-marketing-manager`.

## Philosophy

These skills encode what top-tier practitioners actually do — not what textbooks say. The autonomous loop keeps them sharp: every revision is scored before and after by an LLM judge, regressions are discarded, every change ships through a schema-validated PR, and the full history is queryable from memory and audit logs.

See `DESIGN.md` for the original design rationale; `loop/prompt.md` and `loop/schedule.md` document the earlier manual research loop this system supersedes.
