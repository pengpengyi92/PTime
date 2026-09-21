# PTime

**V0.1 - Global Time Adapter**

PTime treats time as an operational resource.

The goal is not to know what time it is.
The goal is to know what becomes actionable because of the time.

```text
Time x Region x People x Opportunity -> Action
Current time -> Global working windows -> Relevant people -> Suggested communication
```

PTime is a lightweight, on-demand Python CLI with two deterministic agents.
It does not use an LLM, scrape LinkedIn, send messages, book meetings, or run a scheduler.
Scores are explainable heuristics, **not measured response probabilities or calendar availability**.

## Quick Start

Python 3.11 or newer:

```bash
git clone https://github.com/pengpengyi92/PTime.git
cd PTime
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Then:

```bash
python -m pip install -e ".[dev]"
python -m ptime now
python -m ptime contacts
python -m pytest
```

The installed `ptime` command is equivalent to `python -m ptime`.
No account, API key or environment variable is required. Runtime uses local files only.

**Contacts start empty.** The normal command reads `private/contacts.yaml` relative to
the current working directory if it exists. It never silently loads fictional people.
To preview the ranking explicitly:

```bash
python -m ptime contacts --demo --at 2026-09-21T22:15
python -m ptime now --at 2026-09-21T22:15 --json
python -m ptime now --regions London NewYork Boston
python -m ptime contacts --contacts private/contacts.yaml --source pconnection --json
```

`--demo` uses only clearly fictional examples. Real contacts stay in ignored local
files; do not paste their CLI output into public issues or logs.

## The 22:15 Shenzhen Example

At **2026-09-21 22:15 Asia/Shanghai**, the default configuration gives:

| Region | Local time | Window | Regional score |
| --- | --- | --- | --- |
| Shenzhen / China | 22:15 +08:00 | weak | 0.25 |
| Hong Kong | 22:15 +08:00 | weak | 0.25 |
| Singapore | 22:15 +08:00 | weak | 0.25 |
| London | 15:15 +01:00 | active | 0.95 |
| New York / Boston / Greenwich, CT | 10:15 -04:00 | active | 0.95 |
| Chicago | 09:15 -05:00 | active | 0.95 |
| San Francisco | 07:15 -07:00 | early | 0.55 |

The date matters: offsets change with daylight saving time.
The fictional London recruiter and Boston researcher are eligible in this example;
Singapore late evening and California early morning are deferred. Even a P0 priority
cannot override quiet hours. Informal friend contact is limited by default to 09:00-21:00;
being a friend does not make a 22:15 message automatically appropriate.

## Two Agents

- **TimeAdapterAgent** converts one timezone-aware instant into regional working windows.
- **GlobalContactAdapterAgent** loads an explicit local contact source, applies eligibility
  rules, ranks eligible people and explains the suggested action.

```text
P-Global operating context
         |
       PTime
         |
Global communication window
         |
P-LinkedIn / P-Connection normalized local export
         |
Suggested talk / follow-up / interview proposal / opportunity
         |
Human review and actual communication elsewhere
```

PMap can later consume the JSON output. There is no live PMap or CRM integration in V0.1.
P-Global manages global context, PMap space, PTime time, and P-Connection relationship memory.

## Configuration and Ranking

Edit the three files in `config/`, or copy all three into an ignored directory and pass
`--config-dir private/config`. Installed wheels bundle the defaults.

- `regions.yaml`: nine region IDs, display names and explicit IANA timezones.
- `working_windows.yaml`: base zone, working weekdays, window scores and modes.
- `scoring.yaml`: ranking weights, relationship/action scores and recency thresholds.

Intervals are start-inclusive and end-exclusive. The default workweek is Monday-Friday.
Lunch allows asynchronous suggestions, not immediate interviews. Professional contact is
deferred outside work windows; friends may receive informal suggestions during daytime
weekends and early evening. These are configurable conventions, not cultural facts.

For eligible contacts:

```text
regional score = local time score * weekday multiplier
availability heuristic = regional score * relationship score * action score

final_score =
    0.40 * regional score
  + 0.25 * contact priority
  + 0.15 * relationship score
  + 0.10 * recency score
  + 0.10 * opportunity score
```

The JSON component called `time_score` is the regional score after weekday adjustment.
Recency is days since contact / 14, capped at 1; unknown history uses 0.5.
An active opportunity with no elapsed deadline scores 1, otherwise 0.
Follow-up is described as due after seven days by default, not asserted as an obligation.

Do-not-contact, quiet/early hours, professional weekend/evening restrictions and same-day
follow-up suppression are gates **before ranking**. Deferred records have zero final and
availability scores while preserving diagnostic components. Ties are sorted deterministically.

## Input, Output and Boundaries

See [adapter contract](docs/adapters.md), [time semantics](docs/time-semantics.md),
[architecture](docs/architecture.md), and [privacy](PRIVACY.md).

Both commands support full ISO timestamps, base-zone override and JSON output.
A naive timestamp uses the base zone; ambiguous/nonexistent DST wall times are rejected.
An offset-bearing timestamp identifies the instant directly.

Limitations:
- No holiday, leave, travel, personal calendar, consent or reply-likelihood verification.
- One configurable regional workweek/window policy, not individualized working calendars.
- Adapters consume **normalized** local YAML/JSON; they do not read native CRM exports unchanged.
- No automatic discovery of contacts, API calls, outreach, reminders or persistence.
- Contact dates and opportunity deadlines use the recipient's local calendar date.
- At most 1,000 contacts and 1 MB per local input document.
- Real-world communication effectiveness remains **UNMEASURED**.

## Development

```bash
python -m pytest
python -m build --wheel
```

Code lives in `ptime/`, defaults in `config/`, synthetic examples in `data/`, and
regression tests in `tests/`. Wheels include defaults and the opt-in demo.
After installing the wheel (not an editable checkout), run
`python scripts/smoke_installed.py` to check it from a temporary working directory.
V0.1 verification: 124 tests and installed-wheel smoke passed on Windows with
Python 3.11.3 and 3.12.13. macOS/Linux execution is not yet verified.
See [VERSION.md](VERSION.md), [TODO.md](TODO.md), and [BENCHMARK_CARD.md](BENCHMARK_CARD.md)
for scope and measured evidence.
