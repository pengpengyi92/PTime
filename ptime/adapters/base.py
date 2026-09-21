"""Explicit local exports, never authenticated scraping or automatic CRM imports."""

from dataclasses import fields
from pathlib import Path
from typing import Protocol

from ptime.core.config import read_document
from ptime.models import Contact, Opportunity


class ContactSource(Protocol):
    def get_contacts(self) -> list[Contact]: ...


def parse_contacts(document, source: str) -> list[Contact]:
    if isinstance(document, dict):
        if set(document) != {"contacts"}:
            raise ValueError("Export wrapper must contain only a contacts list")
        document = document["contacts"]
    if not isinstance(document, list):
        raise ValueError("Contact export must be a list or a contacts wrapper")
    if len(document) > 1000:
        raise ValueError("V0.1 supports at most 1000 contacts per explicit export")
    contacts = []
    allowed = {f.name for f in fields(Contact)}
    for index, record in enumerate(document):
        if not isinstance(record, dict) or set(record) - allowed:
            raise ValueError(f"Contact row {index + 1}: unknown fields or invalid record; use a normalized export")
        values = dict(record)
        opportunities = values.get("opportunities", [])
        if not isinstance(opportunities, list):
            raise ValueError(f"Contact row {index + 1}: opportunities must be a list")
        try:
            values["opportunities"] = tuple(Opportunity(**item) for item in opportunities)
            values["source"] = source
            contacts.append(Contact(**values))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Contact row {index + 1}: {exc}") from exc
    return contacts


class LocalContactSource:
    source_name = "local_export"

    def __init__(self, path: Path):
        self.path = Path(path)

    def get_contacts(self) -> list[Contact]:
        return parse_contacts(read_document(self.path), self.source_name)
