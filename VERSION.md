# PTime Version Record

## Implemented package

Current package version: **2.1.0**.  
Status: **CLOSED / PUBLISHED**, 2026-09-25, with the documented Python 3.12/platform validation limits.  
Canonical implemented value: [VERSION](VERSION).  
Theme: Festival Timing, General Greeting and Follow-up Coordination.

Implementation history:

`0.1.0 -> 2.0.0 -> 2.1.0`

Implementation tag `v2.1.0` resolves locally and remotely to
`54d5b21abf8e457881b0fe3402471474ad99e034`.

## Design / spec track

Highest declared design/spec version: **2.3.0**.  
Status: **SPEC RELEASED / IMPLEMENTATION PENDING**, 2026-10-03.  
Theme: **Markov Chain Discrete-Time Manager**.

Design/spec ordering:

`2.2.0 (planned Temporal Operating Layer) -> 2.3.0 (Markov discrete-time spec)`

V2.3 introduces `T -> T+1 -> T+2` state-transition management: current actions are
evaluated by both immediate value and their effect on the next state. Recovery / sleep
is a first-class transition when continuing would increase drift or sleep debt.

See:
- `version/LATEST.md`
- `version/AGENT.md`
- `releases/V2.3.md`
- `docs/MARKOV_CHAIN_DISCRETE_TIME_MANAGER.md`

## Monotonic version rule

Version history is append-only. A future version must not move backward relative to the
highest version already declared. An older version must never be relabeled as latest.

The canonical package `VERSION` remains **2.1.0** until V2.3 implementation and release
gates are actually completed.