"""Config-driven layered calendars; unknown dated years are never extrapolated."""

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import yaml

from ptime.core.config import default_resource, read_document
from ptime.core.timezone import get_zone, localize, parse_instant
from ptime.festivals.models import Festival, FestivalOccurrence, bounded_int, strings
from ptime.models import day


@dataclass(frozen=True)
class CalendarCatalog:
    festivals: dict[str, Festival]
    views: dict[str, tuple[str, ...]]
    view_timezones: dict[str, str]

    def select(self, region=None, festival_id=None):
        if region is not None and region not in self.views:
            raise ValueError(f"Unknown calendar view: {region}")
        ids = self.views[region] if region else tuple(self.festivals)
        if festival_id is not None:
            if festival_id not in self.festivals:
                raise ValueError(f"Unknown festival: {festival_id}")
            ids = tuple(key for key in ids if key == festival_id)
        return [self.festivals[key] for key in ids]


def load_calendars(config_dir: Path | None = None) -> CalendarCatalog:
    if config_dir is None:
        names = ("chinese", "global", "united_states", "united_kingdom")
        docs = [yaml.safe_load(default_resource(f"festivals/{name}.yaml").read_text(encoding="utf-8")) for name in names]
    else:
        paths = sorted((config_dir / "festivals").glob("*.yaml"))
        if not paths:
            raise ValueError("No festival calendar configuration found")
        docs = [read_document(path) for path in paths]
    festivals, views, zones = {}, {}, {}
    for doc in docs:
        if not isinstance(doc, dict) or set(doc) != {"views", "defaults", "festivals", "include"}:
            raise ValueError("Calendar needs views/defaults/festivals/include")
        if not isinstance(doc["defaults"], dict) or not isinstance(doc["festivals"], list):
            raise ValueError("Invalid calendar configuration")
        strings(doc["views"], "calendar views")
        strings(doc["include"], "calendar includes")
        ids = []
        for row in doc["festivals"]:
            festival = Festival(**(doc["defaults"] | row))
            if festival.id in festivals:
                raise ValueError("Duplicate canonical festival ID; use include")
            festivals[festival.id] = festival
            ids.append(festival.id)
        for name in doc["views"]:
            if name in views:
                raise ValueError("Duplicate calendar view")
            views[name] = tuple(ids + doc["include"])
            zones[name] = doc["defaults"]["default_timezone"]
    if any(key not in festivals for ids in views.values() for key in ids):
        raise ValueError("Calendar include refers to unknown festival")
    return CalendarCatalog(festivals, views, zones)


def festival_date(festival: Festival, year: int) -> date | None:
    bounded_int(year, "year", 1900, 2200)
    rule = festival.cultural_date_rule
    if rule["type"] == "dates":
        return day(rule["dates"].get(year), "festival date")
    if rule["type"] == "fixed":
        try:
            return date(year, rule["month"], rule["day"])
        except ValueError:
            return None
    month, weekday, nth = rule["month"], rule["weekday"], rule["nth"]
    if nth == -1:
        end = date(year, month, monthrange(year, month)[1])
        return end - timedelta(days=(end.weekday() - weekday) % 7)
    start = date(year, month, 1)
    return start + timedelta(days=(weekday - start.weekday()) % 7 + 7 * (nth - 1))


def occurrence(festival: Festival, year: int, zone: str | None = None) -> FestivalOccurrence | None:
    value = festival_date(festival, year)
    if value is None:
        return None
    zone = zone or festival.default_timezone
    get_zone(zone)
    start = datetime.combine(value - timedelta(days=festival.lead_days), time())
    end = datetime.combine(value + timedelta(days=festival.valid_window_days), time())
    # Reject rare midnight gaps rather than silently attach an invalid zone offset.
    return FestivalOccurrence(festival.id, festival.name, f"{festival.id}:{year}", value, zone,
                              parse_instant(start.isoformat(), zone), parse_instant(end.isoformat(), zone),
                              tuple(p for p in festival.official_holiday_period if p.start.year == year),
                              festival.greeting_appropriate, festival.source_note)


def upcoming(catalog, instant, days=30, region=None, festival_id=None, zone=None, include_non_greeting=False):
    bounded_int(days, "days", 0, 366)
    results, warnings = [], []
    for festival in catalog.select(region, festival_id):
        if not festival.enabled or (not include_non_greeting and not festival.greeting_appropriate):
            continue
        effective_zone = zone or catalog.view_timezones.get(region) or festival.default_timezone
        local = localize(instant, effective_zone)
        end = local.date() + timedelta(days=days)
        for year in range((local.date() - timedelta(days=festival.valid_window_days)).year, end.year + 1):
            item = occurrence(festival, year, effective_zone)
            if item is None:
                warnings.append(f"UNKNOWN date: {festival.id} / {year}; extend sourced calendar data")
            elif item.expires_at > instant.astimezone(timezone.utc) and item.cultural_date <= end:
                results.append(item)
    return sorted(results, key=lambda x: (x.cultural_date, x.festival_id)), sorted(set(warnings))
