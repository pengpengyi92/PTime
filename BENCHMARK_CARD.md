# Benchmark Card - PTime V0.1

## Baseline

No PTime implementation existed locally or at the checked GitHub repository path.
The fixed-offset/manual-clock approach cannot model DST. No measured legacy latency,
contact-ranking quality or response-rate baseline exists: **UNMEASURED**.

## Change

IANA zoneinfo conversion; two deterministic agents; configurable rule/scoring policy;
normalized local contact adapters; hard contact gates; text/JSON CLI and packaged defaults.

## Measure

Fixed evaluation fixture: 2026-09-21T22:15 Asia/Shanghai.
Synthetic contacts only. No live users, outbound calls or private data.

Protocol:
1. Run the complete pytest suite.
2. Check both CLI commands and opt-in demo.
3. Build a wheel, install it in an isolated local environment, run it outside source root.
4. Inspect staged files and published repository visibility/ref.

## Result

- Python 3.11.3 / Windows, pytest 8.4.2, tzdata 2026.2: **124 passed in 0.61s**.
- Python 3.12.13 / Windows, pytest 9.1.1, tzdata 2026.4: **124 passed in 0.74s**.
- Wheel build PASS; installed-wheel smoke PASS outside the source directory on both versions.
- Installed smoke verifies current time, nine regions, empty contact default and explicit
  four-contact synthetic demo with two eligible/two deferred at the fixed instant.
- Public staging review: 41 files, no ignored/private paths or credential/email patterns.
- macOS/Linux execution and native CRM exports: **NOT_VERIFIED**.
- The dated fixture yields London 15:15 and NY/Boston 10:15, with SG evening deferred.
- Actual contact availability, response rate and opportunity conversion: **UNMEASURED**.
- Throughput and latency benchmark: **UNMEASURED**; unit-test duration is not product latency.

## Trade-off

Rules are transparent and reproducible but not personalized or empirically calibrated.
Conservative gates can suppress some welcome evening conversations. Local normalized
exports require manual preparation but avoid hidden APIs and accidental private-data collection.

## Next Action

Complete remote publication verification; then validate a user-selected private fixture without
publishing contacts or claiming a real-world ranking improvement.
