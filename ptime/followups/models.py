from dataclasses import dataclass
from datetime import datetime

from ptime.core.timezone import aware_timestamp
from ptime.festivals.models import bounded_int
from ptime.models import CHANNELS, text


@dataclass(frozen=True)
class FollowupRequest:
    id: str
    contact_id: str
    channel: str
    cycle: str | None = None
    status: str = "pending"
    user_requested_at: datetime | None = None
    not_before: datetime | None = None
    due_at: datetime | None = None
    last_followup_at: datetime | None = None
    cooldown_hours: int = 168
    reply_delay_hours: int = 24
    opportunity_urgency: int = 0
    communication_asset_type: str = "follow_up"
    asset_ref: str | None = None

    def __post_init__(self):
        for name in ("id", "contact_id"):
            text(getattr(self, name), name)
        for name in ("cycle", "asset_ref"):
            if getattr(self, name) is not None:
                text(getattr(self, name), name)
        if self.channel not in CHANNELS or self.status not in {"pending", "completed", "canceled"}:
            raise ValueError("Invalid follow-up channel/status")
        if self.communication_asset_type not in {"self_introduction", "greeting", "follow_up", "thank_you", "career_update"}:
            raise ValueError("Unknown communication asset type")
        for name in ("user_requested_at", "not_before", "due_at", "last_followup_at"):
            object.__setattr__(self, name, aware_timestamp(getattr(self, name), name))
        bounded_int(self.cooldown_hours, "cooldown_hours", 24, 2160)
        bounded_int(self.reply_delay_hours, "reply_delay_hours", 24, 2160)
        bounded_int(self.opportunity_urgency, "opportunity_urgency", 0, 3)


@dataclass(frozen=True)
class FollowupRecommendation:
    id: str
    contact_id: str
    state: str
    reason: tuple[str, ...]
    channel: str
    followup_eligible_at: datetime | None = None
    due_at: datetime | None = None
    overdue: bool = False
    opportunity_urgency: int = 0
    communication_asset_type: str = "follow_up"
    asset_ref: str | None = None
    user_approval_required: bool = True
    calendar_verified: bool = False
