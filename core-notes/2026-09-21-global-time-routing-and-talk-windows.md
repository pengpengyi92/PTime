# Global Time Routing and Talk-Window Model

Date: 2026-09-21
Status: Core design note

## Mission

PTime is not a clock. It is a global communication router.

```text
P Connection = WHO
P Global     = WHERE
PTime        = WHEN
P Email / P LinkedIn / adapters = HOW

WHO x WHERE x WHEN x HOW -> ACTION
```

The system should answer: given the current base time, which people, regions and communication actions are appropriate now?

## Work Zone != Talk Zone

A local workday must be decomposed into lower-friction and higher-friction micro-windows.

Proposed timing states:

- PRIME_TALK: strong synchronous window.
- LIGHT_TALK: short synchronous conversation may fit.
- ASYNC: prefer email / LinkedIn / message.
- REST: defer professional outreach.
- BLOCKED: preference / policy / quiet-hours gate prevents outreach.

Recommended duration should be explicit:

- 15m
- 30m
- 45m
- 60m

A lunch window may be suitable for 15-30 minutes but not for an assumed 60-minute deep dive.

## Shenzhen -> Boston

During US daylight-saving time in September 2026, Shenzhen is 12 hours ahead of Boston.

```text
22:00 Shenzhen -> 10:00 Boston
23:00 Shenzhen -> 11:00 Boston
00:00 Shenzhen -> 12:00 Boston
```

This supports a Shenzhen late-evening / Boston late-morning learning and outreach window.

Suggested default interpretation:

- 10:00-11:30 Boston -> PRIME_TALK
- 12:00-13:30 Boston -> LIGHT_TALK / lunch; prefer 15-30m
- longer sessions -> require explicit agreement / calendar confirmation

The offset is not permanent. DST must always be calculated with IANA zoneinfo.

## Shenzhen -> London

China evening overlaps with the London workday. London should be surfaced before or alongside the US East Coast depending on current time and contact priority.

Conceptual handoff:

```text
Asia active
-> Asia closing / London active
-> London closing / US East active
-> US West opening
```

## Routing Function

Target model:

```text
Current Time
x Region
x Person
x Relationship
x Opportunity
x Local Work Window
x Micro Window
x Channel
x Duration
x Explicit Preference
-> Next Best Communication Action
```

## Product Requirement

PTime should eventually expose:

- local time and DST-aware offset;
- work-zone state;
- talk-zone state;
- recommended meeting duration;
- recommended channel;
- reason / friction explanation;
- next acceptable window;
- human-approval requirement;
- optional calendar verification state.

## Philosophy

The objective is not to work continuously across every global time zone.

The objective is:

> Use the right hour for the right geography, person, channel and conversation length.

That converts global time-zone separation into communication optionality without violating rest and availability boundaries.
