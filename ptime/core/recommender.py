"""Eligibility gates precede ranking so priority cannot defeat quiet hours."""

from datetime import date, datetime

from ptime.agents.time_adapter import TimeAdapterAgent
from ptime.core.config import Settings, load_settings
from ptime.core.scoring import components, rank_score
from ptime.core.timezone import require_aware
from ptime.models import CommunicationAction, Contact, Region, TimeRecommendation, TimeWindow

ACTION_TEXT = {
    "follow_up": "Draft a professional follow-up",
    "informal_chat": "Suggest an informal catch-up",
    "interview": "Propose an interview slot; confirm availability first",
    "coffee_chat": "Propose a coffee-chat slot; confirm availability first",
    "research_discussion": "Draft a focused research question",
    "recruiting_message": "Draft a recruiting message",
    "application_follow_up": "Draft an application follow-up",
    "relationship_maintenance": "Draft a light catch-up message",
}


def gate(contact: Contact, window: TimeWindow) -> str | None:
    if contact.do_not_contact:
        return "Do-not-contact preference: no outreach"
    if window.working_status in {"avoid", "weak", "early"}:
        return "Outside the default contact window; prepare a draft for later"
    if contact.next_action in {"follow_up", "application_follow_up"} and contact.last_contact == date.fromisoformat(window.local_date):
        return "Already contacted today; do not send another same-day follow-up"
    informal = contact.relationship == "friend" and contact.next_action in {"informal_chat", "relationship_maintenance"}
    if window.working_status in {"weekend", "informal"} and not informal:
        return "Outside professional working hours; defer professional outreach"
    if contact.next_action in {"interview", "coffee_chat"} and window.working_status != "active":
        return "Soft window: defer proposing an immediate synchronous conversation"
    return None


def recommend(contacts: list[Contact], instant: datetime, settings: Settings | None = None) -> list[TimeRecommendation]:
    require_aware(instant)
    settings = settings or load_settings()
    time_agent = TimeAdapterAgent(settings)
    results = []
    seen = set()
    for contact in contacts:
        identity = (contact.name.casefold(), contact.organization.casefold(), contact.timezone)
        if identity in seen:
            raise ValueError("Duplicate contact identity in input; reconcile exports before ranking")
        seen.add(identity)
        window = time_agent.window_for(instant, Region(contact.location, contact.timezone))
        values, reasons = components(contact, window, settings)
        blocked_reason = gate(contact, window)
        available = round(
            window.communication_score * settings.relationships[contact.relationship] * settings.actions[contact.next_action], 6
        )
        if blocked_reason:
            reasons.append(blocked_reason)
        else:
            reasons.append("Time-window suggestion only; confirm personal availability and preferences")
        recommendation = blocked_reason or ACTION_TEXT[contact.next_action]
        if not blocked_reason and contact.topics:
            recommendation += "; topic: " + ", ".join(contact.topics[:2])
        if not blocked_reason and window.working_status == "soft":
            recommendation += "; asynchronous message only"
        action = CommunicationAction(contact.next_action, recommendation, "defer" if blocked_reason else "suggested")
        results.append(TimeRecommendation(
            contact.name, contact.organization, contact.location, contact.timezone,
            window.local_time, window.local_date, window.local_datetime, contact.priority,
            0.0 if blocked_reason else available,
            0.0 if blocked_reason else rank_score(values, settings),
            blocked_reason is None, action, tuple(reasons), values, contact.source, contact.synthetic,
        ))
    return sorted(results, key=lambda r: (not r.eligible_now, -r.final_score, r.person.casefold(), r.organization.casefold(), r.timezone))
