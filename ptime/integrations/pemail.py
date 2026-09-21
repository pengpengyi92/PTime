"""Explicit normalized local communication export; no live API."""

from ptime.integrations.base import LocalCommunicationSource


class PEmailSource(LocalCommunicationSource):
    source_name = "pemail_communication_export"
