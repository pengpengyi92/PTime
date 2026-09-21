# V2.0 Communication Snapshot and Timing Contract

## Local Integration

All five classes in `ptime/integrations/` implement:

```python
class CommunicationSource(Protocol):
    def get_contacts(self) -> list[Contact]: ...
    def get_pending_actions(self) -> list[PendingAction]: ...
```

They read one validated snapshot, so editing a file cannot produce contacts from one
version and actions from another. MockCommunicationSource takes explicit validated
in-memory records. There are no native exports, APIs, authentication or network calls.
P Kago's class is only a generic local placeholder; its native schema is unknown.

Every input has exactly two lists:

```yaml
contacts:
  - id: example-london
    name: Example London Researcher
    region: London
    timezone: Europe/London
    relationship_type: researcher
    priority: P0
    channels: [email, linkedin]
    topics: [quant, research]
    last_contact_at: "2026-09-18T09:00:00Z"
    preferred_contact_windows: ["09:30-12:00", "14:00-18:00"]
    source_systems: [PConnection]
    synthetic: true
pending_actions:
  - id: example-draft
    contact_id: example-london
    channel: email
    context: professional
    kind: follow_up
    status: draft
    due_at: "2026-09-22T16:00:00Z"
```

Keep real snapshots in ignored private/. Input is bounded at 1 MB and 1,000 contacts /
1,000 actions. Duplicate IDs, dangling contact IDs, malformed types and unknown fields fail.
`region` aliases `location`; `relationship_type` aliases `relationship`.
Conflicting aliases are rejected. The Python Contact model retains legacy field names.
Unique explicit IDs are mandatory for V2 snapshots; channels may be empty, which yields REVIEW.
Timezone must be confirmed explicitly as an IANA zone: a city name is not enough.
Organization/relationship/priority may be omitted to use legacy defaults; null values are
not interpreted as known data. Recipient addresses and message bodies are not needed for
timing and are deliberately outside this normalized contract. P Email retains them privately.

`last_contact_at`, `next_action_due`, `due_at`, `not_before` and scheduled timestamps
must include a numeric UTC offset or Z. Ambiguous naive timestamps are rejected.
`last_contact_at` derives the recipient-local `last_contact` date. Conflicting date/timestamp
fields and contact history after the evaluation instant fail visibly.

## Pending Actions

Fields: id, contact_id, channel, kind, context, status, optional priority/due_at/not_before,
expected_reply, scheduled_at/scheduled_until, confirmed.

- Channels: email, linkedin, wechat, whatsapp, telegram, phone, video_call, in_person.
- Contexts: professional, semi_professional, informal, personal.
- Kinds: legacy actions plus `reply`.
- States: draft/pending are actionable; sent/completed/canceled are SKIP.
- due_at is a **soft deadline**, displayed as overdue when passed; it is not a send trigger.
- not_before is an explicit earliest timing bound.
- expected_reply=true must be kind=reply; without explicit expectation a reply needs REVIEW.
- A scheduled interval requires both aware start/end, a synchronous channel and explicit
  confirmed=true to qualify. Pending/unconfirmed intervals need REVIEW.
- A confirmed interval never moves automatically. Expired meetings are SKIP.

## Channel and Context Policy

Edit config/channels.yaml. Channel intervals and context intervals intersect, together
with recipient-local weekdays and explicit preferred windows. Default examples:
email 09:00-18:00, LinkedIn 08:00-20:00, messaging 09:00-21:00.
Phone/video/in-person and interview/coffee actions also need 09:00-12:00 or 14:00-18:00
working-day windows unless there is an explicitly confirmed meeting.

Contexts determine whether weekdays apply. On weekends, informal/personal suggestions
require a friend by default. Channel availability does not imply an account connection.

## Exceptions and Non-Negotiable Gates

Priority never overrides do-not-contact or an unlisted channel.

Default quiet interval is 23:00-07:00; late exception interval is 21:00-23:00.
An explicit expected reply can permit asynchronous response in that late interval.
A friend can use it only for informal/personal context and explicitly recorded preferred
windows. Friendship, overdue status or P0 priority alone does not unlock late outreach.

Explicitly confirmed synchronous meetings are the narrow exception to usual timing,
rest and preference windows, only between their provided start/end. They still respect
do-not-contact, allowed channels and not_before. This is user-supplied evidence, not
calendar verification. No event is created.

Repeated same-day follow-ups are deferred until a later date; an explicit expected reply
is a different action. Terminal queue items suppress automatic fresh suggestions for
that contact, preventing a completed task from resurfacing as new outreach.

## Decisions

- SEND_NOW: appropriate under supplied timing rules; human review still mandatory.
- WAIT: unsuitable now; next_window_at is UTC, next_window_local includes date and offset.
- REVIEW: missing channel, unknown permission/context or unconfirmed schedule.
- BLOCKED: do-not-contact.
- SKIP: already sent/completed/canceled or elapsed confirmed interval.

No future window within the configured search horizon (default 8 local days) produces
WAIT with null next-window fields and an explicit explanation. Never invent a slot.
Window search evaluates actual UTC instants at rule boundaries, both DST folds and offset
transitions. Local gaps are skipped; offsets at the next window are recalculated.

The score uses legacy components with regional time score multiplied by channel score.
Only eligible records get nonzero final scores. Due status breaks otherwise equal ranks;
it cannot change eligibility. Scores are preferences, not response probabilities.

## CLI and Compatibility

```bash
python -m ptime talk --input private/communication.yaml --source pconnection
python -m ptime email --input private/communication.json --source pemail --json
python -m ptime talk --demo --at 2026-09-21T22:15
```

Without --input, talk/email read private/communication.yaml if present; otherwise empty.
Without queue items, talk suggests the best eligible channel per contact and reports
other currently eligible channels. Explicit queue items are evaluated individually.
Email processes **only explicit email queue items**; it never creates drafts.

The legacy contacts command retains its original conservative policy and file schema.
Its behavior is intentionally not the same as the richer V2 talk router.
A legacy three-file --config-dir works for now/contacts; talk/email require channels.yaml too.
No V1.0 is invented. Version jumps 0.1.0 -> 2.0.0 per the approved mission expansion.
