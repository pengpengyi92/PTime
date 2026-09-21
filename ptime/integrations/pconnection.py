"""Explicit normalized local communication export; no live API."""

from ptime.integrations.base import LocalCommunicationSource


class PConnectionSource(LocalCommunicationSource):
    source_name = "pconnection_communication_export"
