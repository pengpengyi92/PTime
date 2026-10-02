# PTime Global Time Mental Router — Hong Kong Base

- Date: 2026-10-02
- Base zone: Asia/Hong_Kong (UTC+8)
- Purpose: instant mental conversion for global communication, with IANA/DST verification before important calls.

## Core formula

```text
Target local time = Hong Kong time + target offset from HK
```

Then adjust the calendar date if the result crosses 00:00 or 24:00.

## High-frequency routes

### United Kingdom / London

```text
London summer (BST, UTC+1): HK - 7h
London winter (GMT, UTC+0): HK - 8h
```

Mental rule:
> **UK = subtract 7 or 8 hours.**

Use `Europe/London` for exact DST-aware conversion.

### Boston / US East

```text
Boston summer (EDT, UTC-4): HK - 12h
Boston winter (EST, UTC-5): HK - 13h
```

Mental rule:
> **Boston = subtract 12 or 13 hours.**

Use `America/New_York` for exact DST-aware conversion.

## Australia — do not treat as one time zone

### Sydney / Melbourne / Canberra / Hobart

Standard time:
```text
AEST = UTC+10
HK -> SYD/MEL = +2h
```

Daylight time:
```text
AEDT = UTC+11
HK -> SYD/MEL = +3h
```

For 2026, DST begins Sunday 2026-10-04 at 02:00 local and ends on the first Sunday of April.

Mental rule:
> **Sydney/Melbourne = HK +2h in standard time, +3h in daylight time.**

Always verify with `Australia/Sydney` or `Australia/Melbourne`.

### Brisbane

Queensland does not observe DST.

```text
AEST = UTC+10
HK -> Brisbane = +2h year-round
```

Use `Australia/Brisbane`.

### Adelaide

Standard time:
```text
ACST = UTC+9:30
HK -> Adelaide = +1h30m
```

Daylight time:
```text
ACDT = UTC+10:30
HK -> Adelaide = +2h30m
```

Mental rule:
> **Adelaide = HK +1.5h standard / +2.5h daylight.**

Use `Australia/Adelaide`.

### Perth

Western Australia does not observe DST.

```text
AWST = UTC+8
HK -> Perth = +0h
```

Mental rule:
> **Perth = Hong Kong time.**

Use `Australia/Perth`.

### Darwin

Northern Territory does not observe DST.

```text
ACST = UTC+9:30
HK -> Darwin = +1h30m year-round
```

Use `Australia/Darwin`.

## 2026-10-02 live mental snapshot

At approximately 22:07 HKT:
- Sydney / Melbourne / Brisbane ≈ 00:07 next day;
- Adelaide ≈ 23:37;
- Perth ≈ 22:07;
- London ≈ 15:07;
- Boston ≈ 10:07.

On 2026-10-04, Sydney / Melbourne / Adelaide move one hour further ahead because DST starts there. Brisbane, Perth and Darwin do not change.

## PTime operating rule

Use two layers:

```text
Layer 1 — Mental Router
HK base + memorized offset
-> instant communication intuition

Layer 2 — Exact Router
IANA timezone + DST-aware calculation
-> verified local time before call / meeting / invite
```

Never hard-code only `AEST`, `BST`, `EDT`, etc. for long-lived automation. The canonical zone must be the IANA location name.

## Global communication shorthand

```text
HK evening
-> UK afternoon
-> Boston morning
-> Australia late evening / next-day midnight
```

This makes Hong Kong a useful P-Global communication base:
- Europe is still active;
- US East is entering / inside the workday;
- Australia may already be late, especially East Coast.

> **Fast mental math for intuition; IANA zones for truth.**
