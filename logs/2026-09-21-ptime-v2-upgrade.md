# PTime V2.0 Upgrade - 2026-09-21

## Request
Upgrade to a lightweight Global Communication Timing Layer:
WHO x WHERE x WHEN x HOW -> ACTION.
Retain V0.1, add five communication sources, channel/context timing, talk/email and version governance.
No website/cloud, LLM, database, background scheduler, email client or autonomous sending.

Source: docs/PTIME_V2.0_CODEX_SPEC.md. Illustrative person names were genericized before
public preservation; the original attachment remains local. New fixtures are all fictional.

## Audit and Baseline
- Fetched origin; remote/local main both d5844e3. No newer remote changes.
- Working tree clean before edits; implementation branch codex/ptime-v2-communication-routing.
- Existing baseline: 124 tests passed in 0.54s (Python 3.11.3).
- Existing normalized adapters, validated dataclasses, zoneinfo and argparse retained.
- Other system repositories were not modified or scanned for private people.

## Implementation
- Extended Contact with ID/channels/context, aware timestamps, preferences and source labels.
- PendingAction and RoutedAction separate queued input from advisory output.
- Five local snapshot readers plus mock interface. No invented native APIs.
- Eight channel policies and four contexts. Conservative preferences, local weekdays,
  not-before times, terminal states and explicit exceptions.
- Future-window candidates use real UTC instants, local boundaries, both DST folds and
  timezone transitions. No fake wall-clock start is returned in a spring gap.
- talk suggests one best channel per unqueued contact and evaluates explicit queue items.
- email evaluates only supplied email records, never creates drafts.
- SEND_NOW remains advisory; approval and calendar-unverified fields are always present.

## Version Decision
The approved mission is V2.0, so 0.1.0 jumps directly to 2.0.0.
V1.0 is recorded as not released, not retroactively invented.
VERSION, package metadata/runtime version, AGENT, CHANGELOG and release docs maintained together.

## Evidence and Remaining Work
- Initial expanded suite: 228 passed in 1.33s; all 124 legacy tests retained.
- Dated demo: London/Boston eligible; Shenzhen email next day at 09:00 +08:00;
  California LinkedIn waits for 08:00 local; Singapore friend needs an explicit late preference.
- Final regression: Python 3.11.3 241 passed in 1.45s; Python 3.12.13 241 passed in 1.28s.
- Final wheel built, installed in both local test environments and smoke-tested outside
  the checkout. All four commands, packaged channels, empty inputs and both demos PASS.
- Fixed a final-review edge case: late friend preferences cannot bypass interview/coffee
  timing. Pending-action kind now controls follow-up explanations; do-not-contact remains
  BLOCKED even when no channel is recorded. Added targeted regressions.
- Existing Python 3.12 sandbox temp-directory restriction used approved normal-permission
  test runs; uv used a project-local ignored cache. No global dependencies were changed.
- Public-file audit PASS: 66 tracked files and 17 local Markdown links.
  Private/export/dependency paths excluded; only reserved example email addresses found.
  No token/private-key signatures or ungenericized illustrative person names in public files.
- Real calendar availability, native source integration and reply/connection outcomes are
  NOT_VERIFIED / UNMEASURED. No real messages, meetings or private profiles used.

## Publication and Closure
- Commit: 4eaae66acd9b63a551c5a33c26b8458e39562665.
- Message: feat: upgrade PTime to global communication timing layer v2.0.
- Main fast-forwarded from the implementation branch, with no history rewriting.
- Main and annotated v2.0.0 tag pushed atomically.
- Remote tag object a1d81070bb28c9e9fc4bb97abb18fad48b6c438d resolves to the implementation commit.
- Workspace PROJECTS.md updated; unrelated repository contents preserved.
- This final documentation receipt follows publication; the release tag remains immutable.

**PTIME V2.0 CLOSED**
