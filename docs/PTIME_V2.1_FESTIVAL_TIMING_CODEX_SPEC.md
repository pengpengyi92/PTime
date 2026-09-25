# PTime V2.1 — Festival Timing & General Greeting Upgrade Spec

Status: PLANNED
Date: 2026-09-25

## Mission

Extend PTime V2.0 from timezone/channel-aware communication routing into festival-aware relationship timing.

PTime V2.1 should add:
- Chinese / Greater China festival calendar;
- Global festival calendar;
- General Greeting template library;
- Professional and Reconnect variants;
- festival-aware contact recommendations;
- reply-triggered follow-up timing;
- human approval gates.

Do NOT turn PTime into a CRM or autonomous sender.

## Core equation

Time
x Region
x People
x Relationship
x Channel
x Opportunity
x Festival
-> Communication Action

Compact form:

WHEN
+ WHO
+ WHERE
+ HOW
+ WHY NOW
-> ACTION

## New concept: Festival Timing

Festivals are recurring temporal opportunities for relationship maintenance.

Examples:

Chinese / Greater China:
- Mid-Autumn Festival
- National Day
- New Year
- Spring Festival
- Lantern Festival
- Dragon Boat Festival

Global:
- New Year
- Christmas
- Thanksgiving
- Easter
- configurable region-specific public holidays.

Festival presence alone must never force outreach.

PTime should evaluate:
- relationship relevance;
- cultural / regional fit;
- channel fit;
- recent-contact suppression;
- do-not-contact rules;
- quiet time;
- duplicate greeting suppression;
- whether a greeting was already sent this festival cycle.

## New module structure

Suggested:

ptime/
  festivals/
    calendar.py
    models.py
    router.py
  greetings/
    models.py
    templates.py
    renderer.py

config/
  festivals.china.yaml
  festivals.global.yaml
  greeting_templates.yaml

## Data models

Festival:
- id
- name
- locale
- region_tags
- date_rule
- default_timezone
- greeting_appropriate
- suggested_channels
- enabled

GreetingTemplate:
- id
- festival_id
- audience
- locale
- style
- text
- personalization_slots

style enum:
- general
- professional
- reconnect

FestivalTouchpoint:
- contact_id
- festival_id
- state
- recommended_channel
- recommended_template_id
- reason
- not_before
- expires_at
- followup_state

Touchpoint states:
- SUGGEST
- WAIT
- SKIP
- BLOCKED
- GREETED
- REPLIED
- FOLLOW_UP_ELIGIBLE
- CLOSED

## Greeting library behavior

General:
light, broadly reusable, no job/referral ask.

Professional:
slightly more formal; appropriate for colleagues, recruiters, alumni, institutional contacts.

Reconnect:
may include one light sentence indicating recent work/research and openness to reconnect.

The greeting itself should not include a hard referral request.

## Follow-up conversion

Festival Greeting
-> Reply
-> Conversation
-> Context Update
-> Optional DD / Coffee Chat / Collaboration / Recruiting Follow-up

PTime should only recommend the next step. It must not send messages or infer consent.

## CLI scope

Recommended additions:

ptime festivals
- show upcoming relevant festivals

ptime greetings
- preview templates by festival/style/locale

ptime touchpoints
- rank festival-based contact opportunities from explicit local contact snapshots

Optional examples:

ptime festivals --region china --days 30
ptime greetings --festival mid_autumn --style general --locale zh-CN
ptime touchpoints --festival mid_autumn --demo

## Calendar design

Use explicit calendar data and/or deterministic festival date logic.

Requirements:
- timezone-aware festival date boundaries;
- support multi-day holidays separately from the festival day;
- distinguish cultural festival from government holiday period;
- configurable region applicability;
- tests for yearly date changes.

Do not assume that every contact in a region celebrates every festival.

## Privacy / safety boundaries

- no automatic sending;
- no scraping contacts;
- no inferred religion or sensitive identity;
- no unsolicited high-frequency outreach;
- no bypassing do-not-contact;
- no private contact data committed to repo;
- templates remain generic/public-safe;
- all examples fictional.

## Acceptance criteria

1. Existing V2.0 tests remain passing.
2. New festival calendar tests cover at least Chinese and Global calendars.
3. Duplicate greeting suppression works.
4. Recent-contact suppression works.
5. Do-not-contact remains absolute.
6. Festival relevance never overrides quiet/channel restrictions.
7. General/Professional/Reconnect templates render deterministically.
8. Follow-up suggestions require explicit reply state or separate user action.
9. Demo fixtures use fictional contacts only.
10. README, AGENT.md, CHANGELOG, VERSION.md and release record are updated together when implementation is complete.

## Version policy

Current release: 2.0.0.
Target release: 2.1.0.

Do not change VERSION / package metadata to 2.1.0 until implementation, tests and release acceptance are complete.

## Deliverables

- implementation;
- tests;
- sample festival calendars;
- template library;
- CLI commands;
- README section;
- AGENT rules;
- changelog;
- release document;
- benchmark / test evidence;
- migration compatibility with V2.0.
