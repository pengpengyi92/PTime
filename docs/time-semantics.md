# Time Semantics

## One Instant, Multiple Views

The core works with aware Python datetimes. The CLI accepts:
- No `--at`: current system UTC instant.
- `2026-09-21T22:15`: wall time in the configured base zone (default Asia/Shanghai).
- `2026-09-21T22:15+08:00`: explicit instant; base zone changes display, not interpretation.
- `2026-09-21T14:15Z`: the same instant.

Date-only and clock-only inputs are rejected. This prevents silently attaching today's
date to a historical example.

IANA zones drive conversion; CST/EST abbreviations and hand-written offsets are not region
identifiers. UTC is also accepted. Python's [zoneinfo documentation](https://docs.python.org/3/library/zoneinfo.html)
describes DST, fold and data sources. The declared `tzdata` dependency is important on
Windows, which may not supply an IANA database. When a system database exists, zoneinfo
may use it first. Keep system and Python timezone data maintained.

## DST Safety

A naive local time is tried with both fold values and round-tripped through UTC.
Zero valid instants means a nonexistent spring-forward time.
Two valid instants means an ambiguous fall-back time.
Both cases fail with actionable errors instead of silently choosing an instant.

For example, `2026-10-25T01:30` in London is ambiguous; use `+01:00` or `+00:00`
after determining which instant is intended. A timezone-aware datetime created directly
by an API caller carries its chosen fold/offset; invalid gap values are rejected.
See Python's [datetime semantics](https://docs.python.org/3/library/datetime.html).

Tests cover London's 2026-03-29 / 2026-10-25 and New York's 2026-03-08 / 2026-11-01
boundaries, including exact UTC instants and wall-time rejection.

## Recipient-Local Decisions

Weekday, contact recency, opportunity deadline and window classification use the
recipient's local date. Monday in Shenzhen can still be Sunday in California.
Windows are half-open and must cover all 1,440 minutes exactly once.

The default 21:00-23:00 weak window remains deferred for friends as well as professional
contacts. Weekend labeling must not override the early or avoid windows.
Holidays, travel and a person's actual workweek are unknown in V0.1.

Scores express a policy preference, not a claim that a person is awake, free or consenting.
