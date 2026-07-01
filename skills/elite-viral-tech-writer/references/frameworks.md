# Framework Crib Sheet — Elite Viral Tech Writer

When-to-use guidance for the proven frameworks this persona draws on. These
are lenses, not scripts: pick one per artifact, apply it invisibly. If the
reader can name the framework you used, you used it too loudly.

---

## Marketing / Resonance Side

### Jobs-to-be-Done (JTBD) — Christensen, Ulwick
**What**: people "hire" products to do a job in a specific situation.
Format: *"When I <situation>, I want to <motivation>, so I can <outcome>."*
**Use for**: PRDs (define the job before requirements), positioning, README
"why this exists" sections, choosing which features a launch post mentions.
**The move**: write the job statement first; every claim in the artifact must
serve it. Features that don't serve the primary job get cut or demoted.

### AIDA — Attention, Interest, Desire, Action
**What**: the classic conversion arc: stop them → intrigue them → make them
want it → tell them exactly what to do.
**Use for**: landing copy, launch emails, any artifact whose success metric
is a click. Weakest for engineer audiences — they resent visible Desire
stages; compress AIDA to Attention → Evidence → Action for them.

### PAS — Problem, Agitate, Solve
**What**: name the pain, make its cost vivid, then reveal the fix.
**Use for**: launch announcements, cold outreach, the opening of blog posts.
The workhorse for technical marketing because it starts from truth (a real
problem) rather than hype.
**Caution**: agitation must stay factual ("this costs your team ~4 hrs/week")
— manufactured dread reads as manipulation and fails the Rigor Gate.

### Hook–Story–Offer — Brunson
**What**: earn attention (hook), transfer belief through narrative (story),
then present the ask (offer).
**Use for**: longer-form launches, product pages, conference talk abstracts,
threads. The story is where technical writing has an unfair advantage: real
engineering war stories are inherently better than invented marketing ones.

### SUCCESs — *Made to Stick*, Heath brothers
**What**: sticky ideas are Simple, Unexpected, Concrete, Credible, Emotional,
Stories.
**Use as**: a final-pass checklist on any Hybrid or Marketing artifact. The
two levers most often missing from technical writing: **Unexpected** (lead
with the counterintuitive finding) and **Concrete** (replace category words
with picturable ones).

### Positioning — *Obviously Awesome*, Dunford
**What**: deliberately choose the market frame: competitive alternatives →
unique attributes → value → who cares most → market category.
**Use for**: the comparison table in a README, the category sentence in a
launch ("a time-series database" vs. "flight recorder for your metrics"),
deciding which alternatives a design doc must address.

---

## Design / Rigor Side

### C4 Model — Simon Brown
**What**: architecture described at four zoom levels — Context, Containers,
Components, Code — each diagram for a specific audience.
**Use for**: the Proposed Design section of design docs. Most docs need only
levels 1-2; draw level 3 only for the novel or contested parts. Never mix
zoom levels in one diagram — it's the diagram equivalent of a run-on
sentence.

### Architecture Decision Records — Michael Nygard
**What**: short, immutable records of architecturally significant decisions:
Context → Decision → Consequences.
**Use for**: any decision someone will later ask "why on earth did they do
it this way?" about. The Consequences section must list costs, not just
benefits — that asymmetry is what separates a record from an advertisement.

### Diátaxis — Daniele Procida
**What**: documentation has four distinct modes serving four reader needs:
**tutorials** (learning), **how-to guides** (goals), **reference**
(information), **explanation** (understanding).
**Use for**: structuring doc sites and deciding what a given page is allowed
to do. The most common docs failure is mixing modes — a tutorial that
detours into reference tables loses the learner. One page, one mode.

### Working Backwards PR/FAQ — Amazon
**What**: write the launch press release and customer FAQ *before* building;
if the PR isn't compelling, the product isn't either.
**Use for**: PRD openings, validating a feature idea, forcing clarity on
customer benefit early. This framework IS the fusion this skill exists for
— marketing craft used as a design-rigor tool.

### Design Doc Culture — Google-style
**What**: conventions that make design docs reviewable: goals/non-goals,
alternatives considered with honest rejection reasons, explicit open
questions, named reviewers, status lifecycle.
**Use for**: any Design-mode artifact in a multi-stakeholder setting. The
underrated section is **Non-Goals**: each one is a review objection answered
in advance.

---

## Cross-Cutting Pairings

| Artifact | Rigor lens | Resonance lens |
|---|---|---|
| README | Diátaxis (it's a how-to + reference hybrid) | Positioning + SUCCESs |
| Design doc | C4 + Google conventions | PAS (in the Context section only) |
| ADR | Nygard | — (clarity is the resonance) |
| PRD | Working Backwards | JTBD |
| Launch post | Rigor Gate on every claim | PAS or Hook-Story-Offer |
| Blog post | real data, real code | Hook-Story-Offer + SUCCESs |
| Landing page | scoped claims only | AIDA |
