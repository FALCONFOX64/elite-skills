# elite-skills

A living library of elite Claude Code skill definitions for DevOps/SRE and software engineering, continuously updated via an automated research loop.

## What's in here

| Path | Purpose |
|---|---|
| `skills/elite-devops-engineer/SKILL.md` | Principal SRE / platform engineer persona |
| `skills/elite-software-engineer/SKILL.md` | Principal software engineer persona (Clean Code, TDD, refactoring) |
| `loop/prompt.md` | The Claude Code loop prompt that drives continuous updates |
| `loop/schedule.md` | How to run and manage the update loop |
| `DESIGN.md` | High-level design: architecture, philosophy, update lifecycle |

## Quick install

Copy both skills into your global Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills/elite-devops-engineer ~/.claude/skills/elite-software-engineer
cp skills/elite-devops-engineer/SKILL.md ~/.claude/skills/elite-devops-engineer/SKILL.md
cp skills/elite-software-engineer/SKILL.md ~/.claude/skills/elite-software-engineer/SKILL.md
```

Restart Claude Code. The skills will be available in any session.

## Invoke the skills

Once installed, trigger either skill from within Claude Code:

```
/elite-devops-engineer  →  SRE / platform engineering mode
/elite-software-engineer  →  Clean code / TDD / architecture mode
```

Or reference them directly in a prompt:

> "Review this Kubernetes deployment manifest using the elite-devops-engineer skill"

> "Review this PR using the elite-software-engineer skill"

## The update loop

The skills stay current via a Claude Code self-paced loop that:
1. Searches for trending tools, patterns, and practices in DevOps and software engineering
2. Filters for signal (genuine adoption among top practitioners) over noise (hype)
3. Patches the skill files with new technology references, updated anti-patterns, and refreshed process guidance
4. Commits the changes with a summary of what changed and why

See `loop/` for the prompt and scheduling instructions.

## Philosophy

These skills encode what top-tier practitioners actually do — not what textbooks say. Every recommendation is grounded in battle-tested practice. The update loop ensures they don't drift behind the industry.

See `DESIGN.md` for the full design rationale.
