# PTime V2.1 — Festival Timing, General Greeting & Follow-up

Status: CLOSED / PUBLISHED (documented environment limits retained)
Package version: 2.1.0
Plan date: 2026-09-25
Previous stable version: 2.0.0

## Why V2.1

PTime V2.0 solves global professional timing by combining timezone, region, relationship, channel and opportunity.

V2.1 adds festival / cultural timing, follow-up state and relationship lifecycle.

The purpose is to make recurring relationship maintenance easier, more natural and more global.

## Relationship model

PCV Self-Introduction:
first contact -> establish identity.

PTime General Greeting:
existing relationship -> maintain warmth / reconnect.

PTime Follow-up:
reply / prior interaction -> next communication window.

Combined lifecycle:

Self Introduction -> Conversation -> Follow-up -> Festival / Periodic Touchpoint -> Reconnect -> DD / Coffee Chat / Collaboration / Recruiting.

## Implemented calendar layers

Chinese / Greater China:
- Mid-Autumn Festival
- National Day
- New Year
- Spring Festival
- Lantern Festival
- Dragon Boat Festival

Global shared:
- New Year
- Christmas

United States:
- Thanksgiving
- Independence Day
- Memorial Day
- Labor Day

United Kingdom:
- Christmas
- New Year
- Easter
- Early May Bank Holiday
- Spring Bank Holiday
- Summer Bank Holiday
- optional future Boxing Day / region-specific variants (not implemented)

## Implemented capabilities

- General / Professional / Reconnect greeting library
- bilingual Chinese / English templates
- festival-aware touchpoint ranking
- region-aware calendars
- duplicate greeting suppression
- recent-contact suppression
- reply-aware follow-up eligibility
- PCV self-introduction integration contract
- human approval for every communication action
- no autonomous sending

## Version boundary

Implementation and baseline tests were completed before atomically updating package
version surfaces to 2.1.0. Final versioned wheel, public review and remote refs
pass. Main and v2.1.0 were atomically published and verified at 54d5b21.
Historical CODEX/plan notes are retained; V2.2 remains planning-only.

342 tests pass on Python 3.11.3; the source-independent final 2.1.0 wheel smoke passes
all eight commands. Python 3.12 revalidation is blocked by temporary-directory access
and unavailable approval review, not claimed as passed. The [implementation log](../../logs/2026-09-25-ptime-v2.1-implementation.md)
tracks current final gates. See the [input contract](../../docs/v2.1-contract.md).

Lunar festivals and UK variable dates are explicit 2026-2027 tables. Four calendar
views share canonical IDs; 15 events and 54 templates. Full UK division calendars,
China makeup working days and private availability are not implemented. No auto-send.

## Release goal

PTime should become better at managing:
- timezone timing
- festival timing
- follow-up timing
- relationship-maintenance timing

The goal is not more messages.

The goal is better timing and better relationship continuity.
