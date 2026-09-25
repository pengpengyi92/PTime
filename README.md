# PTime

**V2.1 - Festival, Greeting & Follow-up Timing**

PTime converts time into actionable global communication windows.

- Where is currently inside a working window?
- Who might be appropriate to contact now?
- Which channel fits the relationship and context?
- What conversation or follow-up is actionable?

```text
Time x Region x People x Relationship x Channel x Opportunity -> Communication Action
TIME -> WHO -> CHANNEL -> ACTION

P Connection = WHO
P Global = WHERE
PTime = WHEN
P Email / P LinkedIn = HOW
WHO x WHERE x WHEN x HOW -> ACTION
```

The purpose is not to know what time it is.
The purpose is to know what becomes actionable because of the time.

## Why PTime

PTime treats time as an operational resource. When one region finishes its workday,
another may still be active. Late evening in Shenzhen can be a professional window
in London or the US East Coast, shifting attention toward relevant people there.

The goal is **not to communicate constantly**. It is to communicate at the right time,
while respecting both parties' rest, availability and preferences.

Conceptual cycle from a Shenzhen base (date/DST-dependent, not fixed offsets):

```text
China morning       -> Asia
China afternoon     -> Asia, then Europe opening
China evening       -> Europe, then US East opening
China late evening  -> US East, then US West opening
```

At **2026-09-21 22:15 Asia/Shanghai**:
London 15:15 +01:00; New York/Boston 10:15 -04:00; San Francisco 07:15 -07:00;
Hong Kong/Singapore 22:15 +08:00. All nine configured regions use IANA zoneinfo/DST,
not manually assumed time differences.

## Position in the System

```text
                P Global
                   |
             Global regions
                   |
                 PTime
        /          |          \
 P Connection  P LinkedIn    P Email
        \          |          /
          Communication Router
                   |
      Talk / Follow-up / Interview / Email
                   |
             Human approval
```

P Kago is an additional **generic local adapter placeholder** with no assumed native API.
PMap may later consume timing JSON. None of these names imply live account connectivity.

## Quick Start

Python 3.11+:

```bash
git clone https://github.com/pengpengyi92/PTime.git
cd PTime
python -m venv .venv
```

Activate with `.\.venv\Scripts\Activate.ps1` on Windows PowerShell, or
`source .venv/bin/activate` on macOS/Linux, then:

```bash
python -m pip install -e ".[dev]"
python -m ptime now
python -m ptime talk
python -m ptime email
python -m pytest
```

The installed `ptime` console command is equivalent. No API key or environment variable
is required. No LLM, database, server, frontend or cloud deployment is involved.

**Inputs start empty.** Preview explicitly with fictional data:

```bash
python -m ptime talk --demo --at 2026-09-21T22:15
python -m ptime email --demo --at 2026-09-21T22:15 --json
python -m ptime now --regions London NewYork Boston
```

The dated demo ranks London/Boston and defers the Shenzhen email to
**2026-09-22 09:00 +08:00**, displaying its UTC equivalent. An explicitly recorded
Singapore friend's late preference demonstrates a narrow informal exception.
These are fictional people, not live contacts.

## Commands and Inputs

| Command | Purpose | Default local input |
| --- | --- | --- |
| now | Nine global clocks and regional windows | Config only |
| contacts | Compatible V0.1 contact ranking | private/contacts.yaml |
| talk | Best channel per unqueued contact; evaluate queued actions | private/communication.yaml |
| email | Time the explicit email draft/action queue only | private/communication.yaml |
| festivals | Layered calendar context | Packaged public configuration |
| greetings | Preview bilingual general/professional/reconnect copy | Packaged public configuration |
| touchpoints | Explicitly opted-in relationship timing | private/touchpoints.yaml |
| followups | Reply/user-request-driven future windows | private/touchpoints.yaml |

Paths are relative to the working directory. Missing default input yields empty results,
not fabricated contacts; an explicitly requested missing file fails.

```bash
python -m ptime talk --input private/communication.yaml --source pconnection
python -m ptime email --input private/communication.json --source pemail --json
python -m ptime contacts --contacts private/contacts.yaml
```

The five V2 source names are pemail, plinkedin, pconnection, pglobal, pkago; local is also
supported. All consume the same normalized YAML/JSON contract, **not raw native exports**.
See [V2 input and timing contract](docs/v2-contract.md) and the synthetic
[data example](data/communication.example.yaml).

## Timing and Recommendations

Configure:
- `regions.yaml`: region IDs, display labels and IANA zones.
- `working_windows.yaml`: regional windows, workweek, base zone and weekend weighting.
- `scoring.yaml`: priority/relationship/recency/opportunity weights.
- `channels.yaml`: eight channel rules, four contexts, quiet/late intervals and search horizon.

Use `--config-dir private/config` to override. All four files are needed for talk/email;
legacy now/contacts still accept a three-file configuration.

Channels: email, linkedin, wechat, whatsapp, telegram, phone, video_call, in_person.
Contexts: professional, semi_professional, informal, personal.

Channel and context windows intersect with explicit contact preferences. Synchronous
conversation needs a working meeting window or an explicitly confirmed interval.
Do-not-contact and allowed channels always apply. A high priority or overdue task never
grants permission to ignore these gates.

Default late exceptions:
- An explicitly expected asynchronous reply may fit 21:00-23:00.
- A friend needs a recorded late preference and informal/personal context.
- An explicitly confirmed synchronous meeting is eligible only during its supplied interval,
  even outside usual hours; PTime does not verify or create the calendar event.

Otherwise, quiet hours and same-day follow-up suppression defer outreach. Next-window
search recalculates date, local weekday and DST, including spring gaps and repeated fall times.

`SEND_NOW` is **only a timing suggestion**. It does not send, schedule or authorize anything.
Other decisions: WAIT, REVIEW, BLOCKED, SKIP. Results contain reasons, score components,
topics, source labels, due/overdue status and a dated next window where one exists.
All carry `requires_human_approval: true` and `calendar_verified: false`.

V2 scoring retains the V0.1 weighted baseline:
0.40 time + 0.25 priority + 0.15 relationship + 0.10 recency + 0.10 opportunity.
Time includes weekday and channel multipliers; overdue state breaks otherwise equal ranks.
Scores are **uncalibrated heuristics**, not availability or response probabilities.

## Boundaries and Privacy

PTime is not a CRM, email client, LinkedIn replacement or scheduler.
- No APIs, scraping, outbound messages, automatic drafts, reminders or account discovery.
- Curated festival dates, NOT a complete leave/travel or personal-availability calendar.
- Maximum 1 MB / 1,000 contacts / 1,000 pending actions per normalized local snapshot.
- Only synthetic examples in Git. Real contacts and outputs stay in ignored private/.
- Real-world communication effectiveness remains **UNMEASURED**.

See [privacy](PRIVACY.md), [DST semantics](docs/time-semantics.md),
[legacy adapter contract](docs/adapters.md), and [architecture](docs/architecture.md).

## Version and Verification

Version moves directly from **0.1.0 to 2.0.0** for this mission expansion; no V1.0 release
is claimed. V2.1 is an additive minor upgrade. Read [AGENT.md](AGENT.md), [CHANGELOG.md](CHANGELOG.md), [VERSION](VERSION),
and [release notes](releases/V2.1.md). Both V0.1 CLI commands remain available with
their original conservative policy; V2 exceptions apply to talk/email.

```bash
python -m pytest
python -m build --wheel
```

After installing the built wheel rather than an editable checkout:
`python scripts/smoke_installed.py` tests packaged defaults, three demos and all eight commands
from a temporary directory. Measured results and limitations are recorded in
[BENCHMARK_CARD.md](BENCHMARK_CARD.md), [TODO.md](TODO.md) and the
[V2.1 implementation log](logs/2026-09-25-ptime-v2.1-implementation.md).
The earlier [V2.0 upgrade log](logs/2026-09-21-ptime-v2-upgrade.md) remains preserved.

## Festival Timing & Relationship Touchpoints

V2.0 = timezone / region / channel timing.
V2.1 = timezone + festival + follow-up + relationship-maintenance timing.

```text
WHO x WHERE x WHEN x HOW x WHY NOW -> Advisory Action
Self Introduction -> Conversation -> Follow-up -> Festival / Periodic Touchpoint
-> Reconnect -> DD / Coffee Chat / Collaboration / Recruiting
```

PCV Self-Introduction is a first-contact communication asset. PTime General Greeting
is a relationship-maintenance timing asset: PCV decides WHAT, PTime decides WHEN.
Only an opaque asset reference is consumed; no CV or private repository is opened.

```bash
ptime festivals --region china --days 30
ptime festivals --region united_kingdom --days 60 --include-non-greeting
ptime festivals --region united_states --days 60
ptime greetings --festival mid_autumn --style general --locale zh-CN
ptime greetings --festival christmas --style professional --locale en
ptime touchpoints --festival mid_autumn --demo --at 2026-09-25T10:00+08:00 --json
ptime followups --demo --at 2026-09-25T10:00+08:00 --json
```

Four calendar layers, 15 canonical events and 54 generic bilingual templates.
Lunar/UK dated tables cover 2026-2027; unknown years are reported, not guessed.
Shared festivals have one ID across views. Festival day and official holiday period
are separate. UK sample means England/Wales. Non-greeting holidays are not outreach
triggers. Source citations and scope are in [festival sources](docs/festival-sources.md).

No contact is opted in based on location. Explicit festival preferences are required.
One greeting per contact/cycle across all channels; recent contacts and active
conversations are suppressed. SUGGEST never authorizes sending. No-reply never
causes automatic repeated follow-ups. Explicit reply/user action may open an advisory
follow-up after cooldown, V2 policy checks, and both recipient/sender rest protection.

Previewing does not write history. After actual human-approved interaction, update
the private snapshot. No scheduler, auto-sender or hidden relationship storage.
See [V2.1 contract](docs/v2.1-contract.md), [fictional example](data/touchpoints.example.yaml)
and [V2.1 release](releases/V2.1/README.md).
