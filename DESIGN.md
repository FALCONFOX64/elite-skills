# High-Level Design: elite-skills

## Overview

`elite-skills` is a self-updating Claude Code skill library. It encodes the mindset, decision frameworks, and practices of top-tier (0.01%) engineers as reusable skill definitions — and keeps them current through an automated research loop that continuously patches the skills with emerging tools, patterns, and anti-patterns.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        GitHub Repo                          │
│  skills/                                                    │
│    elite-devops-engineer/SKILL.md  ◄──┐                    │
│    elite-software-engineer/SKILL.md ◄─┤  committed updates │
│  loop/                              │                       │
│    prompt.md  ──────────────────────┘                      │
│    schedule.md                                              │
└─────────────────────────────────────────────────────────────┘
         │  git pull / manual sync
         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Local Claude Code                          │
│  ~/.claude/skills/                                          │
│    elite-devops-engineer/SKILL.md                           │
│    elite-software-engineer/SKILL.md                         │
│                                                             │
│  Session: /elite-devops-engineer                            │
│           /elite-software-engineer                          │
└─────────────────────────────────────────────────────────────┘
         │  skill context injected
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Session                       │
│  - Persona active for duration of invocation                │
│  - Applies principles, frameworks, output standards         │
│  - Flags anti-patterns proactively                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Update Loop Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                    Claude Code Loop                           │
│                                                               │
│  1. WebSearch: DevOps/SRE trending tools (current year)      │
│  2. WebSearch: Software engineering trends (current year)     │
│  3. Filter: signal > noise (adoption by top practitioners)   │
│  4. Patch: SKILL.md files — tech refs, anti-patterns,        │
│            process guidance                                   │
│  5. Summarize: what changed and why                           │
│  6. ScheduleWakeup: self-pace next iteration                 │
│                                                               │
│  Cadence: self-paced (model chooses based on signal velocity) │
│  Fallback: hourly wakeup if no event fires                   │
└───────────────────────────────────────────────────────────────┘
```

---

## Skill Design Philosophy

### Why skills instead of system prompts?

Claude Code skills are reusable, invocable, and composable. A skill can be:
- Triggered on demand for a specific task
- Combined with other skills in the same session
- Updated independently of any project
- Shared across all projects via `~/.claude/skills/`

A system prompt is session-wide and static. A skill is surgical and living.

### Persona architecture

Each skill is structured in layers:

```
SKILL.md
├── Persona          — who the model is embodying
├── Core Principles  — non-negotiable truths (sorted by impact)
├── Decision Frameworks — how to reason about trade-offs
├── Processes        — concrete steps for common scenarios
├── Output Standards — what every response must contain
├── Technology Reference — canonical tools (updated by loop)
├── Anti-Patterns    — what to flag immediately (updated by loop)
└── Autonomy Mode    — how to behave without hand-holding
```

The **Technology Reference** and **Anti-Patterns** sections are the primary targets of loop updates — they decay fastest as the industry evolves.

### Signal vs. noise filter

The loop applies a strict filter before patching:

| Include | Exclude |
|---|---|
| Tools with measurable enterprise adoption | Tools in preview / beta only |
| Practices backed by data (Gartner, DORA, vendor reports) | Practices backed only by blog posts |
| Anti-patterns with documented incident history | Theoretical risks without real-world examples |
| Industry consensus across multiple sources | Single-vendor claims |

---

## Skill File Format

Skills follow the Claude Code command format: YAML frontmatter + Markdown body.

```markdown
---
description: One-line description used for skill discovery
---

# Skill Title

## Persona
...

## Core Principles
...
```

The `description` field is what Claude Code displays in skill listings. Keep it under 160 characters and make it trigger-condition specific.

---

## Installation & Distribution

### Single machine
```bash
cp -r skills/elite-devops-engineer ~/.claude/skills/
cp -r skills/elite-software-engineer ~/.claude/skills/
```

### Team / org distribution
For teams, add this repo as a Claude Code plugin source in `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "elite-skills": {
      "source": {
        "source": "github",
        "repo": "FALCONFOX64/elite-skills"
      }
    }
  }
}
```

Then install via the Claude Code marketplace UI.

---

## Update Loop: Operational Notes

### Running the loop
In any Claude Code session:
```
/loop Research trending technology developments relevant to DevOps/SRE and elite software engineering...
```
(Full prompt in `loop/prompt.md`)

### What the loop touches
- **Adds** to Technology Reference tables when new tools reach production adoption
- **Adds** to Anti-Patterns when a new failure mode has documented real-world impact
- **Updates** process guidance when better practices have displaced old ones
- **Does not remove** established content without clear evidence of obsolescence

### Committing loop output
After each iteration, commit the updated SKILL.md files:
```bash
git add skills/
git commit -m "loop: update skills with trending tech [YYYY-MM-DD]"
git push
```

Then pull on other machines:
```bash
git pull
cp -r skills/elite-devops-engineer ~/.claude/skills/
cp -r skills/elite-software-engineer ~/.claude/skills/
```

---

## Roadmap

- [ ] GitHub Actions workflow to run the loop on a schedule and auto-commit
- [ ] Additional skills: `elite-security-engineer`, `elite-data-engineer`, `elite-ml-engineer`
- [ ] Marketplace plugin manifest so the skills install via `claude marketplace install`
- [ ] Changelog auto-generation from loop summaries
- [ ] Diff view per iteration to track skill evolution over time
