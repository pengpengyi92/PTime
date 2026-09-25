# Changelog

## [2.1.0] - 2026-09-25

### Added
- Four layered calendars (Chinese/Greater China, shared, US, UK) with 15 canonical
  events, explicit date coverage, source metadata and separate official periods.
- Fifty-four general/professional/reconnect templates, Chinese and English.
- `festivals`, `greetings`, `touchpoints`, `followups` read-only CLI commands.
- Explicit per-contact festival opt-in; canonical-cycle and cross-channel dedup;
  recent-contact, active-conversation and template-reuse suppression.
- Reply/user-action-driven follow-up timing, contact-wide cooldown, stale-reply
  checks, soft due/urgency metadata, terminal state and sender-rest protection.
- PCV reference-only asset contract, synthetic fixture, expanded installed-wheel smoke.

### Compatibility and Safety
- Existing four commands and V2.0 schemas/policies retained. No new dependencies.
- Festivals are not permission to send; geography is not inferred observance.
- Lunar/UK dated tables cover 2026-2027 only; unknown years are explicit.
- No runtime network, persistent contact store, automation, scheduling or messages.
- Initial baseline 241 tests; expanded suite 342 PASS on Python 3.11.3.
  Python 3.12 revalidation is environment-blocked; see the implementation log.

## [2.0.0] - 2026-09-21

### Added
- Global Communication Timing Layer and channel/context-aware contact router.
- Five normalized local communication sources: P Email, P LinkedIn, P Connection,
  P Global and a generic P Kago placeholder; explicit in-memory mock adapter.
- Eight channel policies, four contexts, contact preferences and pending-action lifecycle.
- `ptime talk` and `ptime email`, text/JSON, deterministic explanations and next windows.
- Explicit expected-reply and confirmed-meeting exceptions with human gates.
- DST-aware next-window search, including nonexistent starts and repeated local times.
- AGENT.md, VERSION, release history and version consistency tests.

### Changed
- PTime expands from timezone adapter into global communication timing infrastructure.
- Contact adds IDs, channels, context, aware contact/due timestamps, preferred windows
  and provenance. Legacy constructor fields and commands remain supported.

### Core Philosophy
Time x Region x People x Relationship x Channel x Opportunity -> Communication Action.
TIME -> WHO -> CHANNEL -> ACTION.

### Safety
SEND_NOW does not send, schedule or grant authorization. No real contacts or accounts
are imported. All examples are fictional. Scores remain uncalibrated heuristics.

## [0.1.0] - 2026-09-21

Two deterministic agents, nine IANA regions, validated local adapters, weighted contact
ranking and text/JSON CLI. 124 tests plus installed-wheel checks on Python 3.11/3.12.
First public bootstrap: 5825365; closure: d5844e3.

No V1.0 release exists between these versions.
