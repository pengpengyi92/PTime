"""Read a user-prepared normalized export, not P-Global's private case notes."""

from ptime.adapters.base import LocalContactSource


class PGlobalSource(LocalContactSource):
    source_name = "pglobal_local_export"
