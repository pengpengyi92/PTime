# TODO

## P0 - V0.1 Closure
- [x] Two callable agents, six validated models and nine IANA region configurations.
- [x] Current-time / explicit-time CLI with JSON and useful errors.
- [x] Configurable scores, eligibility gates and transparent explanations.
- [x] Three normalized local adapters; empty-by-default contacts and opt-in synthetic demo.
- [x] Regression tests for DST, midnight, boundaries, ranking, input and privacy safeguards.
- [x] Build and test the installed wheel outside the source directory (Python 3.11 and 3.12).
- [x] Verify staged publication contains only reviewed docs/code and synthetic contacts.
- [ ] Create/verify public GitHub PTime repository and push reviewed V0.1.

## P1 - Evidence-Led Follow-Up
- [ ] With user-selected private data, validate one normalized export from each real source.
- [ ] Compare recommendations against a manually labeled fixed private set before tuning weights.
- [ ] Define an opt-in reply/usefulness evaluation; current real-world outcome is UNMEASURED.

## P2 - Only When Needed
- [ ] Evaluate per-contact schedules and holiday calendars with DST/holiday regression fixtures.
- [ ] Add opt-in source-specific exporters after documenting native field mappings and consent.
- [ ] Design PMap/time-window consumption without coupling it to message sending.
