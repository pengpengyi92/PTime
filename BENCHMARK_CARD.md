# Benchmark Card - PTime V2.1

## Baseline
V2.0 local f347fa7: 241 tests PASS on Python 3.11.3 / Windows (3.22s).
Remote documentation was fast-forwarded to 3ae8b04, then bf8d4f2. The latter's
V2.2 plans remain plans, not implemented release claims.

## Change
Four calendars, 15 canonical festivals, 54 bilingual templates, explicit touchpoint
preferences/history and reply/user-action follow-up routing. Four additive CLI
commands reuse V2 timing policy with sender-rest protection. No new dependency.

## Measure
Falsifiable question: do festival suggestions preserve existing timing/privacy gates
while producing deterministic, source-supported calendar and follow-up output?
Fixed synthetic evaluation instant: 2026-09-25T10:00+08:00. Retain the 241 baseline
cases; add 101 date, DST, dedup, opt-in, cooldown, rendering and invalid-input cases.
Build the 2.1.0 wheel; install without source/editable fallback and run all eight
commands from a temporary working directory. Review changed public files and links.

## Result
- Final regression: **342 passed in 3.81s**, Python 3.11.3 / Windows.
- Versioned 2.1.0 wheel built and installed; source-independent smoke **PASS**:
  eight commands plus console entry point, four calendars, six bilingual/style
  previews, empty defaults and three explicitly synthetic demos.
- Fixed festival demo: SUGGEST 1, FOLLOW_UP_ELIGIBLE 1, GREETED 1, SKIP 1, BLOCKED 1.
- Public change review: only fictional contact fixtures and generic templates;
  no private exports, dependencies or credential-pattern matches. Local links pass.
- Main and annotated v2.1.0 pushed atomically; remote tag resolves to
  54d5b21abf8e457881b0fe3402471474ad99e034, matching the local implementation.
- Python 3.12 full regression **NOT_VERIFIED**: temporary-path permission failures;
  elevated retry unavailable due approval-review usage limit. No bypass attempted.
- macOS/Linux and native source integrations **NOT_VERIFIED**.
- Actual availability, reply rates, productivity and relationship outcomes **UNMEASURED**.
- Test wall time is not a routing throughput or latency benchmark.

## Trade-off
Conservative explicit opt-in and complete local history can suppress useful greetings.
Lunar/UK dated rules cover 2026-2027 only; unknown years are visible, never invented.
No full working-day calendar, inferred identity, actual calendar availability,
persistent sender, or automatic outreach. A reply permits advice, not sending.

## Next Action
Evaluate a fixed private user-labeled set and rerun Python 3.12 when permitted.
Do not tune scores based solely on unit tests or claim improved communication outcomes.

---

# Historical Benchmark Card - PTime V2.0

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
- Version/package metadata consistency tests PASS.
- Public review: 66 tracked files, 17 local Markdown links PASS; only synthetic contact
  examples and reserved example email addresses. No private exports/dependencies tracked.
- main and v2.0.0 pushed atomically; remote annotated tag resolves to
  4eaae66acd9b63a551c5a33c26b8458e39562665 (implementation).
- Actual availability, communication/reply rate and opportunity conversion: **UNMEASURED**.
- Native source integration, macOS/Linux execution: **NOT_VERIFIED**.
- Unit-test wall time is not a routing latency benchmark.

## Trade-off
Conservative explicit inputs avoid invented connectivity and permissions.
Channel-aware exceptions are richer but require recorded context. A confirmed interval is
trusted user input, not calendar evidence. One ruleset does not capture every work culture.
The bounded search returns no suggestion beyond its horizon instead of guessing.

## Next Action
Evaluate a fixed private user-labeled
dataset without claiming real-world improvement from unit-test results.
