# PTime Before-Sleep Queue / Next-Day Execution Loop

Date: 2026-09-23

## Core Idea

PTime should manage the transition between one day and the next.

The goal is not to keep working late.

The goal is:

**Before Sleep → Think Through Tomorrow Queue → Sleep → Next-Day Execution → Close**

This creates a clean separation between:
- planning
- recovery
- execution

## Before-Sleep Queue

Before sleep, PTime should generate a short Tomorrow Queue.

Each item should include:
- Who / What
- Why it matters
- Next Action
- Best Time
- Channel
- Deadline
- Close Condition

Example:
- Tencent FIT DD
  - contact target
  - questions
  - desired next step
  - close condition: meeting scheduled / referral / next interview

- HKU DS Student DD
  - student target
  - research topic
  - questions
  - desired next step
  - close condition: call scheduled / research task / PI intro

## Rule

At night:
**Do not open new strategic branches.**

Instead:
1. review open loops
2. select the few highest-value items
3. convert them into Tomorrow Queue
4. stop thinking
5. sleep

## Next-Day Execution

The next day should not restart from uncertainty.

PTime should present:
- Reach Out Now
- Follow Up Due
- DD / Informal Meeting Queue
- Application Next Steps
- Close Queue

Then execution becomes:
**Send → Talk → DD → Follow Up → Next Action → Close**

## Why This Works

It protects ETM-AAO:
- less late-night decision fatigue
- less context switching
- better sleep
- faster morning startup
- clearer priorities
- higher close rate

## PTime Role

PTime evolves from Time Adapter into:

**Time Router + People Router + Opportunity Scheduler + Close Engine**

Before sleep, its job is planning.
During the day, its job is routing.
At the end of the day, its job is closing and re-queuing.

## Daily Loop

**Day Execution**
→ Close / Update Status
→ Evening Review
→ Before-Sleep Tomorrow Queue
→ Sleep
→ Wake
→ Execute Queue
→ Repeat

## Design Principle

Tomorrow's work should be mostly decided before sleep.

Tomorrow should be used for:
**execution, conversation, judgment, delivery, and close**.
