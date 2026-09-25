# EPIC Note — Greeting / Festival Timing Module

Date: 2026-09-25

## New module

Greeting / Festival Timing

Suggested structure:

timing/
  festivals/
    chinese_calendar.yaml
    global_calendar.yaml
  greetings/
    general/
    professional/
    reconnect/
  followups/
  rules/

## Core objects

Festival:
- id
- name
- region
- date_rule
- timezone
- greeting_appropriate
- relationship_types
- suggested_channels

GreetingTemplate:
- id
- festival_id
- style: general | professional | reconnect
- locale
- message
- personalization_slots

FestivalTouchpoint:
- contact_id
- festival_id
- status
- last_touch
- suggested_action
- followup_after_reply

## Routing

Festival Timing
-> relevant contacts
-> relationship class
-> appropriate template
-> human review
-> send externally by user
-> reply / no reply
-> optional follow-up window.

No autonomous sending.

## V2.1 objective

Add festival-aware communication timing on top of PTime V2.0's timezone/channel router.

Chinese Calendar + Global Calendar become first-class timing sources.
General Greeting becomes a reusable template system.
Festival touchpoints should be advisory and human-approved.

## Expanded PTime role

PTime should increasingly manage the full timing layer around people:
- connection timing;
- interview scheduling and preparation windows;
- daily follow-up cadence;
- festival greetings;
- reconnect windows;
- post-reply follow-up;
- progress / artifact update timing.

The system should distinguish intent:
- **maintenance**: lightweight greeting or check-in;
- **reconnect**: reopen a dormant conversation;
- **follow-up**: move an existing thread forward;
- **conversion**: arrange a meeting, interview, DD call, or collaboration;
- **value update**: return with new progress, evidence, or artifacts.

## Design principle

Festival greetings are useful accelerators, but daily follow-up remains the main relationship engine.

Greeting -> maintenance / reconnect.
Daily follow-up -> progress.
Interview / meeting -> conversion.
Artifact / progress update -> value creation.
