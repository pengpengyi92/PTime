# Architecture

```text
CLI: explicit input + aware evaluation instant
 |
 +--> TimeAdapterAgent --> IANA conversion --> TimeWindow
 |
 +--> ContactSource --> validated Contact + Opportunity
                        |
                 GlobalContactAdapterAgent
                        |
           recipient window + eligibility gates
                        |
          weighted components + explanation
                        |
       suggested CommunicationAction / defer
                        |
                   text or JSON
```

## Ownership

- `models.py`: validated immutable dataclasses and stable enum choices.
- `core/timezone.py`: instant parsing, DST validation and localization.
- `core/config.py`: bounded local file reading and configuration validation.
- `agents/time_adapter.py`: time-of-day and local-weekday rules.
- `adapters/`: normalized YAML/JSON input and explicit provenance labels.
- `core/scoring.py`: interpretable components and configurable weights.
- `core/recommender.py`: hard gates, draft suggestions, deterministic ranking.
- `agents/contact_adapter.py`: contact-source orchestration.
- `__main__.py`: CLI presentation and error handling.

No database, LLM, remote API, background task or outbound action is needed.
The agent boundary is callable Python, not an invented external service.

Default config and synthetic examples are packaged once, from root `config/` and
`data/`, as resource packages. Source checkouts use those same files.
Users can override all configuration through an explicit directory.

## Falsifiable Design Decisions

1. **zoneinfo over fixed offsets:** the same China wall-clock time must convert differently
   in London/NY summer and winter; tested with DST and date-rollover fixtures.
2. **rules over LLM ranking:** a fixed contact set, instant and config must produce identical
   ranked output regardless of input order; tested. Actual reply-rate improvement is UNMEASURED.
3. **gates before weighted scores:** P0 plus an active opportunity must never bypass
   do-not-contact, quiet/early time or repeated same-day follow-up; tested.
4. **local adapters before live integration:** all three sources must read the same validated
   synthetic YAML/JSON without network access; tested. Real export integration is not claimed.

## Future Boundaries

Individual schedules, holidays, richer identity reconciliation, opt-in CRM exporters and
calendar checks need their own versioned evaluation. Do not add automatic outreach by
relabeling a recommendation as consent. Keep P-Global, P-Connection and P-LinkedIn unchanged.
