"""Time/channel/context routing. Decisions never execute a communication."""

from dataclasses import replace
from datetime import datetime, time, timedelta, timezone

from ptime.agents.time_adapter import TimeAdapterAgent
from ptime.core.channels import ChannelPolicy, contains, load_channels
from ptime.core.config import Settings, load_settings
from ptime.core.recommender import ACTION_TEXT
from ptime.core.scoring import components, rank_score
from ptime.core.timezone import get_zone, localize, require_aware, wall_interval
from ptime.integrations.base import validate_snapshot
from ptime.models import Contact, PendingAction, Region, RoutedAction

ACTIVE = {"draft", "pending"}


def eligible(contact: Contact, action: PendingAction, instant: datetime,
             settings: Settings, policy: ChannelPolicy) -> tuple[bool, str]:
    local = localize(instant, contact.timezone)
    minute = local.hour * 60 + local.minute
    channel = policy.channels[action.channel]
    context = policy.contexts[action.context]
    if action.not_before and instant < action.not_before:
        return False, "Explicit not_before time has not arrived"
    if action.confirmed:
        if action.scheduled_at <= instant < action.scheduled_until:
            return True, "Inside explicitly confirmed local-input meeting interval; calendar unverified"
        return False, "Wait for the explicitly confirmed meeting interval"

    # A queued request is not evidence of a scheduled meeting.
    if action.scheduled_at:
        return False, "Scheduled interval is unconfirmed; human confirmation required"
    if contact.last_contact == local.date() and action.kind in {"follow_up", "application_follow_up"}:
        return False, "Already contacted today; do not repeat a same-day follow-up"
    preferred = tuple(wall_interval(window) for window in contact.preferred_contact_windows)
    if preferred and not contains(preferred, minute):
        return False, "Outside the contact's explicit preferred windows"
    if contains(policy.quiet, minute):
        return False, "Quiet hours; priority does not override rest"
    late = contains(policy.late_reply, minute)
    synchronous = channel.synchronous or action.kind in {"interview", "coffee_chat"}
    if not synchronous and late:
        if action.expected_reply and action.kind == "reply":
            return True, "Explicit expected-reply context permits an asynchronous late reply"
        if contact.relationship == "friend" and action.context in {"informal", "personal"} and preferred:
            return True, "Friend explicitly prefers this late window; informal asynchronous suggestion"
    if not contains(channel.windows, minute):
        return False, f"Outside {action.channel} timing windows"
    if not contains(context.windows, minute):
        return False, f"Outside {action.context} timing windows"
    if context.working_days_only and local.weekday() not in settings.working_weekdays:
        return False, "Recipient-local nonworking day for this communication context"
    if action.context in {"personal", "informal"} and local.weekday() not in settings.working_weekdays and contact.relationship != "friend":
        return False, "Weekend informal outreach needs a friend relationship by default"
    if synchronous:
        if not contains(policy.synchronous_windows, minute) or local.weekday() not in settings.working_weekdays:
            return False, "Synchronous interaction needs a working-day meeting window or confirmed interval"
    return True, f"{action.channel} + {action.context} fits local timing policy; verify availability"


def next_window(contact: Contact, action: PendingAction, instant: datetime,
                settings: Settings, policy: ChannelPolicy) -> datetime | None:
    """Search rule boundaries as real instants, preserving both DST folds and skipping gaps."""
    zone = get_zone(contact.timezone)
    first_day = localize(instant, contact.timezone).date()
    horizon_day = first_day + timedelta(days=policy.search_days)
    edges = policy.boundaries()
    for preferred in contact.preferred_contact_windows:
        edges.update(wall_interval(preferred))
    candidates = set()
    for day_offset in range(policy.search_days + 1):
        date = first_day + timedelta(days=day_offset)
        for minute in edges:
            wall = datetime.combine(date, time()) + timedelta(minutes=minute)
            if wall.date() > horizon_day:
                continue
            for fold in (0, 1):
                candidate = wall.replace(tzinfo=zone, fold=fold).astimezone(timezone.utc)
                if candidate.astimezone(zone).replace(tzinfo=None) == wall and candidate > instant:
                    candidates.add(candidate)
    for exact in (action.not_before, action.scheduled_at):
        if exact and exact > instant and localize(exact, contact.timezone).date() <= horizon_day:
            candidates.add(exact)
    # Offset transitions can jump into a valid window whose wall-clock start never existed.
    # Probe UTC in 30-minute increments only near an offset change, then locate its minute.
    start = instant.astimezone(timezone.utc).replace(second=0, microsecond=0)
    previous = start
    for step in range(1, (policy.search_days + 1) * 48 + 1):
        current = start + timedelta(minutes=30 * step)
        if previous.astimezone(zone).utcoffset() != current.astimezone(zone).utcoffset():
            for minute in range(1, 31):
                candidate = previous + timedelta(minutes=minute)
                if candidate > instant and localize(candidate, contact.timezone).date() <= horizon_day:
                    candidates.add(candidate)
        previous = current
    return next((candidate for candidate in sorted(candidates)
                 if eligible(contact, action, candidate, settings, policy)[0]), None)


def route_one(contact: Contact, action: PendingAction, instant: datetime,
              settings: Settings, policy: ChannelPolicy) -> RoutedAction:
    local = localize(instant, contact.timezone)
    reason = None
    decision = "WAIT"
    if action.status not in ACTIVE:
        decision, reason = "SKIP", f"Action is already {action.status}; never re-route it as a new draft"
    elif contact.do_not_contact:
        decision, reason = "BLOCKED", "Do-not-contact preference"
    elif action.channel not in contact.channels:
        decision, reason = "REVIEW", "Action channel is not in the contact's allowed channels"
    elif action.confirmed and instant >= action.scheduled_until:
        decision, reason = "SKIP", "Confirmed meeting interval has ended; do not move it automatically"
    elif action.scheduled_at and not action.confirmed:
        decision, reason = "REVIEW", "Scheduled interval is unconfirmed; no automatic confirmation"
    elif action.kind == "reply" and not action.expected_reply:
        decision, reason = "REVIEW", "Reply action needs explicit expected_reply context"

    effective = replace(contact, priority=action.priority or contact.priority,
                        next_action=action.kind if action.kind != "reply" else "research_discussion")
    window = TimeAdapterAgent(settings).window_for(instant, Region(contact.location, contact.timezone))
    values, reasons = components(effective, window, settings)
    values["time_score"] = round(values["time_score"] * policy.channels[action.channel].score, 6)
    upcoming = None
    if reason is None:
        allowed, reason = eligible(contact, action, instant, settings, policy)
        decision = "SEND_NOW" if allowed else "WAIT"
        if not allowed:
            upcoming = next_window(contact, action, instant, settings, policy)
            if upcoming is None:
                reasons.append(f"No suitable window found within {policy.search_days} local days")
    reasons.append(reason)
    due = action.due_at or contact.next_action_due
    overdue = bool(due and instant > due)
    if due:
        reasons.append("Due time passed (soft deadline)" if overdue else "Due time recorded (not an automatic send time)")
    if action.confirmed:
        suggestion = "Join only the explicitly agreed conversation; verify it is still on"
    else:
        suggestion = "Prepare the expected reply" if action.kind == "reply" else ACTION_TEXT[action.kind]
    if decision != "SEND_NOW":
        suggestion = reason
    score = rank_score(values, settings) if decision == "SEND_NOW" else 0.0
    return RoutedAction(
        contact.id, contact.name, contact.location, contact.timezone, local.isoformat(),
        action.id, action.channel, action.context, action.kind, decision, score,
        tuple(reasons), suggestion,
        upcoming.isoformat() if upcoming else None,
        localize(upcoming, contact.timezone).isoformat() if upcoming else None,
        values, contact.topics, tuple(dict.fromkeys((*contact.source_systems, contact.source))),
        due.isoformat() if due else None, overdue, contact.synthetic,
    )


def route(contacts: list[Contact], pending_actions: list[PendingAction], instant: datetime,
          settings: Settings | None = None, policy: ChannelPolicy | None = None,
          email_only: bool = False) -> list[RoutedAction]:
    require_aware(instant)
    validate_snapshot(contacts, pending_actions)
    settings, policy = settings or load_settings(), policy or load_channels()
    for contact in contacts:
        if contact.last_contact_at and contact.last_contact_at > instant:
            raise ValueError("last_contact_at is after the evaluation instant")
        if contact.last_contact and contact.last_contact > localize(instant, contact.timezone).date():
            raise ValueError("last_contact is after the evaluation date")
    by_id = {contact.id: contact for contact in contacts}
    result = []
    queued = {action.contact_id for action in pending_actions}
    for action in pending_actions:
        if not email_only or action.channel == "email":
            result.append(route_one(by_id[action.contact_id], action, instant, settings, policy))
    if not email_only:
        for contact in contacts:
            if contact.id in queued:
                continue
            if not contact.channels:
                missing_reason = "Do-not-contact preference" if contact.do_not_contact else "No contact channel supplied; do not invent one"
                result.append(RoutedAction(
                    contact.id, contact.name, contact.location, contact.timezone,
                    localize(instant, contact.timezone).isoformat(), f"suggested:{contact.id}",
                    None, contact.context, contact.next_action, "BLOCKED" if contact.do_not_contact else "REVIEW", 0,
                    (missing_reason,), missing_reason,
                    synthetic=contact.synthetic, source_systems=(contact.source,),
                ))
                continue
            choices = [route_one(contact, PendingAction(
                f"suggested:{contact.id}:{channel}", contact.id, channel,
                kind=contact.next_action, context=contact.context, due_at=contact.next_action_due,
            ), instant, settings, policy) for channel in contact.channels]
            choices.sort(key=route_key)
            best = choices[0]
            available = tuple(item.channel for item in choices if item.decision == "SEND_NOW")
            result.append(replace(best, available_channels=available))
    return sorted(result, key=route_key)


def route_key(item: RoutedAction):
    order = {"SEND_NOW": 0, "WAIT": 1, "REVIEW": 2, "BLOCKED": 3, "SKIP": 4}
    return (order[item.decision], -item.score, not item.overdue,
            item.next_window_at or "9999", item.person.casefold(), item.contact_id, item.action_id)
