"""Read a user-prepared normalized export; no LinkedIn API or browser scraping."""

from ptime.adapters.base import LocalContactSource


class PLinkedInSource(LocalContactSource):
    source_name = "plinkedin_local_export"
