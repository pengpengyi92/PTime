# NOG — AlphaTime Drift-Interrupt Design Handoff

**Date:** 2026-10-09  
**Visibility:** Public-safe generic system note; not a personal activity log.  
**Status:** Design note only (not shipped functionality).

## Decision
A PTime temporal state should carry: intent, current action, context/environment, fatigue risk, drift flag, selected T+1 action, and evidence/Close state.

## Proposed flow
`Detect intent-action divergence → Interrupt → Choose feasible action or Recovery → Handoff → Verify next state.`

## Safety and quality checks
- Explicitly allow recovery and sleep; the goal is next-state quality, not continuous labor.
- Preserve offline, self-directed operation; no covert behavioral tracking.
- Keep operational information generic; do not expose real personal event details in public PTime.
- Do not claim V2.3 implemented. Current package remains 2.1.0.

## Future validation idea
Evaluate user-chosen task-start latency, actual micro-Close presence and next-block readiness in a private test; no metrics are claimed here.