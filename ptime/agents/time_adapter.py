"""Time Adapter Agent: one instant to heuristic regional working windows."""

from datetime import datetime

from ptime.core.config import Settings, load_settings
from ptime.core.timezone import localize, require_aware
from ptime.models import Region, TimeWindow

WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


class TimeAdapterAgent:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()

    def window_for(self, instant: datetime, region: Region) -> TimeWindow:
        local = localize(instant, region.timezone)
        minute = local.hour * 60 + local.minute
        rule = next(rule for rule in self.settings.windows if rule.start <= minute < rule.end)
        working_day = local.weekday() in self.settings.working_weekdays
        multiplier = 1.0 if working_day else self.settings.weekend_multiplier
        status = rule.status
        modes = rule.modes
        if not working_day and rule.status in {"active", "soft"}:
            status = "weekend"
            modes = ("informal_chat_by_agreement", "draft_for_later")
        period = "night" if local.hour < 7 or local.hour >= 23 else (
            "morning" if local.hour < 12 else "afternoon" if local.hour < 18 else "evening"
        )
        offset = local.strftime("%z")
        return TimeWindow(
            region.region, region.timezone, local.strftime("%H:%M"), local.date().isoformat(),
            local.isoformat(timespec="seconds"), offset[:3] + ":" + offset[3:],
            WEEKDAYS[local.weekday()], period, rule.name, status,
            rule.score, multiplier, round(rule.score * multiplier, 6), modes,
        )

    def run(self, instant: datetime, region_ids: list[str] | None = None) -> list[TimeWindow]:
        require_aware(instant)
        identifiers = list(self.settings.regions) if region_ids is None else region_ids
        unknown = set(identifiers) - self.settings.regions.keys()
        if unknown:
            raise ValueError("Unknown region IDs: " + ", ".join(sorted(unknown)))
        return [self.window_for(instant, self.settings.regions[key]) for key in dict.fromkeys(identifiers)]
