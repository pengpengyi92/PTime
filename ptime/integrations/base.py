"""A single validated snapshot keeps contacts and queued actions consistent."""

from pathlib import Path
from typing import Protocol

from ptime.adapters.base import parse_contacts
from ptime.core.config import read_document
from ptime.models import Contact, PendingAction


class CommunicationSource(Protocol):
    def get_contacts(self) -> list[Contact]: ...
    def get_pending_actions(self) -> list[PendingAction]: ...


def validate_snapshot(contacts: list[Contact], actions: list[PendingAction]) -> None:
    if len(contacts) > 1000 or len(actions) > 1000:
        raise ValueError("V2 supports at most 1000 contacts and 1000 actions")
    ids = [contact.id for contact in contacts]
    if any(not key for key in ids) or len(set(ids)) != len(ids):
        raise ValueError("Communication contacts require unique nonempty IDs")
    action_ids = [action.id for action in actions]
    if len(set(action_ids)) != len(action_ids):
        raise ValueError("Duplicate pending action ID")
    if any(action.contact_id not in ids for action in actions):
        raise ValueError("Pending action refers to an unknown contact_id")


def parse_snapshot(document, source: str) -> tuple[list[Contact], list[PendingAction]]:
    if not isinstance(document, dict) or set(document) != {"contacts", "pending_actions"}:
        raise ValueError("Communication snapshot requires contacts and pending_actions lists")
    if not isinstance(document["contacts"], list) or not isinstance(document["pending_actions"], list):
        raise ValueError("contacts and pending_actions must be lists")
    if len(document["contacts"]) > 1000 or len(document["pending_actions"]) > 1000:
        raise ValueError("V2 supports at most 1000 contacts and 1000 actions")
    rows = []
    for item in document["contacts"]:
        if not isinstance(item, dict):
            raise ValueError("Each contact must be a mapping")
        row = dict(item)
        for alias, canonical in (("region", "location"), ("relationship_type", "relationship")):
            if alias in row:
                if canonical in row and row[alias] != row[canonical]:
                    raise ValueError(f"Conflicting contact fields: {alias} and {canonical}")
                row[canonical] = row.pop(alias)
        rows.append(row)
    contacts = parse_contacts(rows, source)
    try:
        actions = [PendingAction(**row) for row in document["pending_actions"]]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid pending action: {exc}") from exc
    validate_snapshot(contacts, actions)
    return contacts, actions


class MockCommunicationSource:
    """Explicit in-memory fixture; never an implicit fallback for a live source."""

    source_name = "mock"

    def __init__(self, contacts: list[Contact], actions: list[PendingAction]):
        validate_snapshot(contacts, actions)
        self._contacts = tuple(contacts)
        self._actions = tuple(actions)

    def get_contacts(self) -> list[Contact]:
        return list(self._contacts)

    def get_pending_actions(self) -> list[PendingAction]:
        return list(self._actions)


class LocalCommunicationSource(MockCommunicationSource):
    source_name = "local_communication_export"

    def __init__(self, path: Path):
        contacts, actions = parse_snapshot(read_document(Path(path)), self.source_name)
        super().__init__(contacts, actions)
