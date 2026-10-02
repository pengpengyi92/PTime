# PTime Notebook — Boston-First Global Talk Matrix

- Base: Hong Kong / HKT (UTC+8)
- Updated: 2026-10-02 22:23:55 HKT
- Goal: calculate the core global-talk zones in seconds.

## One-line rule

```text
HK
├─ London      = HK -7/-8h
├─ NY/Boston   = HK -12/-13h
│  ├─ Chicago  = NY/Boston -1h
│  └─ SF/LA    = NY/Boston -3h
├─ Amsterdam   = London +1h
└─ Sydney      = HK +2/+3h
```

For fast daily intuition, use the current-season defaults:
- London: HK -7h
- NY / Boston: HK -12h
- Chicago: Boston -1h
- SF / Silicon Valley / LA: Boston -3h
- Sydney: HK +2h
- Amsterdam: London +1h

Then verify with IANA timezone before an important call / meeting.

## Boston-first worked example

If Hong Kong is **22:00**:

```text
NY / Boston  = 10:00
Chicago      = 09:00
SF / LA      = 07:00
London       = 15:00
Amsterdam    = 16:00
Sydney       = 00:00 next day
```

## Core matrix

| Anchor | Fast rule | Full DST-aware rule | IANA zone |
|---|---:|---:|---|
| London | HK -7h | -7 BST / -8 GMT | Europe/London |
| New York / Boston | HK -12h | -12 EDT / -13 EST | America/New_York |
| Chicago | Boston -1h | HK -13 CDT / -14 CST | America/Chicago |
| SF / Silicon Valley / LA | Boston -3h | HK -15 PDT / -16 PST | America/Los_Angeles |
| Sydney | HK +2h | +2 AEST / +3 AEDT | Australia/Sydney |
| Amsterdam | London +1h | HK -6 CEST / -7 CET | Europe/Amsterdam |

## Default mental policy

```text
London    -7
Boston    -12
Chicago   Boston -1
SF/LA     Boston -3
Sydney    +2
Amsterdam London +1
```

For exact scheduling:
```text
mental estimate -> IANA timezone check -> date check -> call / message / meeting
```

> **First solve Boston. Then derive the rest of the US. Add Sydney. Subtract London.**
