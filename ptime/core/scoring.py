"""Transparent bounded ranking components, not calibrated response probabilities."""

from datetime import date

from ptime.core.config import Settings
from ptime.models import Contact, TimeWindow


def components(contact: Contact, window: TimeWindow, settings: Settings) -> tuple[dict[str, float], list[str]]:
    local_day = date.fromisoformat(window.local_date)
    reasons = [f"{window.region}: {window.working_status} / {window.window}", f"{contact.priority} priority"]
    recency = 0.5
    if contact.last_contact is None:
        reasons.append("Last contact unknown; neutral recency score")
    else:
        elapsed = (local_day - contact.last_contact).days
        if elapsed < 0:
            raise ValueError(f"last_contact is after the evaluation date for {contact.name}")
        recency = min(elapsed / settings.recency_days, 1.0)
        reasons.append(f"Last contact {elapsed} local calendar days ago")
        if contact.next_action in {"follow_up", "application_follow_up"} and elapsed >= settings.follow_up_due_days:
            reasons.append(f"Follow-up due by the configured {settings.follow_up_due_days}-day heuristic")
    active = [o for o in contact.opportunities if o.active_on(local_day)]
    if active:
        reasons.append("Active opportunity in local input: " + ", ".join(o.title for o in active))
    else:
        reasons.append("No active opportunity recorded in the local input")
    values = {
        "time_score": window.communication_score,
        "contact_priority": settings.priorities[contact.priority],
        "relationship_score": settings.relationships[contact.relationship],
        "recency_score": recency,
        "opportunity_score": float(bool(active)),
    }
    return values, reasons


def rank_score(values: dict[str, float], settings: Settings) -> float:
    return round(sum(settings.weights[key] * value for key, value in values.items()), 6)
