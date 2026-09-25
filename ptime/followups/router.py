"""Only explicit replies or user actions may open a deeper follow-up window."""

from dataclasses import replace
from datetime import timedelta

from ptime.core.channels import load_channels
from ptime.core.config import load_settings
from ptime.core.timezone import require_aware
from ptime.festivals.rules import rested_window, validate_times, with_history
from ptime.followups.models import FollowupRequest, FollowupRecommendation
from ptime.models import PendingAction


def route_followups(snapshot, instant, settings=None, policy=None, base_timezone=None):
    require_aware(instant)
    settings, policy = settings or load_settings(), policy or load_channels()
    base_timezone = base_timezone or settings.base_timezone
    validate_times(snapshot.contacts, snapshot.history, instant)
    contacts = {c.id: with_history(c, snapshot.history) for c in snapshot.contacts}
    requests = list(snapshot.followups)
    claimed = {(r.contact_id, r.cycle) for r in requests}
    for record in sorted(snapshot.history, key=lambda r: (r.contact_id, r.cycle, r.greeted_at), reverse=True):
        if (record.contact_id, record.cycle) not in claimed:
            requests.append(FollowupRequest(f"after:{record.contact_id}:{record.cycle}", record.contact_id,
                                             record.channel, cycle=record.cycle))
            claimed.add((record.contact_id, record.cycle))
    result = []
    for request in requests:
        for timestamp in (request.user_requested_at, request.last_followup_at):
            if timestamp and timestamp > instant:
                raise ValueError("Follow-up evidence cannot be in the future")
        contact = contacts[request.contact_id]
        records = [r for r in snapshot.history if r.contact_id == contact.id and (request.cycle is None or r.cycle == request.cycle)]
        replies = [r.replied_at for r in records if r.replied_at]
        reply = max(replies) if replies else None
        item = FollowupRecommendation(request.id, contact.id, "SKIP", (), request.channel,
                                       due_at=request.due_at, overdue=bool(request.due_at and instant > request.due_at),
                                       opportunity_urgency=request.opportunity_urgency,
                                       communication_asset_type=request.communication_asset_type, asset_ref=request.asset_ref)
        if contact.do_not_contact:
            result.append(replace(item, state="BLOCKED", reason=("Do-not-contact",)))
            continue
        terminal_action = any(a.contact_id == contact.id and a.kind in {"follow_up", "application_follow_up"}
                              and a.status not in {"draft", "pending"} for a in snapshot.pending_actions)
        if request.status != "pending" or terminal_action or any(r.closed or r.reply_state == "declined" for r in records):
            result.append(replace(item, state="CLOSED", reason=("Explicit terminal follow-up or interaction state",)))
            continue
        if request.channel not in contact.channels:
            result.append(replace(item, state="BLOCKED", reason=("Channel restriction",)))
            continue
        if reply is None and request.user_requested_at is None:
            result.append(replace(item, reason=("No explicit reply or separate user action; no automatic no-reply chasing",)))
            continue
        if reply and instant - reply > timedelta(days=30) and request.user_requested_at is None:
            result.append(replace(item, reason=("Reply is over 30 days old; refresh context via an explicit user action",)))
            continue
        earliest = request.not_before or (reply or request.user_requested_at)
        if reply:
            earliest = max(earliest, reply + timedelta(hours=request.reply_delay_hours))
        if request.user_requested_at:
            earliest = max(earliest, request.user_requested_at)
        # Prior attempts are contact-wide, not reset by changing request IDs or channels.
        attempts = [r.last_followup_at for r in requests if r.contact_id == contact.id and r.last_followup_at]
        if attempts:
            earliest = max(earliest, max(attempts) + timedelta(hours=request.cooldown_hours))
        no_reply = [r.greeted_at for r in records if r.reply_state == "no_reply"]
        if no_reply and (reply is None or max(no_reply) > reply):
            earliest = max(earliest, max(no_reply) + timedelta(hours=request.cooldown_hours))
        action = PendingAction(request.id, contact.id, request.channel, kind="follow_up", context=contact.context,
                               not_before=earliest, due_at=request.due_at)
        when = rested_window(contact, action, instant, settings, policy, base_timezone)
        state = "FOLLOW_UP_ELIGIBLE" if when and when <= instant else "WAIT"
        reason = "Reply/user action opens advisory follow-up; delays, contact frequency, V2 windows and sender rest still apply"
        if when is None:
            reason += "; no joint window inside search horizon"
        result.append(replace(item, state=state, followup_eligible_at=when, reason=(reason,)))
    order = {"FOLLOW_UP_ELIGIBLE": 0, "WAIT": 1, "SKIP": 2, "CLOSED": 3, "BLOCKED": 4}
    return sorted(result, key=lambda r: (order[r.state], not r.overdue, -r.opportunity_urgency, r.contact_id, r.id))
