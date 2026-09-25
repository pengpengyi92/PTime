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

## Version Protocol

SemVer: PATCH = fixes/small rule changes, MINOR = new capability/adapter, MAJOR = mission
or architecture expansion. This release intentionally jumps from 0.1.0 to 2.0.0; no 1.0.0
release is asserted.

Update VERSION, pyproject.toml, ptime.__version__, CHANGELOG.md and VERSION.md together.
For major/minor releases add releases/Vx.y.md; update README/AGENT when behavior changes.
Run unit regressions and an installed-wheel smoke test before committing/tagging a release.
Do not mark a version closed while required tests or publication are outstanding.
