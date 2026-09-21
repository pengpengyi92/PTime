# Benchmark Card - PTime V2.0

## Baseline
V0.1 commit d5844e3: two agents, nine regions, three local adapters, now/contacts.
Before edits: **124 tests passed in 0.54s** on Python 3.11.3 / Windows.

## Change
Channel/context-aware router, explicit queue lifecycle, five normalized local integration
classes, next-window search, talk/email and version governance. No new runtime dependencies.

## Measure
Fixed fixture: 2026-09-21T22:15 Asia/Shanghai, synthetic inputs only.
Regression protocol: retain all legacy tests; add eight-channel, four-context, privacy,
pending lifecycle, expected-reply, confirmed-meeting and DST future-window fixtures.
Verify both Python versions and installed wheel outside checkout. Inspect public files and tag.

## Result
- First expanded run: **228 passed in 1.33s** on Python 3.11.3.
- Old 124-test suite still passes unchanged.
- Synthetic email queue: Boston SEND_NOW; Shenzhen WAIT -> 2026-09-22 09:00 +08:00.
- London/NY weekend waits recalculate spring/fall DST offsets.
- Gap/fold fixtures prove next-window search does not fabricate nonexistent wall-clock starts.
- Final Python 3.11.3: **241 passed in 1.45s**; Python 3.12.13: **241 passed in 1.28s**.
- Final wheel build and source-directory-independent smoke: PASS on both versions.
- All four commands, packaged channel policy, both synthetic demos and empty defaults verified.
- Version/package metadata consistency tests PASS. Public tag/push verification pending.
- Actual availability, communication/reply rate and opportunity conversion: **UNMEASURED**.
- Native source integration, macOS/Linux execution: **NOT_VERIFIED**.
- Unit-test wall time is not a routing latency benchmark.

## Trade-off
Conservative explicit inputs avoid invented connectivity and permissions.
Channel-aware exceptions are richer but require recorded context. A confirmed interval is
trusted user input, not calendar evidence. One ruleset does not capture every work culture.
The bounded search returns no suggestion beyond its horizon instead of guessing.

## Next Action
Complete publication checks, then evaluate a fixed private user-labeled
dataset without claiming real-world improvement from unit-test results.
