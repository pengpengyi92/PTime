# PTime Agent Guide

PTime is the temporal coordination layer of the user's personal operating system.

Current Time -> Active Regions -> Relevant People -> Appropriate Channel -> Recommended Communication Action

## Core Relationships

- P Connection = WHO
- P Global = WHERE
- PTime = WHEN
- P Email / P LinkedIn = HOW

WHO x WHERE x WHEN x HOW -> ACTION

The global workday never exists in only one timezone. When one professional workday
ends, other regions may still be active. Use those windows intelligently; the goal
is not constant communication or sacrificing rest.

## Boundaries

PTime is not a full CRM, email client, LinkedIn replacement, calendar replacement,
or generic productivity app. It is a small composable timing and routing layer.

Prefer small adapters, clear interfaces, simple scoring, explainable recommendations
and configurable rules. Avoid monoliths, fixed timezone offsets, fake integrations,
unnecessary databases and premature AI complexity.

Before implementing a feature, ask whether it helps determine WHEN, WHO, WHERE, HOW,
or WHAT ACTION. Otherwise it probably belongs elsewhere.

## V2.0 Behavior

- Read README.md, AGENTS.md, VERSION, CHANGELOG.md and the current release document first.
- Keep legacy `now` and `contacts` available. Channel-aware routing is `talk` / `email`.
- Consume only explicit normalized local snapshots. P Kago is a generic placeholder,
  not a known native API. All integration names denote local adapter contracts.
- SEND_NOW is a timing suggestion, never permission to send. Every result requires
  human approval; actual calendar availability is unverified.
- Priority never overrides do-not-contact, quiet time, repeated follow-ups or channel restrictions.
- Explicit expected replies may qualify for asynchronous late windows.
  A friend's late window must be explicitly recorded; friendship alone is insufficient.
- An explicitly confirmed synchronous meeting may override usual working/quiet/preference
  windows only inside its recorded interval. It does not create or verify a calendar event.
  Do-not-contact and channel restrictions still apply.
- Preserve UTC instants, IANA zones and both DST folds in future-window search.
- Real contacts, drafts and exported recommendations remain private and untracked.
- No LLM, network client, scheduled sender, background worker or cloud deployment in V2.0.

## V2.1 Festival and Follow-up Rules

- Festivals are timing signals, not sending authority. Keep general greetings light;
  never combine a holiday greeting with an aggressive job/referral ask.
- Follow-up requires explicit reply state or separate user action. No reply is not
  permission to chase. Re-running the CLI does not record a send or alter history.
- Never infer religion, ethnicity, nationality or political identity from location.
  Use explicit festival IDs/preferences; region filters are not personal opt-ins.
- Preserve human approval. No autonomous outreach, mass-send loop or real contacts
  in tracked fixtures. Keep all actual history in ignored private snapshots.
- V2.0 timing restrictions remain authoritative. Do not sacrifice user sleep/rest
  to catch another timezone; V2.1 also checks sender quiet hours.
- Frequency overrides must be explicit input edits and cannot bypass hard blocks.
- Separate cultural dates from official holiday periods. No guessed lunar dates;
  unsupported years must be UNKNOWN. Keep source/date/scope in configuration.
- PCV integration is reference-only: PTime decides WHEN; content systems decide WHAT.

## V2.3 Markov Chain / Discrete-Time Design

V2.3 adds a state-transition view of personal time:

`T -> T+1 -> T+2`

At each meaningful decision boundary, evaluate both:
1. immediate value; and
2. the quality/probability of the next state created by the current action.

Practical model:

`P(S[t+1] | S[t], A[t])`

This is a useful operating approximation, not a claim that human behavior is literally
memoryless. Sleep debt, energy, attention, location, mission clarity and unfinished work
should be represented inside the current state.

Core rules:
- purposeful exploration is valid while information gain remains positive;
- when information gain saturates, close or transition to a named purpose;
- uncontrolled drift can self-propagate across several states;
- recovery / sleep is a first-class transition and can be the best action when there
  is no strong next T;
- optimize cumulative AlphaTime density and next-state quality, not raw waking hours.

Read `docs/MARKOV_CHAIN_DISCRETE_TIME_MANAGER.md` and `releases/V2.3.md`
before implementing this feature.

## Version Protocol

Before any version work, read `version/LATEST.md` and `version/AGENT.md`.

SemVer: PATCH = fixes/small rule changes, MINOR = new capability/adapter, MAJOR = mission
or architecture expansion. Version history is monotonic and append-only: never move a
latest/current pointer backward or call an older version current.

The implemented package version and design/spec version are separate tracks. A spec may
be ahead, but `VERSION`, pyproject.toml and `ptime.__version__` advance only after
implementation, tests, packaging smoke checks and release metadata are complete.

Update VERSION, pyproject.toml, ptime.__version__, CHANGELOG.md and VERSION.md together
for an implemented package release. For major/minor releases add releases/Vx.y.md and
update README/AGENT when behavior changes.

Do not mark a version closed while required tests or publication are outstanding.
