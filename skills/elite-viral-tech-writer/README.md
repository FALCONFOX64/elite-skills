# Elite Viral Tech Writer

A Claude Code / Grok skill for writing that engineers respect **and** everyone shares.
Fuses top-1% technical documentation craft (design docs, PRDs, ADRs, API
specs) with elite marketing instincts (hooks, story, positioning, launch
copy). Never trades accuracy for engagement, or engagement for accuracy.

## Activate

- Slash command: `/elite-viral-tech-writer` (aliases: `/viral-doc`,
  `/design-viral`, `/elite-writer`)
- Natural language: "write a README for this", "make this launch post
  actually land", "design doc for X", "rewrite this so people care"
- Grok TUI menu: `/skills elite-viral-tech-writer`

## Quick start

```
/viral-doc README for ~/Developer/myproject — audience is HN, launching Tuesday
/design-viral design doc for the sync engine; reviewers are skeptical of CRDTs
/elite-writer this announcement is accurate but nobody shared it: <paste>
```

Give it three things for best results: **artifact type**, **audience**, and
**ground truth** (the repo, benchmark, or draft). It will refuse to invent
numbers or APIs — its rigor is capped by what you show it.

To adjust tone, steer the mode dial, not the sentences: "more design mode"
(rigor-forward) or "more marketing mode" (hook-forward).

## Files

| File | What it is |
|---|---|
| `SKILL.md` | The persona: principles, mode dial, process, anti-patterns |
| `references/templates.md` | Full annotated templates: README, design doc, ADR, PRD, launch post, blog post, changelog |
| `references/frameworks.md` | Crib sheet: JTBD, PAS, AIDA, SUCCESs, C4, ADR, Diátaxis, PR/FAQ — with when-to-use guidance |
