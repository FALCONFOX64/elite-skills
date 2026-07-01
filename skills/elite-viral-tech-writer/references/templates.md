# Templates — Elite Viral Tech Writer

Full annotated skeletons. Each template lists its mode, the reader's state of
mind, and per-section guidance. Copy the skeleton, then run the Viral
Technical Design Loop from SKILL.md over it.

---

## 1. Viral README (Hybrid, 50:50)

**Reader's state**: landed from a link, deciding in ~10 seconds whether this
repo deserves 5 minutes. They are asking: *what is it, is it for me, does it
actually work, can I try it right now?* Answer in that order.

````markdown
# <name> — <what it does + why you'd care, ≤ 12 words>

<!-- 1-2 sentence expansion: the pain it kills, stated as the reader's pain -->

<!-- THE 30-SECOND PROOF: gif, asciinema, or a copy-paste block that shows
     the core value. This is the most important block in the file. -->
```bash
<the one command that demonstrates the magic>
```

## Why this exists
<!-- 3 sentences max. The story: what broke, what you tried, why you built
     this instead. Founders' honesty here converts skeptics. -->

## Install
<!-- Shortest real path first. Alternatives collapsed or linked. -->

## Usage
<!-- 2-4 runnable examples ordered by likelihood of need. Each: one line of
     context, then code, then (if non-obvious) expected output. -->

## How it compares
<!-- Honest table vs. 2-3 real alternatives. You MUST lose at least one row,
     truthfully — it's what makes the rows you win believable. -->

## Limits
<!-- Plain statements of what it doesn't do / when not to use it.
     This section generates more trust per word than any other. -->

## Contributing / License
<!-- Standard, brief. -->

<!-- ONE closing CTA: star, try the hosted demo, join the Discord. Pick one. -->
````

**Skim test for READMEs**: title + first code block alone should be enough
for a reader to decide correctly.

---

## 2. Design Doc (Design, 80:20)

**Reader's state**: obligated but busy; a reviewer looking for reasons to
object. Your job: make the *thinking* inspectable, not just the conclusion.

```markdown
# <Title: the decision, not the topic — "Sync via CRDTs" not "Sync Design">

**Status**: draft | in review | approved  **Author**:  **Reviewers**:  **Date**:

## Context and Problem
<!-- THE HOOK LIVES HERE, even in design mode. Open with the concrete failure
     or limit that forces this work: the incident, the metric, the customer.
     Then: why now. 2-3 paragraphs. A reviewer who feels the problem reviews
     the solution generously. -->

## Goals
<!-- Measurable. "Support 10k concurrent editors at <200ms sync latency." -->

## Non-Goals
<!-- As important as goals. Each non-goal is a pre-empted review comment. -->

## Proposed Design
<!-- C4 discipline: zoom in stepwise.
     1. Context: the system in its environment (one diagram).
     2. Containers: deployable units and their interactions.
     3. Components: only for the parts that are novel or contested.
     Interfaces before internals. Include the data model and the failure
     modes: what happens when each arrow in the diagram breaks? -->

## Alternatives Considered
<!-- The credibility engine. For each: what it was, its genuine strengths,
     and the specific reason it lost. "Rejected because we didn't like it"
     is not a reason; "rejected because it requires clock sync we can't
     guarantee across regions" is. -->

## Risks and Mitigations
## Rollout Plan
<!-- Phases, guardrail metrics, and the rollback trigger. A design that
     can't be rolled out incrementally is a design risk itself. -->

## Open Questions
<!-- Numbered, so review comments can reference them. -->
```

---

## 3. Architecture Decision Record (Design — Nygard format)

One decision per record. Immutable once accepted; superseded, never edited.

```markdown
# ADR-<number>: <decision in active voice>

**Status**: proposed | accepted | superseded by ADR-<n>
**Date**:

## Context
<!-- The forces in tension: technical, organizational, political. Neutral
     tone — a future reader should understand why this was hard. -->

## Decision
<!-- "We will <do X>." Active voice, no hedging. -->

## Consequences
<!-- BOTH directions. What gets easier, what gets harder, what debt is
     taken on knowingly. An ADR listing only benefits is fiction and will
     be treated as such by the engineer who inherits it. -->
```

---

## 4. PRD (Hybrid, 50:50)

**Reader's state**: split audience — execs skim for the bet, engineers read
for the contract. Serve both: narrative up top, precision below.

```markdown
# PRD: <feature/product>

## The Opportunity
<!-- One paragraph that a CEO and a staff engineer both nod at. Pain,
     evidence of pain (support tickets, churn data, user quotes), size of
     prize. Optional power move: replace this section with an Amazon-style
     internal press release — write the launch announcement first, work
     backwards. -->

## Who and Why (JTBD)
<!-- "When I <situation>, I want to <motivation>, so I can <outcome>."
     One primary job. Secondary jobs listed but explicitly deprioritized. -->

## Success Metrics
<!-- Numbers and dates. "Adoption" is not a metric; "40% of weekly-active
     teams use it within 60 days of GA" is. Include the counter-metric
     you'll watch to catch harm (e.g., support load, latency). -->

## Requirements
<!-- MoSCoW-ranked: Must / Should / Could / Won't. Each requirement
     testable — a reviewer should be able to say pass/fail. -->

## Out of Scope
<!-- Explicit. Every deferred feature named here saves a meeting later. -->

## Open Questions
```

---

## 5. Launch Announcement (Marketing, 20:80)

**Reader's state**: mid-scroll, zero obligation, 2 seconds of attention on
loan. Structure is PAS wrapped around one demo.

```markdown
<!-- HOOK — one of:
     • the problem, viscerally ("Your CI bill doubled and got slower.")
     • the number ("We cut cold starts from 6s to 80ms.")
     • the counterintuitive claim ("We deleted our cache to get faster.")
     Never: "We're excited to announce..." — that's *your* emotion, and the
     reader doesn't work for you. -->

<!-- PROBLEM → AGITATE: 2-3 short paragraphs. Name the pain, then the cost
     of living with it — in the reader's currency (time, money, on-call
     sleep). Specific scenario beats general claim. -->

<!-- SOLVE — THE REVEAL: what it is, in one sentence, then immediately the
     demo: code block, gif, or before/after numbers. Show, then explain. -->

<!-- PROOF: one or two, real only — benchmark (linked methodology), design
     partner quote (named, with permission), live playground. Rigor Gate
     applies at full strength here precisely because this is the section
     most tempting to inflate. -->

<!-- PRACTICALITIES: pricing/availability/compatibility in plain terms.
     Burying the price reads as shame. -->

<!-- ONE CTA: the single next action, lowest-friction version.
     "Try it in your browser, no signup: <link>" -->
```

**Channel variants**: HN — cut the agitate section, engineers self-agitate;
lead closer to the technical meat and link the deep-dive. Twitter/X thread —
hook tweet must stand completely alone; one idea per tweet; demo in tweet 2.
Email — subject line is the hook and gets 50% of the effort.

---

## 6. Technical Blog Post (Hybrid, 50:50)

**Reader's state**: chose to click on a promise; will leave at the first
paragraph that doesn't advance it.

```markdown
# <Title: specific promise, no gap — "How we cut Postgres storage 60% with
   one migration" not "Our Postgres Journey">

<!-- HOOK: the moment of maximum tension in the story. The 3am page, the
     graph going vertical, the test that couldn't fail but did. In medias
     res — start inside the moment, backfill context after. -->

<!-- CONTEXT: the minimum a smart outsider needs. Resist explaining your
     whole architecture; link instead. -->

<!-- THE JOURNEY: attempts in order, including failures — the failed
     attempts are what make it a story and not a press release. Real code,
     real numbers, real dead ends. Section headers narrate the arc
     ("The obvious fix made it worse"). -->

<!-- THE PAYOFF: the resolution, with the before/after evidence. -->

<!-- THE LESSON: one generalizable takeaway the reader can apply without
     your codebase. This is the part that gets quoted and shared. -->

<!-- CTA: one door — the repo, the deeper doc, the hiring page. -->
```

---

## 7. Changelog / Release Notes (Hybrid, quick-form)

Per notable change: **what changed → why you'd care → migration cost if any**,
in 1-3 lines. Lead the release with the single most valuable change, not the
chronologically first. Group the rest: Added / Changed / Fixed / Deprecated.
Breaking changes get a migration snippet, not a warning label.
