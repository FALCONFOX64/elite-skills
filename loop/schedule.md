# Loop Scheduling Guide

## Option 1: Interactive session loop (recommended for now)

Run inside any Claude Code session. The loop self-paces and runs as long as the session is open.

```
/loop [paste prompt from prompt.md]
```

Claude schedules its own wakeups. No configuration needed. Stop by closing the session or telling Claude to stop the loop.

## Option 2: GitHub Actions scheduled workflow (future)

Automate the loop to run on a cron schedule and commit updates directly to the repo.

Planned workflow (`.github/workflows/update-skills.yml`):

```yaml
name: Update Elite Skills
on:
  schedule:
    - cron: '0 6 * * *'   # Daily at 06:00 UTC
  workflow_dispatch:        # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run skill update loop
        run: |
          # Claude Code CLI invocation (when headless loop support ships)
          claude --print "$(cat loop/prompt.md)" \
            --output-format text \
            > /tmp/loop-output.txt
      - name: Commit if changed
        run: |
          git config user.name "elite-skills-loop"
          git config user.email "loop@falconfox.com"
          git add skills/
          git diff --cached --quiet || \
            git commit -m "loop: update skills [$(date +%Y-%m-%d)]"
          git push
```

Status: **planned** — requires Claude Code headless loop support.

## Option 3: Cloud schedule via /schedule

Use Claude Code's `/schedule` skill to run the update prompt on a cloud-hosted cron:

```
/schedule daily at 7am: [paste prompt from prompt.md]
```

This runs independently of any local session. Output is delivered as a notification.

## Stopping the loop

In an active session loop: tell Claude "stop the loop" or close the session.

For a cloud schedule: run `/schedule` → manage → delete the relevant job.
