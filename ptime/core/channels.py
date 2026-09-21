"""Validated channel/context policy; no transport or calendar client."""

from dataclasses import dataclass
from pathlib import Path

import yaml

from ptime.core.config import default_resource, read_document
from ptime.core.timezone import wall_interval
from ptime.models import CHANNELS, CONTEXTS, unit


def intervals(value) -> tuple[tuple[int, int], ...]:
    if not isinstance(value, list) or not value:
        raise ValueError("Policy windows must be a nonempty list")
    result = tuple(sorted(wall_interval(item) for item in value))
    if any(left[1] > right[0] for left, right in zip(result, result[1:])):
        raise ValueError("Policy windows must not overlap")
    return result


def contains(windows: tuple[tuple[int, int], ...], minute: int) -> bool:
    return any(start <= minute < end for start, end in windows)


@dataclass(frozen=True)
class ChannelRule:
    windows: tuple[tuple[int, int], ...]
    score: float
    synchronous: bool


@dataclass(frozen=True)
class ContextRule:
    windows: tuple[tuple[int, int], ...]
    working_days_only: bool


@dataclass(frozen=True)
class ChannelPolicy:
    channels: dict[str, ChannelRule]
    contexts: dict[str, ContextRule]
    synchronous_windows: tuple[tuple[int, int], ...]
    quiet: tuple[tuple[int, int], ...]
    late_reply: tuple[tuple[int, int], ...]
    search_days: int

    def boundaries(self) -> set[int]:
        windows = list(self.quiet + self.late_reply + self.synchronous_windows)
        for rule in self.channels.values():
            windows.extend(rule.windows)
        for rule in self.contexts.values():
            windows.extend(rule.windows)
        return {0, *(edge for interval in windows for edge in interval)}


def load_channels(config_dir: Path | None = None) -> ChannelPolicy:
    doc = read_document(config_dir / "channels.yaml") if config_dir is not None else yaml.safe_load(
        default_resource("channels.yaml").read_text(encoding="utf-8")
    )
    required = {"search_days", "quiet_window", "early_window", "late_reply_window",
                "contexts", "channels", "synchronous_windows"}
    if not isinstance(doc, dict) or set(doc) != required:
        raise ValueError("channels.yaml has missing or unknown fields")
    if type(doc["search_days"]) is not int or not 1 <= doc["search_days"] <= 14:
        raise ValueError("search_days must be an integer between 1 and 14")
    if not isinstance(doc["channels"], dict) or set(doc["channels"]) != CHANNELS:
        raise ValueError("Configure exactly the eight supported channels")
    if not isinstance(doc["contexts"], dict) or set(doc["contexts"]) != CONTEXTS:
        raise ValueError("Configure exactly the four supported contexts")
    channels, contexts = {}, {}
    for name, entry in doc["channels"].items():
        if not isinstance(entry, dict) or set(entry) != {"windows", "score", "synchronous"} or type(entry["synchronous"]) is not bool:
            raise ValueError("Invalid channel rule")
        expected_sync = name in {"phone", "video_call", "in_person"}
        if entry["synchronous"] != expected_sync:
            raise ValueError("Channel synchronicity must match its transport semantics")
        channels[name] = ChannelRule(intervals(entry["windows"]), unit(entry["score"], "channel score"), entry["synchronous"])
    for name, entry in doc["contexts"].items():
        if not isinstance(entry, dict) or set(entry) != {"windows", "working_days_only"} or type(entry["working_days_only"]) is not bool:
            raise ValueError("Invalid context rule")
        contexts[name] = ContextRule(intervals(entry["windows"]), entry["working_days_only"])
    return ChannelPolicy(
        channels, contexts, intervals(doc["synchronous_windows"]),
        (wall_interval(doc["quiet_window"]), wall_interval(doc["early_window"])),
        (wall_interval(doc["late_reply_window"]),), doc["search_days"],
    )
