"""IANA conversion with explicit handling of DST wall-time ambiguity."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import re


def get_zone(name: str) -> ZoneInfo:
    if not isinstance(name, str) or not name or ("/" not in name and name != "UTC"):
        raise ValueError("Use an IANA timezone such as Europe/London, not CST/EST or an offset")
    try:
        return ZoneInfo(name)
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise ValueError(f"Invalid or unavailable IANA timezone: {name}. Install/update tzdata.") from exc


def require_aware(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("A timezone-aware instant is required")
    # Reject manually attached zoneinfo values representing a nonexistent wall time.
    restored = value.astimezone(timezone.utc).astimezone(value.tzinfo)
    if restored.replace(tzinfo=None) != value.replace(tzinfo=None):
        raise ValueError("Nonexistent local time; provide a valid offset-aware instant")
    return value


def parse_instant(value: str | None, base_timezone: str = "Asia/Shanghai") -> datetime:
    zone = get_zone(base_timezone)
    if value is None:
        return datetime.now(timezone.utc)
    if not isinstance(value, str) or "T" not in value:
        raise ValueError("--at needs a full ISO date and time, e.g. 2026-09-21T22:15")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Invalid ISO timestamp; include date and time") from exc
    if parsed.tzinfo is not None:
        return parsed.astimezone(timezone.utc)

    candidates = set()
    for fold in (0, 1):
        candidate = parsed.replace(tzinfo=zone, fold=fold)
        utc = candidate.astimezone(timezone.utc)
        if utc.astimezone(zone).replace(tzinfo=None) == parsed:
            candidates.add(utc)
    if not candidates:
        raise ValueError("Nonexistent local time at a DST transition; choose another time")
    if len(candidates) > 1:
        raise ValueError("Ambiguous local time at a DST transition; include an explicit UTC offset")
    return candidates.pop()


def localize(instant: datetime, timezone_name: str) -> datetime:
    return require_aware(instant).astimezone(get_zone(timezone_name))


def aware_timestamp(value: str | datetime | None, label: str) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, str):
        if "T" not in value:
            raise ValueError(f"{label} requires an offset-aware ISO datetime")
        try:
            value = datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"{label} requires an offset-aware ISO datetime") from exc
    return require_aware(value).astimezone(timezone.utc)


def wall_interval(value: str) -> tuple[int, int]:
    if not isinstance(value, str) or not re.fullmatch(r"\d{2}:\d{2}-\d{2}:\d{2}", value):
        raise ValueError("Contact windows must use HH:MM-HH:MM")
    def minutes(clock: str) -> int:
        hour, minute = map(int, clock.split(":"))
        if not 0 <= hour <= 24 or not 0 <= minute < 60 or (hour == 24 and minute):
            raise ValueError("Invalid contact window clock")
        return hour * 60 + minute
    start, end = map(minutes, value.split("-"))
    if not 0 <= start < end <= 1440:
        raise ValueError("Contact windows must increase within a day; split overnight windows")
    return start, end
