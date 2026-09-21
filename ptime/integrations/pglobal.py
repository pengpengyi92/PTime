"""Explicit normalized local communication export; no live API."""

from ptime.integrations.base import LocalCommunicationSource


class PGlobalSource(LocalCommunicationSource):
    source_name = "pglobal_communication_export"
