"""Explicit normalized local communication export; no live API."""

from ptime.integrations.base import LocalCommunicationSource


class PLinkedInSource(LocalCommunicationSource):
    source_name = "plinkedin_communication_export"
