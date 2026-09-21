"""Small validated data contracts. Exported scores are heuristics."""

from dataclasses import dataclass, field
from datetime import date, datetime
import math

from ptime.core.timezone import get_zone

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
