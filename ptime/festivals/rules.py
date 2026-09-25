"""V2.1 composes V2.0 recipient gates with an additional sender-rest gate."""

from dataclasses import replace
from datetime import datetime, time, timedelta

from ptime.core.channels import contains
from ptime.core.contact_router import eligible, next_window
from ptime.core.timezone import localize, parse_instant


def rested_window(contact, action, instant, settings, policy, base_timezone, expires_at=None):
    """Return a joint window; never bypass recipient policy or either person's rest."""
    cursor = max(instant, action.not_before or instant)
    horizon = cursor + timedelta(days=policy.search_days)
    if expires_at is not None:
        horizon = min(horizon, expires_at)
    for _ in range(64):
        if cursor >= horizon:
            return None
        if not eligible(contact, action, cursor, settings, policy)[0]:
            cursor = next_window(contact, action, cursor, settings, policy)
            if cursor is None:
                return None
            continue
        local = localize(cursor, base_timezone)
        minute = local.hour * 60 + local.minute
        if not contains(policy.quiet, minute):
            return cursor
        end = next(end for start, end in policy.quiet if start <= minute < end)
        wall = datetime.combine(local.date(), time()) + timedelta(minutes=end)
        try:
            cursor = parse_instant(wall.isoformat(), base_timezone)
        except ValueError:
            # For rare DST boundary gaps/folds, advance by real minutes and re-evaluate.
            cursor += timedelta(minutes=1)
    return None


def validate_times(contacts, history, instant):
    for contact in contacts:
        if contact.last_contact_at and contact.last_contact_at > instant:
            raise ValueError("last_contact_at is after evaluation time")
        if contact.last_contact and contact.last_contact > localize(instant, contact.timezone).date():
            raise ValueError("last_contact date is after evaluation time")
    for item in history:
        if item.greeted_at > instant or (item.replied_at and item.replied_at > instant):
            raise ValueError("Interaction history contains future evidence")


def with_history(contact, history):
    times = [t for r in history if r.contact_id == contact.id for t in (r.greeted_at, r.replied_at) if t]
    if contact.last_contact_at:
        times.append(contact.last_contact_at)
    if not times:
        return contact
    latest = max(times)
    if contact.last_contact and localize(latest, contact.timezone).date() < contact.last_contact:
        return contact
    return replace(contact, last_contact=None, last_contact_at=latest)
