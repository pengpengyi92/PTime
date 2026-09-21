"""Read a normalized export with confirmed IANA zones; do not guess from profiles."""

from ptime.adapters.base import LocalContactSource


class PConnectionSource(LocalContactSource):
    source_name = "pconnection_local_export"
