"""Read-only local V2.1 contract; no CRM, persistence or cross-repo reads."""

from dataclasses import dataclass

from ptime.festivals.models import GreetingPreference, GreetingRecord
from ptime.followups.models import FollowupRequest
from ptime.integrations.base import parse_snapshot
from ptime.models import Contact, PendingAction


@dataclass(frozen=True)
class RelationshipSnapshot:
    contacts: tuple[Contact, ...]
    pending_actions: tuple[PendingAction, ...]
    preferences: tuple[GreetingPreference, ...]
    history: tuple[GreetingRecord, ...]
    followups: tuple[FollowupRequest, ...]


def parse_relationship_snapshot(document, catalog, templates, source="local"):
    required = {"contacts", "pending_actions", "preferences", "history", "followups"}
    if not isinstance(document, dict) or set(document) != required:
        raise ValueError("V2.1 snapshot needs contacts, pending_actions, preferences, history, followups")
    if any(not isinstance(v, list) or len(v) > 1000 for v in document.values()):
        raise ValueError("V2.1 snapshot lists must contain at most 1000 entries each")
    contacts, actions = parse_snapshot({k: document[k] for k in ("contacts", "pending_actions")}, source)
    preferences = tuple(GreetingPreference(**row) for row in document["preferences"])
    history = tuple(GreetingRecord(**row) for row in document["history"])
    followups = tuple(FollowupRequest(**row) for row in document["followups"])
    ids = {c.id for c in contacts}
    if any(row.contact_id not in ids for row in (*preferences, *history, *followups)):
        raise ValueError("Unknown contact_id in relationship snapshot")
    if len({p.contact_id for p in preferences}) != len(preferences) or len({r.id for r in followups}) != len(followups):
        raise ValueError("Duplicate preference/follow-up ID")
    template_by_id = {t.id: t for t in templates}
    for pref in preferences:
        if set(pref.festival_ids + pref.excluded_festival_ids) - catalog.festivals.keys():
            raise ValueError("Unknown festival preference")
        for cycle in pref.reset_cycles:
            validate_cycle(cycle, catalog)
    for record in history:
        validate_cycle(record.cycle, catalog)
        if record.cycle.split(":")[0] != record.festival_id:
            raise ValueError("History festival/cycle mismatch")
        # Historical copy may have been retired; an unknown template ID remains evidence of a send.
        template = template_by_id.get(record.template_id)
        if template is not None and template.festival_id != record.festival_id:
            raise ValueError("History template/festival mismatch")
    for request in followups:
        if request.cycle is not None:
            validate_cycle(request.cycle, catalog)
            if not any(r.contact_id == request.contact_id and r.cycle == request.cycle for r in history):
                raise ValueError("Follow-up cycle has no explicit interaction history")
    return RelationshipSnapshot(tuple(contacts), tuple(actions), preferences, history, followups)


def validate_cycle(cycle, catalog):
    parts = cycle.split(":")
    if len(parts) != 2 or parts[0] not in catalog.festivals or not parts[1].isdigit() or not 1900 <= int(parts[1]) <= 2200:
        raise ValueError("Cycle must use canonical_festival:YYYY")
