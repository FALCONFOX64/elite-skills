# Update Loop Prompt

This is the prompt used with Claude Code's `/loop` command to continuously research and update the elite skills.

## Usage

In any Claude Code session with this repo open, run:

```
/loop Research trending technology developments relevant to DevOps/SRE and elite software engineering — new tools, frameworks, patterns, and practices gaining traction in the industry. Then update both ~/.claude/skills/elite-devops-engineer/SKILL.md and ~/.claude/skills/elite-software-engineer/SKILL.md to reflect what's current: add emerging tools to the technology reference tables, update anti-patterns if new ones have become common, and refresh any process recommendations where better practices have emerged. Focus on signal over noise — only add what's genuinely gaining adoption among top practitioners, not hype. After each update, summarize what changed and why.
```

The loop is self-paced — Claude decides the cadence based on how much signal is available. Typically fires every 1-4 hours in an active session.

## What the loop does each iteration

1. **Searches** for current-year trends across DevOps/SRE and software engineering
2. **Filters** results: only includes tools/practices with documented adoption data
3. **Patches** the skill files:
   - Technology Reference tables — new tools at production-adoption stage
   - Anti-Patterns — new failure modes with real-world evidence
   - Process sections — updated guidance where better practices have emerged
4. **Syncs** changes to `~/Developer/elite-skills/` copies
5. **Summarizes** what changed and why before sleeping

## After each iteration

Commit the changes to keep the repo in sync:

```bash
cd ~/Developer/elite-skills
git add skills/
git commit -m "loop: update skills with trending tech [$(date +%Y-%m-%d)]"
git push
```

## Signal quality criteria

The loop applies this filter before updating a skill:

| Signal quality | Action |
|---|---|
| Adopted by multiple Fortune 500 / top-tier engineering orgs | Add immediately |
| CNCF incubating or graduated project | Add to tech reference |
| Backed by DORA, Gartner, or major vendor survey data | Add anti-pattern or update process |
| Single blog post, vendor marketing, or preview-only tool | Skip |
| Hype without adoption metrics | Skip |
