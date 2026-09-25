"""Small, validated calendar and relationship snapshot contracts."""

from dataclasses import dataclass, field
from datetime import date, datetime

from ptime.core.timezone import aware_timestamp, get_zone
from ptime.models import CHANNELS, day, text

STYLES = {"general", "professional", "reconnect"}
ASYNC_CHANNELS = CHANNELS - {"phone", "video_call", "in_person"}


def bounded_int(value, label, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{label} must be an integer between {low} and {high}")


def strings(value, label):
    if not isinstance(value, (list, tuple)) or len(value) > 100:
        raise ValueError(f"{label} must be a bounded list")
    for item in value:
        text(item, label)
    if len(set(value)) != len(value):
        raise ValueError(f"{label} contains duplicates")
    return tuple(value)


def flags(obj, *names):
    for name in names:
        if type(getattr(obj, name)) is not bool:
            raise ValueError(f"{name} must be boolean")


@dataclass(frozen=True)
class HolidayPeriod:
    region: str
    start: date
    end: date
    source_note: str

    def __post_init__(self):
        text(self.region, "holiday region")
        text(self.source_note, "holiday source")
        for name in ("start", "end"):
            object.__setattr__(self, name, day(getattr(self, name), name))
        if not self.start or not self.end or self.end < self.start:
            raise ValueError("Holiday requires inclusive start <= end")


@dataclass(frozen=True)
class Festival:
    id: str
    name: str
    canonical_name: str
    locale: str
    country_or_region: str
    region_tags: tuple[str, ...]
    calendar_type: str
    cultural_date_rule: dict
    default_timezone: str
    source_note: str
    official_holiday_period: tuple[HolidayPeriod, ...] = ()
    greeting_appropriate: bool = True
    professional_greeting_appropriate: bool = True
    reconnect_appropriate: bool = True
    suggested_channels: tuple[str, ...] = ("email", "wechat", "linkedin")
    lead_days: int = 2
    valid_window_days: int = 2
    enabled: bool = True

    def __post_init__(self):
        for name in ("id", "name", "canonical_name", "locale", "country_or_region", "calendar_type", "source_note"):
            text(getattr(self, name), name)
        get_zone(self.default_timezone)
        for name in ("region_tags", "suggested_channels"):
            object.__setattr__(self, name, strings(getattr(self, name), name))
        if not self.suggested_channels or set(self.suggested_channels) - ASYNC_CHANNELS:
            raise ValueError("Greeting channels must be explicit asynchronous channels")
        flags(self, "enabled", "greeting_appropriate", "professional_greeting_appropriate", "reconnect_appropriate")
        bounded_int(self.lead_days, "lead_days", 0, 30)
        bounded_int(self.valid_window_days, "valid_window_days", 1, 30)
        periods = tuple(p if isinstance(p, HolidayPeriod) else HolidayPeriod(**p) for p in self.official_holiday_period)
        object.__setattr__(self, "official_holiday_period", periods)
        rule = self.cultural_date_rule
        if not isinstance(rule, dict):
            raise ValueError("cultural_date_rule must be a mapping")
        kind = rule.get("type")
        required = {"fixed": {"type", "month", "day"}, "nth_weekday": {"type", "month", "weekday", "nth"}, "dates": {"type", "dates"}}
        if kind not in required or set(rule) != required[kind]:
            raise ValueError("Unknown or malformed date rule")
        if kind == "dates":
            if not isinstance(rule["dates"], dict) or not rule["dates"]:
                raise ValueError("Explicit dated calendar must not be empty")
            for year, value in rule["dates"].items():
                bounded_int(year, "calendar year", 1900, 2200)
                parsed = day(value, "festival date")
                if parsed is None or parsed.year != year:
                    raise ValueError("Calendar date must be present and match its year")
        else:
            bounded_int(rule["month"], "month", 1, 12)
            if kind == "fixed":
                bounded_int(rule["day"], "day", 1, 31)
                date(2000, rule["month"], rule["day"])
            else:
                bounded_int(rule["weekday"], "weekday", 0, 6)
                if type(rule["nth"]) is not int or rule["nth"] not in {-1, 1, 2, 3, 4}:
                    raise ValueError("nth must be -1 (last) or 1..4")


@dataclass(frozen=True)
class FestivalOccurrence:
    festival_id: str
    name: str
    cycle: str
    cultural_date: date
    timezone: str
    not_before: datetime
    expires_at: datetime
    official_holiday_period: tuple[HolidayPeriod, ...]
    greeting_appropriate: bool
    source_note: str


@dataclass(frozen=True)
class GreetingPreference:
    contact_id: str
    festival_ids: tuple[str, ...] = ()
    excluded_festival_ids: tuple[str, ...] = ()
    style: str = "general"
    locale: str = "en"
    audience: str = "general"
    active_conversation: bool = False
    recent_contact_hours: int = 72
    allow_active_conversation: bool = False
    allow_recent_contact: bool = False
    reset_cycles: tuple[str, ...] = ()

    def __post_init__(self):
        text(self.contact_id, "contact_id")
        text(self.audience, "audience")
        if self.style not in STYLES or self.locale not in {"en", "zh-CN"}:
            raise ValueError("Unsupported greeting style/locale")
        for name in ("festival_ids", "excluded_festival_ids", "reset_cycles"):
            object.__setattr__(self, name, strings(getattr(self, name), name))
        flags(self, "active_conversation", "allow_active_conversation", "allow_recent_contact")
        bounded_int(self.recent_contact_hours, "recent_contact_hours", 1, 720)


@dataclass(frozen=True)
class GreetingRecord:
    contact_id: str
    festival_id: str
    cycle: str
    template_id: str
    channel: str
    greeted_at: datetime
    reply_state: str = "no_reply"
    replied_at: datetime | None = None
    closed: bool = False

    def __post_init__(self):
        for name in ("contact_id", "festival_id", "cycle", "template_id"):
            text(getattr(self, name), name)
        if self.channel not in CHANNELS or self.reply_state not in {"no_reply", "replied", "declined"}:
            raise ValueError("Invalid greeting channel/reply state")
        for name in ("greeted_at", "replied_at"):
            object.__setattr__(self, name, aware_timestamp(getattr(self, name), name))
        if self.greeted_at is None or (self.reply_state == "replied") != (self.replied_at is not None):
            raise ValueError("Greeting/reply state needs matching timestamps")
        if self.replied_at and self.replied_at < self.greeted_at:
            raise ValueError("Reply cannot precede greeting")
        flags(self, "closed")


@dataclass(frozen=True)
class FestivalTouchpoint:
    contact_id: str
    festival_id: str
    cycle: str
    relationship_class: str
    state: str
    reason: tuple[str, ...]
    not_before: datetime
    expires_at: datetime
    recommended_template_id: str | None = None
    recommended_channel: str | None = None
    last_contact_at: datetime | None = None
    duplicate_suppressed: bool = False
    recent_contact_suppressed: bool = False
    reply_state: str = "none"
    followup_eligible_at: datetime | None = None
    score: float = 0.0
    score_components: dict[str, float] = field(default_factory=dict)
    user_approval_required: bool = True
    calendar_verified: bool = False
