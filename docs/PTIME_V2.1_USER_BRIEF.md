PTime V2.1 — Festival Timing, General Greeting & Follow-up Upgrade

Status: PLANNED
Target version: 2.1.0
Plan date: 2026-09-25
Current stable version: 2.0.0

1. Upgrade Mission

Upgrade PTime from a timezone/channel-aware communication router into a broader Timing & Follow-up Coordination Layer.

PTime V2.1 must add festival-aware relationship timing while preserving the lightweight, human-approved architecture introduced in V2.0.

The new system should answer not only:

* Who can I talk to right now?
* Which region is currently inside a working window?
* Which channel is appropriate?

It should also answer:

* Is there a culturally natural reason to reconnect now?
* Is an upcoming festival a good relationship-maintenance touchpoint?
* Which greeting style fits this contact?
* Should this be a general greeting, a professional greeting, or a reconnect greeting?
* If the contact replies, when should a deeper follow-up happen?

Core objective:

TIME
+ REGION
+ PEOPLE
+ RELATIONSHIP
+ CHANNEL
+ OPPORTUNITY
+ FESTIVAL / CALENDAR CONTEXT
-> COMMUNICATION ACTION

PTime remains a timing and recommendation layer.

It must NOT become a full CRM, mass-messaging engine, autonomous sender, social scraper, or relationship-manipulation system.

⸻

2. Product Philosophy

PTime V2.0 established:

P Connection = WHO
P Global = WHERE
PTime = WHEN
P Email / P LinkedIn = HOW

PTime V2.1 adds:

Festival / Calendar = WHY NOW

New compact model:

WHO
x WHERE
x WHEN
x HOW
x WHY NOW
-> ACTION

A festival is not a command to send.

It is a naturally occurring communication window that may reduce friction for relationship maintenance.

The system should recommend opportunities, not force outreach.

⸻

3. Relationship Lifecycle

First Contact

PCV Self-Introduction Kit:

New Connection
-> First Introduction
-> Identity / Background / Current Focus
-> Permission-safe Context
-> Conversation

Typical channels:

* WeChat
* LinkedIn
* Email
* messaging apps

PCV owns the reusable self-introduction content.

PTime only helps determine when it is appropriate to send or follow up.

PCV should eventually maintain:

self_intro.zh-CN
self_intro.en

plus optional role-specific or geography-specific variants.

The English version is especially important for global communication.

Existing Relationship

PTime General Greeting:

Existing Connection
-> Festival / Calendar Timing
-> Light Greeting
-> Reply or No Reply
-> Optional Follow-up

Full lifecycle:

Self Introduction
-> Conversation
-> Follow-up
-> Festival / Periodic Touchpoint
-> Reconnect
-> DD / Coffee Chat / Collaboration / Recruiting
-> Continued Relationship

PTime should support this lifecycle without storing unnecessary private relationship history.

⸻

4. General Greeting Library

Add a reusable General Greeting system.

Required styles:

General

Broadly reusable.

Short.

Warm.

No job ask.

No referral ask.

No hard CTA.

Professional

Suitable for:

* colleagues
* recruiters
* alumni
* institutional contacts
* managers
* professional acquaintances

May include one light sentence such as:

很高兴之前有机会认识和交流，之后有机会再多聊聊。

Still no hard referral ask inside the greeting itself.

Reconnect

Suitable for:

* dormant contacts
* prior informal meetings
* previous recruiters
* alumni
* professional contacts not spoken to recently

May include one short update such as:

最近我也在推进一些新的工作和研究方向，之后有机会再找你聊聊。

The purpose is to reopen the conversation naturally.

⸻

5. Calendar Architecture

PTime V2.1 must support multiple calendar views.

Do not create only one generic Global Calendar.

Use layered calendars.

5.1 Chinese / Greater China Calendar

Initial set:

* Mid-Autumn Festival
* National Day
* New Year
* Spring Festival / Lunar New Year
* Lantern Festival
* Dragon Boat Festival

Optional future additions:

* Qingming Festival
* Double Ninth Festival
* region-specific Hong Kong public holidays
* region-specific Macau public holidays

Important:

The cultural festival date and the government holiday period are not necessarily the same thing.

Store these separately.

Example:

Mid-Autumn Festival Date
!=
Official Holiday Period

⸻

5.2 Global Shared Calendar

Initial shared set:

* New Year
* Christmas

These may be globally relevant but still require relationship/context checks.

⸻

5.3 United States Calendar

Initial set:

* Thanksgiving
* Independence Day
* Memorial Day
* Labor Day

Optional:

* Martin Luther King Jr. Day
* Presidents’ Day
* Veterans Day

Do not assume every public holiday is greeting-worthy.

Each festival or holiday needs a:

greeting_appropriate

flag.

⸻

5.4 United Kingdom Calendar

Initial set:

* Christmas
* New Year
* Easter
* Early May Bank Holiday
* Spring Bank Holiday
* Summer Bank Holiday

Optional:

* Boxing Day
* England-specific dates
* Wales-specific dates
* Scotland-specific dates
* Northern Ireland-specific dates

Again, not every bank holiday should automatically trigger outreach.

⸻

5.5 Other Regional Calendars

Architecture must remain extensible for:

* Hong Kong
* Singapore
* Europe
* Australia
* Middle East
* country-specific cultural holidays

Region-specific calendars should be configuration-driven rather than hardcoded into routing logic.

⸻

6. Festival Data Model

Add a Festival model.

Suggested fields:

id
name
canonical_name
locale
country_or_region
region_tags
calendar_type
cultural_date_rule
official_holiday_period
default_timezone
greeting_appropriate
professional_greeting_appropriate
reconnect_appropriate
suggested_channels
lead_days
valid_window_days
enabled
source_note

Example:

festival_id: mid_autumn
region_tags:
  - CN
  - HK
  - SG_CHINESE
calendar_type: chinese
greeting_appropriate: true
professional_greeting_appropriate: true
reconnect_appropriate: true

Do not infer religion, ethnicity, or sensitive identity from a person’s location.

Festival relevance must be based only on explicit contact metadata or user-selected applicability.

⸻

7. Greeting Template Data Model

Add GreetingTemplate.

Fields:

id
festival_id
style
locale
audience
channel
message
personalization_slots
active

Style enum:

general
professional
reconnect

Audience examples:

general
friend
colleague
recruiter
alumni
professional_contact
institutional_contact

Templates must remain public-safe and generic.

Do not commit:

* real names
* private contact data
* confidential job information
* employer-specific sensitive information

⸻

8. Festival Touchpoint Model

Add FestivalTouchpoint.

Suggested fields:

contact_id
festival_id
relationship_class
recommended_template_id
recommended_channel
reason
state
not_before
expires_at
last_contact_at
duplicate_suppressed
recent_contact_suppressed
reply_state
followup_eligible_at
user_approval_required

Suggested states:

SUGGEST
WAIT
SKIP
BLOCKED
GREETED
REPLIED
FOLLOW_UP_ELIGIBLE
CLOSED

PTime must never interpret SUGGEST as authorization to send.

⸻

9. Follow-up Timing

Festival greeting is only the first touchpoint.

The larger V2.1 objective is to improve PTime’s follow-up management.

Core flow:

Festival Greeting
-> Reply
-> Conversation
-> Context Update
-> Follow-up Timing
-> DD / Coffee Chat / Career Update / Collaboration / Recruiting
-> Human Decision

Rules:

1. Do not recommend immediate hard asks after a greeting by default.
2. If the person replies naturally, PTime may mark the relationship as FOLLOW_UP_ELIGIBLE.
3. Follow-up timing should consider:
    * reply timestamp
    * timezone
    * working window
    * relationship class
    * prior follow-up frequency
    * due date
    * opportunity urgency
    * channel
4. No-reply should not trigger aggressive repeated messages.
5. Respect do-not-contact and cooldown windows.
6. Follow-up recommendations remain advisory.

⸻

10. PCV Self-Introduction Integration

PTime V2.1 must document conceptual integration with the PCV Self-Introduction Kit.

The two systems serve different lifecycle stages.

PCV Self-Introduction

Purpose:

* first contact
* identity establishment
* bilingual/global introduction
* Chinese version
* English version
* later region-aware variants

PTime General Greeting

Purpose:

* existing contact
* relationship maintenance
* festival timing
* reconnect
* follow-up

Recommended interface:

PCV produces:

self_intro.zh-CN
self_intro.en
optional role-specific variants

PTime consumes only a reference or template ID, not private PCV content unless explicitly supplied.

Do not tightly couple repositories.

PTime should expose a simple adapter contract such as:

communication_asset_type:
- self_introduction
- greeting
- follow_up
- thank_you
- career_update

Core responsibility split:

PTime decides WHEN.
The content system decides WHAT.

⸻

11. Suggested Repository Structure

Suggested new structure:

ptime/
  festivals/
    models.py
    calendar.py
    router.py
    rules.py
  greetings/
    models.py
    templates.py
    renderer.py
  followups/
    models.py
    rules.py
    router.py
config/
  festivals/
    chinese.yaml
    global.yaml
    united_states.yaml
    united_kingdom.yaml
  greetings/
    general.yaml
    professional.yaml
    reconnect.yaml
data/
  festivals.example.yaml
  greetings.example.yaml
  touchpoints.example.yaml

Keep the implementation small and composable.

Do not add unnecessary databases or services.

⸻

12. CLI Scope

Recommended commands.

Festivals

ptime festivals
ptime festivals --region china --days 30
ptime festivals --region united_kingdom --days 60
ptime festivals --region united_states --days 60

Purpose:

Show upcoming greeting-relevant festivals.

Greetings

ptime greetings --festival mid_autumn --style general --locale zh-CN
ptime greetings --festival christmas --style professional --locale en

Purpose:

Preview reusable templates.

Touchpoints

ptime touchpoints --festival mid_autumn --demo
ptime touchpoints --region united_states --days 30 --demo

Purpose:

Rank relationship-maintenance opportunities from explicit local snapshots.

Follow-ups

Optional V2.1 command:

ptime followups --demo

Purpose:

Show eligible follow-up windows after explicit prior interaction state.

No command should send messages.

⸻

13. Initial Greeting Templates

Mid-Autumn — General

中秋快乐！祝你和家人节日愉快，事事顺心，最近一切都好～🌕🥮

Mid-Autumn — Professional

中秋快乐！祝你和家人节日愉快、诸事顺利。也很高兴之前有机会认识和交流，之后有机会再多聊聊！

Mid-Autumn — Reconnect

中秋快乐！最近还好吗？祝你和家人节日愉快、事事顺心～最近我也在推进一些新的工作和研究方向，之后有机会再找你聊聊！

Add equivalent English examples for global testing.

Future English examples should cover:

* Christmas
* New Year
* Thanksgiving
* UK-specific professional greetings

Greeting copy should live in configuration rather than core logic.

⸻

14. Routing Rules

Festival timing must respect existing V2.0 constraints.

Festival relevance NEVER overrides:

* do-not-contact
* quiet time
* channel restrictions
* explicit relationship preferences
* recent-contact suppression
* duplicate festival greeting suppression
* terminal action states

Suggested scoring factors:

festival relevance
relationship relevance
region fit
timezone fit
recency
channel fit
opportunity relevance
user priority

Priority cannot override hard blocks.

⸻

15. Duplicate / Frequency Controls

Required protections:

* one greeting per contact per festival cycle unless user explicitly resets
* suppress if contacted very recently
* suppress if already in an active conversation unless user chooses otherwise
* suppress if the same greeting template was already used
* avoid multiple festival greetings across different channels to the same person by default
* allow manual override only through explicit user action

Goal:

relationship maintenance, not spam.

⸻

16. Cultural Safety

Do not infer:

* religion
* ethnicity
* nationality
* political identity
* sensitive personal traits

from contact location alone.

A contact in the United States should not automatically receive every US cultural or religious greeting.

A contact in China should not automatically receive every Chinese cultural greeting.

Use:

* explicit region metadata
* explicit user-selected festival applicability
* explicit contact preference
* known professional context

Default to conservative suggestions.

⸻

17. README Upgrade

Add a new README section:

Festival Timing & Relationship Touchpoints

Explain:

PTime V2.0
=
Timezone / Region / Channel Timing
PTime V2.1
=
Timezone Timing
+ Festival Timing
+ Follow-up Timing
+ Relationship-maintenance Timing

Use this lifecycle:

Self Introduction
        ↓
Conversation
        ↓
Follow-up
        ↓
Festival / Periodic Touchpoint
        ↓
Reconnect
        ↓
DD / Coffee Chat / Collaboration / Recruiting

Explain the PCV relationship:

PCV Self-Introduction
=
First-contact Communication Asset
PTime General Greeting
=
Relationship-maintenance Timing Asset

⸻

18. AGENT.md Upgrade

Add the following rules:

* Festivals are timing signals, not sending authority.
* General Greeting must remain light by default.
* Do not combine a holiday greeting with an aggressive referral ask.
* Follow-up becomes eligible only after explicit reply state or separate user action.
* Do not infer sensitive cultural identity.
* Preserve human approval.
* No autonomous outreach.
* No mass-send logic.
* No real contacts in tracked fixtures.
* Do not sacrifice the user’s sleep/rest merely to catch another timezone.
* Existing V2.0 timing restrictions remain authoritative.

⸻

19. Release Documentation

Update:

releases/V2.1.md
releases/V2.1/README.md
releases/V2.1/CODEX.md
CHANGELOG.md
VERSION.md
README.md
AGENT.md
CODEX.md

Release V2.1 should clearly document WHY:

PTime needs to manage not only clock time, but natural relationship timing.

And WHAT:

* Chinese Calendar
* Global Calendar
* UK Calendar
* US Calendar
* General / Professional / Reconnect greetings
* festival-aware touchpoints
* follow-up timing
* PCV Self-Introduction integration
* bilingual/global communication support

⸻

20. Version Rules

Current stable version:

2.0.0

Target:

2.1.0

Do NOT bump:

VERSION
pyproject.toml
ptime.__version__
VERSION.md current release

until implementation and tests are complete.

When complete, update all version surfaces atomically.

⸻

21. Testing Requirements

Existing V2.0 tests must continue to pass.

Add tests for:

1. Mid-Autumn date handling.
2. Spring Festival yearly date changes.
3. Christmas recurring date.
4. Thanksgiving date rule.
5. UK bank-holiday configuration.
6. Timezone-aware festival boundaries.
7. Multi-day holiday vs festival-date distinction.
8. General / Professional / Reconnect template rendering.
9. Duplicate greeting suppression.
10. Recent-contact suppression.
11. Do-not-contact hard block.
12. Channel restriction.
13. No-reply cooldown.
14. Explicit reply → follow-up eligibility.
15. No sensitive-identity inference.
16. Deterministic CLI output.
17. Fictional demo fixtures only.
18. V2.0 backward compatibility.

Run installed-wheel smoke tests after implementation.

⸻

22. Acceptance Criteria

V2.1 is complete only when:

* Chinese calendar implemented
* Global calendar implemented
* US calendar implemented
* UK calendar implemented
* greeting templates implemented
* festival touchpoint ranking implemented
* duplicate suppression implemented
* follow-up timing implemented
* PCV integration contract documented
* README updated
* AGENT updated
* CHANGELOG updated
* release documentation updated
* all tests pass
* installed-wheel smoke tests pass
* privacy/public-repo review passes

No release should be marked CLOSED before these gates pass.

⸻

23. Product Boundary

PTime V2.1 is NOT:

* a CRM
* an email client
* a LinkedIn client
* a WeChat client
* an auto-sender
* a social scraper
* a people database
* a religious-calendar recommender
* a spam engine

It is:

A lightweight timing and routing layer for global professional communication and relationship maintenance.

⸻

24. Final V2.1 Positioning

PTime V2.0:

TIME
-> WHO
-> CHANNEL
-> ACTION

PTime V2.1:

TIME
+ TIMEZONE
+ FOLLOW-UP STATE
+ FESTIVAL / CULTURAL TIMING
+ RELATIONSHIP
-> NEXT BEST COMMUNICATION WINDOW

Long-run positioning:

PTime = Global Timing Intelligence for Communication, Follow-up and Relationship Maintenance.

The goal is not to communicate more.

The goal is to communicate:

at the right time, for the right reason, with the right person, and with the right level of intensity.