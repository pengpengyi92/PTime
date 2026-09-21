"""Load and validate configurable region/window/score policies."""

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
import json
import re

import yaml

from ptime.core.timezone import get_zone
from ptime.models import ACTIONS, PRIORITIES, RELATIONSHIPS, Region, text, unit

SCORE_KEYS = {"time_score", "contact_priority", "relationship_score", "recency_score", "opportunity_score"}


def read_document(path: Path):
    if path.stat().st_size > 1_000_000:
        raise ValueError("Input file exceeds the 1 MB V0.1 limit")
    content = path.read_text(encoding="utf-8-sig")
    return json.loads(content) if path.suffix.lower() == ".json" else yaml.safe_load(content)


def default_resource(name: str, resource_package: str = "ptime_defaults"):
    folder = "config" if resource_package == "ptime_defaults" else "data"
    source = Path(__file__).resolve().parents[2] / folder / name
    if source.is_file():
        return source
    return files(resource_package).joinpath(name)


def minute(value: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d|24:00", value):
        raise ValueError("Window boundary must use HH:MM, with 24:00 only as the final end")
    hours, minutes = map(int, value.split(":"))
    return hours * 60 + minutes


@dataclass(frozen=True)
class WindowRule:
    start: int
    end: int
    name: str
    status: str
    score: float
    modes: tuple[str, ...]


@dataclass(frozen=True)
class Settings:
    base_timezone: str
    regions: dict[str, Region]
    windows: tuple[WindowRule, ...]
    working_weekdays: tuple[int, ...]
    weekend_multiplier: float
    weights: dict[str, float]
    priorities: dict[str, float]
    relationships: dict[str, float]
    actions: dict[str, float]
    recency_days: int
    follow_up_due_days: int


def scores(value, keys: set[str], label: str) -> dict[str, float]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{label} must contain exactly: {', '.join(sorted(keys))}")
    return {key: unit(score, f"{label}.{key}") for key, score in value.items()}


def load_settings(config_dir: Path | None = None) -> Settings:
    def load(name):
        if config_dir is not None:
            return read_document(config_dir / name)
        return yaml.safe_load(default_resource(name).read_text(encoding="utf-8"))

    region_data, policy, scoring = (load(name) for name in ("regions.yaml", "working_windows.yaml", "scoring.yaml"))
    if not isinstance(region_data, dict) or not region_data:
        raise ValueError("regions.yaml must be a nonempty mapping")
    regions = {}
    for key, value in region_data.items():
        text(key, "region key")
        if not isinstance(value, dict) or "timezone" not in value:
            raise ValueError("Each region needs an explicit IANA timezone")
        regions[key] = Region(value.get("name", key), value["timezone"])
    if not isinstance(policy, dict) or not isinstance(scoring, dict):
        raise ValueError("Window and scoring configuration must be mappings")
    base_timezone = policy.get("base_timezone", "Asia/Shanghai")
    get_zone(base_timezone)
    weekdays = policy.get("working_weekdays")
    if not isinstance(weekdays, list) or not weekdays or any(type(d) is not int or d not in range(7) for d in weekdays) or len(set(weekdays)) != len(weekdays):
        raise ValueError("working_weekdays must be unique weekday integers 0..6")
    raw_windows = policy.get("windows")
    if not isinstance(raw_windows, list) or not raw_windows:
        raise ValueError("windows must be a nonempty list")
    windows = []
    for entry in raw_windows:
        if not isinstance(entry, dict) or set(entry) != {"start", "end", "name", "status", "score", "modes"}:
            raise ValueError("Each window needs start, end, name, status, score and modes")
        text(entry["name"], "window name")
        if entry["status"] not in {"avoid", "early", "active", "soft", "informal", "weak"}:
            raise ValueError("Unsupported working status")
        if not isinstance(entry["modes"], list) or not entry["modes"]:
            raise ValueError("Window modes must be a nonempty list")
        for mode in entry["modes"]:
            text(mode, "mode")
        windows.append(WindowRule(
            minute(entry["start"]), minute(entry["end"]), entry["name"],
            entry["status"], unit(entry["score"], "window.score"), tuple(entry["modes"]),
        ))
    windows.sort(key=lambda window: window.start)
    cursor = 0
    for window in windows:
        if window.start != cursor or window.end <= window.start:
            raise ValueError("Windows must cover 00:00..24:00 without gaps or overlaps")
        cursor = window.end
    if cursor != 1440:
        raise ValueError("Windows must end at 24:00")
    weights = scores(scoring.get("weights"), SCORE_KEYS, "weights")
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError("Ranking weights must sum to 1")
    for key in ("recency_days", "follow_up_due_days"):
        if type(scoring.get(key)) is not int or scoring[key] <= 0:
            raise ValueError(f"{key} must be a positive integer")
    return Settings(
        base_timezone, regions, tuple(windows), tuple(weekdays),
        unit(policy.get("weekend_multiplier"), "weekend_multiplier"),
        weights, scores(scoring.get("priority"), PRIORITIES, "priority"),
        scores(scoring.get("relationship"), RELATIONSHIPS, "relationship"),
        scores(scoring.get("actions"), ACTIONS, "actions"),
        scoring["recency_days"], scoring["follow_up_due_days"],
    )
