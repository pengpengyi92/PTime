# Local Contact Adapter Contract

This is the legacy `contacts` contract retained from V0.1. For `talk` / `email` use
the [V2 communication snapshot](v2-contract.md), which includes IDs, channels and a queue.

V0.1 implements one narrow interface:

```python
class ContactSource:
    def get_contacts(self) -> list[Contact]: ...
```

`PGlobalSource`, `PLinkedInSource` and `PConnectionSource` are source-labeled readers
of the same normalized local format. They are not authenticated integrations, crawlers,
or native database readers. `--source` records provenance; it does not establish a connection.

## Normalized Example

Place real records only in ignored `private/`. The following is fictional:

```yaml
contacts:
  - name: Example Researcher
    organization: Fictional Research Team
    location: Boston
    timezone: America/New_York
    relationship: researcher
    priority: P1
    topics: [market_data, factor_research]
    last_contact: "2026-09-12"
    next_action: research_discussion
    do_not_contact: false
    synthetic: true
    opportunities:
      - id: fictional-research
        title: Fictional research discussion
        status: active
        deadline: "2026-10-01"
```

JSON may use the same `contacts` wrapper or a top-level list. Empty `contacts: []` is valid.
Unknown fields, invalid zones, invalid enums, future contact dates at evaluation time and
duplicate identities fail visibly. Data loading uses `yaml.safe_load`, not object construction.

Required fields: `name`, `location`, `timezone`. Location is a display label, never a timezone
guess. Other fields have conservative defaults in `Contact`. Dates are ISO calendar dates.
`last_contact` and opportunity `deadline` are interpreted in the contact's timezone; a deadline
is inclusive for that local date. The adapter supplies `source`, overriding any payload label.
Set `synthetic: false` for real private records; never publish them here.

Relationships: friend, researcher, headhunter, recruiter, hr, hiring_manager, pm, founder,
alumni, professional_contact.

Actions: follow_up, informal_chat, interview, coffee_chat, research_discussion,
recruiting_message, application_follow_up, relationship_maintenance.

Priorities: P0, P1, P2, P3. Opportunity states: active, closed, expired.

## Export Preparation

- **P-Global:** manually export selected people using the schema above. The operating manual
  does not imply a machine-readable people API.
- **P-Connection:** export only selected people. Map its relationship metadata and
  `last_contact_at` to the normalized relationship and recipient-local calendar date.
  Its native Person data does not guarantee an explicit IANA timezone: confirm and add it.
  Map a domain to `topics` only when relevant. Do not silently ingest private metadata.
- **P-LinkedIn:** normalize an authorized local export manually. Native LinkedIn CSV files
  and the project's own richer models are not directly accepted.
- **PMap:** future consumer of time-window JSON, not a current contact importer.

No real contact registry was imported for the bootstrap.

```bash
python -m ptime contacts --source pglobal --contacts private/pglobal.yaml
python -m ptime contacts --source plinkedin --contacts private/plinkedin.json
python -m ptime contacts --source pconnection --contacts private/pconnection.yaml
```

## JSON Output

Common fields include version, evaluated_at (UTC), base_timezone, base_time and notice.
`now` returns `regions`; `contacts` returns eligible `recommendations` and `deferred`
records separately, plus total/eligible/deferred counts and data_mode.
`--limit` caps each list, not the counts.

Recommendations contain local date/time/offset, priority, component scores, reason,
source, synthetic marker and a structured action with `requires_human_approval: true`.
All results have `calendar_verified: false`. Output may contain private input:
redirect only into an ignored/private destination, never a public log.
