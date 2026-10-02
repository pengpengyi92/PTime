# PTime Notebook — Boston-First Global Talk Matrix

- Base: Hong Kong / HKT (UTC+8)
- Timestamp: 2026-10-02 22:23:55 HKT
- Goal: calculate the core global talk zones in seconds.

## 0. One-line rule

Use **New York / Boston as the US anchor**.

```text
HK
├─ London      = HK -7/-8h
├─ NY/Boston   = HK -12/-13h
│  ├─ Chicago  = NY/Boston -1h
│  └─ SF/LA    = NY/Boston -3h
└─ Sydney      = HK +2/+3h
```

For fast daily intuition, use the current-season/default shortcuts:
- London: **HK -7h**
- NY / Boston: **HK -12h**
- Chicago: **Boston -1h**
- SF / Silicon Valley / LA: **Boston -3h**
- Sydney: **HK +2h**

Then verify with IANA timezone before an important call / meeting.

## 1. Boston-first worked example

If Hong Kong is **22:00**:

```text
Step 1  NY / Boston = 10:00
Step 2  Chicago     = 09:00
Step 3  SF / LA     = 07:00
Step 4  London      = 15:00
Step 5  Sydney      = 00:00 next day
```

This is the fastest mental route.

## 2. Core matrix

| Anchor | Fast rule | DST-aware full rule | IANA zone |
|---|---:|---:|---|
| London | HK -7h | -7 BST / -8 GMT | `Europe/London` |
| New York / Boston | HK -12h | -12 EDT / -13 EST | `America/New_York` |
| Chicago | Boston -1h | HK -13 CDT / -14 CST | `America/Chicago` |
| SF / Silicon Valley / LA | Boston -3h | HK -15 PDT / -16 PST | `America/Los_Angeles` |
| Sydney | HK +2h | +2 AEST / +3 AEDT | `Australia/Sydney` |

## 3. Amsterdam / continental Europe

Amsterdam is **not the same clock as London**. It is normally one hour ahead of London.

```text
Amsterdam = London +1h
          = HK -6h during CEST
          = HK -7h during CET
```

Use `Europe/Amsterdam`.

Mental rule:
> If you already know London, Amsterdam is simply **London +1h**.

## 4. Global-talk daypart router

### Hong Kong morning
```text
Sydney / Australia -> strongest natural overlap
```

### Hong Kong afternoon
```text
Sydney / Australia
+ London / Europe beginning to open
```

### Hong Kong evening
```text
London afternoon
+ NY / Boston morning
+ Chicago morning
+ SF / LA early morning
```

### Hong Kong midnight / early morning
```text
US West Coast becomes a normal workday window
```

## 5. PTime default mental policy

For casual intuition:
```text
London    -7
Boston    -12
Chicago   Boston -1
SF/LA     Boston -3
Sydney    +2
Amsterdam London +1
```

For anything important:
```text
mental estimate
-> IANA timezone check
-> calendar-date check
-> message / call / meeting
```

## 6. Why this is enough

These nodes cover the user's main recurring global communication graph:

```text
Hong Kong
↔ Sydney
↔ London / Amsterdam
↔ New York / Boston
↔ Chicago
↔ San Francisco / Silicon Valley / Los Angeles
```

> **First solve Boston. Then derive the rest of the US. Add Sydney. Subtract London.**
