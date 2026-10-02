# PTime Notebook — Global Time Zone Matrix from Hong Kong

- Base timezone: **Asia/Hong_Kong (HKT, UTC+8)**
- Date created: 2026-10-02
- Purpose: fast mental conversion + global communication routing
- Rule: **mental offset first; IANA timezone before any important call / meeting**

## 1. Core mental matrix

| Region | Representative cities | IANA zone | Standard-time mental rule from HK | Daylight-time mental rule from HK | Shortcut |
|---|---|---|---:|---:|---|
| UK | London | `Europe/London` | HK -8h (GMT) | HK -7h (BST) | **-8 / -7** |
| US East | New York, Boston | `America/New_York` | HK -13h (EST) | HK -12h (EDT) | **-13 / -12** |
| US Central | Chicago | `America/Chicago` | HK -14h (CST) | HK -13h (CDT) | **-14 / -13** |
| US Pacific | San Francisco, Silicon Valley, Los Angeles | `America/Los_Angeles` | HK -16h (PST) | HK -15h (PDT) | **-16 / -15** |
| Australia East DST states | Sydney, Melbourne | `Australia/Sydney`, `Australia/Melbourne` | HK +2h (AEST) | HK +3h (AEDT) | **+2 / +3** |
| Australia East no DST | Brisbane | `Australia/Brisbane` | HK +2h | HK +2h | **+2** |
| Australia Central | Adelaide | `Australia/Adelaide` | HK +1.5h (ACST) | HK +2.5h (ACDT) | **+1.5 / +2.5** |
| Australia West | Perth | `Australia/Perth` | HK +0h | HK +0h | **same as HK** |

## 2. The five high-frequency PTime routes

### London
```text
HK -7h in British Summer Time
HK -8h in GMT
```

### New York / Boston
Same Eastern Time zone.

```text
HK -12h in EDT
HK -13h in EST
```

### Chicago
One hour behind New York / Boston.

```text
HK -13h in CDT
HK -14h in CST
```

### San Francisco / Silicon Valley / Los Angeles
Same Pacific Time zone.

```text
HK -15h in PDT
HK -16h in PST
```

Mental shortcut:
> **US West Coast = New York/Boston minus another 3 hours.**

### Sydney
```text
HK +2h in AEST
HK +3h in AEDT
```

Mental shortcut:
> **SYD = HK +2 / +3.**

## 3. 2026-10-02 current-season snapshot

On 2026-10-02:
- London is on BST -> **HK -7h**.
- New York / Boston are on EDT -> **HK -12h**.
- Chicago is on CDT -> **HK -13h**.
- San Francisco / Los Angeles are on PDT -> **HK -15h**.
- Sydney / Melbourne are still on AEST -> **HK +2h**.
- Sydney / Melbourne move to AEDT on 2026-10-04 -> then **HK +3h**.

US DST ends on 2026-11-01. UK summer time ends on 2026-10-25.

## 4. Quick examples from HKT

If Hong Kong is **22:00** during the current 2026-10-02 seasonal configuration:

```text
London          15:00
New York/Boston 10:00
Chicago         09:00
SF / LA         07:00
Sydney          00:00 next day
```

If Hong Kong is **00:00**:

```text
London          17:00 previous day? No — same calendar day under normal HKT date handling after midnight must be computed by full datetime.
New York/Boston 12:00 previous calendar day
Chicago         11:00 previous calendar day
SF / LA         09:00 previous calendar day
Sydney          02:00
```

Operational note:
> Always calculate with the full date when crossing midnight; mental arithmetic is for intuition, not calendar bookkeeping.

## 5. Communication-window matrix

Assume a normal local communication window of roughly **09:00-18:00 local**. Exact suitability depends on the relationship.

| Region | Approximate HK window during daylight/summer configuration | PTime intuition |
|---|---|---|
| London | 16:00-01:00 HKT | HK afternoon/evening is excellent |
| New York / Boston | 21:00-06:00 HKT | HK late evening/night is excellent |
| Chicago | 22:00-07:00 HKT | HK late evening/night |
| SF / Silicon Valley / LA | 00:00-09:00 HKT | HK midnight/early morning; late evening only catches early West Coast morning |
| Sydney | 06:00-15:00 HKT when +3h; 07:00-16:00 HKT when +2h | HK morning/daytime is best |

This is why a Hong Kong evening naturally routes:
```text
UK afternoon
-> US East morning
-> Chicago morning
-> US West early morning
while Australia East is already late night
```

## 6. PTime routing order by Hong Kong daypart

### HK morning
Best natural overlap:
- Sydney / Australia;
- Asia;
- US West previous evening for close friends if appropriate.

### HK afternoon
Best natural overlap:
- Australia daytime;
- London morning / midday as Europe opens.

### HK evening
Best natural overlap:
- London afternoon;
- New York / Boston morning;
- Chicago morning;
- US West starts becoming reachable later.

### HK midnight / very early morning
Best natural overlap:
- US West Coast workday;
- US East / Central midday-afternoon.

## 7. Mental ladder

Instead of memorizing every city independently:

```text
London      = HK -7/-8
NY/Boston   = HK -12/-13
Chicago     = NY/Boston -1h
SF/LA       = NY/Boston -3h
Sydney      = HK +2/+3
```

That is enough to reconstruct the core global communication graph quickly.

## 8. PTime safety rule

Never hard-code only the abbreviation (EDT/PDT/BST/AEDT) for future automation.

Use:
- `Europe/London`
- `America/New_York`
- `America/Chicago`
- `America/Los_Angeles`
- `Australia/Sydney`

Then let the timezone database handle DST.

> **Memorize relationships between zones; let IANA handle calendar truth.**
