"""Small validated data contracts. Exported scores are heuristics."""

from dataclasses import dataclass, field
from datetime import date, datetime
import math

from ptime.core.timezone import aware_timestamp, get_zone, localize, wall_interval

CHANNELS = {"email", "linkedin", "wechat", "whatsapp", "telegram", "phone", "video_call", "in_person"}
CONTEXTS = {"professional", "semi_professional", "informal", "personal"}

RELATIONSHIPS = {
    "friend", "researcher", "headhunter", "recruiter", "hr",
    "hiring_manager", "pm", "founder", "alumni", "professional_contact",
}
ACTIONS = {
    "follow_up", "informal_chat", "interview", "coffee_chat", "research_discussion",
    "recruiting_message", "application_follow_up", "relationship_maintenance",
}
PRIORITIES = {"P0", "P1", "P2", "P3"}


def unit(value: float, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{label} must be a finite number from 0 to 1")
    return float(value)


def text(value: str, label: str, allow_empty: bool = False) -> None:
    if not isinstance(value, str) or (not allow_empty and not value.strip()) or len(value) > 1000:
        raise ValueError(f"{label} must be nonempty text (up to 1000 characters)")
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError(f"{label} must not contain terminal control characters")


def day(value: str | date | None, label: str) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        raise ValueError(f"{label} must be a local ISO date, not a timestamp")
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError(f"{label} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO date") from exc


@dataclass(frozen=True)
class Region:
    region: str
    timezone: str

    def __post_init__(self):
        text(self.region, "region")
        get_zone(self.timezone)


@dataclass(frozen=True)
class TimeWindow:
    region: str
    timezone: str
    local_time: str
    local_date: str
    local_datetime: str
    utc_offset: str
    weekday: str
    period: str
    window: str
    working_status: str
    time_score: float
    weekday_score: float
    communication_score: float
    recommended_modes: tuple[str, ...]
    calendar_verified: bool = False


@dataclass(frozen=True)
class Opportunity:
    id: str
    title: str
    status: str = "active"
    deadline: date | None = None

    def __post_init__(self):
        text(self.id, "opportunity.id")
        text(self.title, "opportunity.title")
        if self.status not in {"active", "closed", "expired"}:
            raise ValueError("Opportunity status must be active, closed or expired")
        object.__setattr__(self, "deadline", day(self.deadline, "deadline"))

    def active_on(self, local_date: date) -> bool:
        return self.status == "active" and (self.deadline is None or self.deadline >= local_date)


@dataclass(frozen=True)
class Contact:
    name: str
    location: str
    timezone: str
    organization: str = ""
    relationship: str = "professional_contact"
    priority: str = "P2"
    topics: tuple[str, ...] = ()
    last_contact: date | None = None
    next_action: str = "follow_up"
    opportunities: tuple[Opportunity, ...] = ()
    do_not_contact: bool = False
    synthetic: bool = False
    source: str = "local"
    id: str = ""
    channels: tuple[str, ...] = ()
    last_contact_at: datetime | None = None
    next_action_due: datetime | None = None
    preferred_contact_windows: tuple[str, ...] = ()
    source_systems: tuple[str, ...] = ()
    context: str = "professional"

    def __post_init__(self):
        for key in ("name", "location", "source"):
            text(getattr(self, key), key)
        text(self.organization, "organization", allow_empty=True)
        get_zone(self.timezone)
        if self.relationship not in RELATIONSHIPS:
            raise ValueError("Unknown relationship type")
        if self.priority not in PRIORITIES:
            raise ValueError("Priority must be P0, P1, P2 or P3")
        if self.next_action not in ACTIONS:
            raise ValueError("Unknown communication action")
        if type(self.do_not_contact) is not bool or type(self.synthetic) is not bool:
            raise ValueError("do_not_contact and synthetic must be booleans")
        if not isinstance(self.topics, (tuple, list)):
            raise ValueError("topics must be a list of strings")
        for topic in self.topics:
            text(topic, "topic")
        object.__setattr__(self, "topics", tuple(self.topics))
        object.__setattr__(self, "last_contact", day(self.last_contact, "last_contact"))
        if not isinstance(self.opportunities, (tuple, list)) or any(not isinstance(o, Opportunity) for o in self.opportunities):
            raise ValueError("opportunities must contain Opportunity objects")
        object.__setattr__(self, "opportunities", tuple(self.opportunities))
        text(self.id, "id", allow_empty=True)
        if self.context not in CONTEXTS:
            raise ValueError("Unknown communication context")
        for key in ("channels", "preferred_contact_windows", "source_systems"):
            value = getattr(self, key)
            if not isinstance(value, (list, tuple)):
                raise ValueError(f"{key} must be a list")
            for item in value:
                text(item, key)
            if len(set(value)) != len(value):
                raise ValueError(f"{key} must not contain duplicates")
            object.__setattr__(self, key, tuple(value))
        if set(self.channels) - CHANNELS:
            raise ValueError("Unknown communication channel")
        for window in self.preferred_contact_windows:
            wall_interval(window)
        for key in ("last_contact_at", "next_action_due"):
            object.__setattr__(self, key, aware_timestamp(getattr(self, key), key))
        if self.last_contact_at is not None:
            contact_day = localize(self.last_contact_at, self.timezone).date()
            if self.last_contact is not None and self.last_contact != contact_day:
                raise ValueError("last_contact and last_contact_at disagree in the contact timezone")
            object.__setattr__(self, "last_contact", contact_day)


@dataclass(frozen=True)
class PendingAction:
    id: str
    contact_id: str
    channel: str
    kind: str = "follow_up"
    context: str = "professional"
    status: str = "draft"
    priority: str | None = None
    due_at: datetime | None = None
    not_before: datetime | None = None
    expected_reply: bool = False
    scheduled_at: datetime | None = None
    scheduled_until: datetime | None = None
    confirmed: bool = False

    def __post_init__(self):
        text(self.id, "action.id")
        text(self.contact_id, "action.contact_id")
        if self.channel not in CHANNELS or self.context not in CONTEXTS:
            raise ValueError("Unknown action channel or context")
        if self.kind not in ACTIONS | {"reply"}:
            raise ValueError("Unknown action kind")
        if self.status not in {"draft", "pending", "sent", "completed", "canceled"}:
            raise ValueError("Unknown action status")
        if self.priority is not None and self.priority not in PRIORITIES:
            raise ValueError("Invalid action priority")
        if type(self.expected_reply) is not bool or type(self.confirmed) is not bool:
            raise ValueError("expected_reply and confirmed must be booleans")
        for key in ("due_at", "not_before", "scheduled_at", "scheduled_until"):
            object.__setattr__(self, key, aware_timestamp(getattr(self, key), key))
        if (self.scheduled_at is None) != (self.scheduled_until is None):
            raise ValueError("Scheduled actions require both start and end")
        if self.scheduled_at and not self.scheduled_at < self.scheduled_until:
            raise ValueError("Scheduled end must be after start")
        if self.confirmed and self.scheduled_at is None:
            raise ValueError("confirmed requires an explicit scheduled interval")
        if self.scheduled_at and self.channel not in {"phone", "video_call", "in_person"}:
            raise ValueError("Scheduled meeting intervals require a synchronous channel")
        if self.expected_reply and self.kind != "reply":
            raise ValueError("expected_reply must describe a reply, not a new outreach")


@dataclass(frozen=True)
class RoutedAction:
    contact_id: str
    person: str
    region: str
    timezone: str
    local_datetime: str
    action_id: str
    channel: str | None
    context: str
    kind: str
    decision: str
    score: float
    reasons: tuple[str, ...]
    suggested_action: str
    next_window_at: str | None = None
    next_window_local: str | None = None
    components: dict[str, float] = field(default_factory=dict)
    topics: tuple[str, ...] = ()
    source_systems: tuple[str, ...] = ()
    due_at: str | None = None
    overdue: bool = False
    synthetic: bool = False
    requires_human_approval: bool = True
    calendar_verified: bool = False
    available_channels: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommunicationAction:
    kind: str
    recommendation: str
    status: str
    requires_human_approval: bool = True


@dataclass(frozen=True)
class TimeRecommendation:
    person: str
    organization: str
    location: str
    timezone: str
    local_time: str
    local_date: str
    local_datetime: str
    priority: str
    availability_score: float
    final_score: float
    eligible_now: bool
    recommended_action: CommunicationAction
    reason: tuple[str, ...]
    components: dict[str, float] = field(default_factory=dict)
    source: str = "local"
    synthetic: bool = False
    calendar_verified: bool = False
