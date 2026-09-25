"""Advisory greeting ranking from explicit opt-ins and interaction evidence."""

from dataclasses import replace
from datetime import datetime, time, timedelta

from ptime.core.channels import load_channels
from ptime.core.config import load_settings
from ptime.core.contact_router import route_one
from ptime.core.timezone import parse_instant, require_aware
from ptime.festivals.calendar import upcoming
from ptime.festivals.models import FestivalTouchpoint, GreetingPreference, bounded_int
from ptime.festivals.rules import rested_window, validate_times, with_history
from ptime.greetings.templates import select_templates
from ptime.models import PendingAction


def route_touchpoints(snapshot, catalog, templates, instant, days=30, region=None, festival_id=None,
                     settings=None, policy=None, base_timezone=None):
    require_aware(instant)
    bounded_int(days, "days", 0, 366)
    catalog.select(region, festival_id)
    settings, policy = settings or load_settings(), policy or load_channels()
    base_timezone = base_timezone or settings.base_timezone
    validate_times(snapshot.contacts, snapshot.history, instant)
    preferences = {p.contact_id: p for p in snapshot.preferences}
    results, warnings = [], []
    for original in snapshot.contacts:
        contact = with_history(original, snapshot.history)
        pref = preferences.get(contact.id, GreetingPreference(contact.id))
        events, gaps = upcoming(catalog, instant, days, region, festival_id, contact.timezone, include_non_greeting=True)
        warnings.extend(gaps)
        for event in events:
            festival = catalog.festivals[event.festival_id]
            item = FestivalTouchpoint(contact.id, festival.id, event.cycle, contact.relationship, "SKIP", (),
                                      event.not_before, event.expires_at, last_contact_at=contact.last_contact_at)
            history = [r for r in snapshot.history if r.contact_id == contact.id and r.cycle == event.cycle]
            terminal = any(a.contact_id == contact.id and a.kind == "relationship_maintenance"
                           and a.status not in {"draft", "pending"} for a in snapshot.pending_actions)
            queued = any(a.contact_id == contact.id and a.kind == "relationship_maintenance"
                         and a.status in {"draft", "pending"} for a in snapshot.pending_actions)
            reason = None
            if contact.do_not_contact:
                item, reason = replace(item, state="BLOCKED"), "Do-not-contact; never overridden by festival or priority"
            elif terminal:
                item, reason = replace(item, state="CLOSED"), "Terminal relationship-maintenance action in explicit V2 queue"
            elif festival.id not in pref.festival_ids or festival.id in pref.excluded_festival_ids:
                reason = "No explicit festival applicability, or explicitly excluded; location is not consent"
            elif not festival.greeting_appropriate or ((pref.style == "professional" or contact.context in {"professional", "semi_professional"}) and not festival.professional_greeting_appropriate) or (pref.style == "reconnect" and not festival.reconnect_appropriate):
                reason = "Calendar event/style is not greeting-appropriate in configuration"
            elif any(r.closed or r.reply_state == "declined" for r in history):
                item, reason = replace(item, state="CLOSED"), "Explicit closed/declined interaction"
            elif history and event.cycle not in pref.reset_cycles:
                replied = any(r.reply_state == "replied" for r in history)
                item = replace(item, state="REPLIED" if replied else "GREETED", duplicate_suppressed=True,
                               reply_state="replied" if replied else "no_reply")
                reason = "One greeting per canonical cycle across all channels; explicit reset required"
            elif queued:
                reason = "Existing V2 maintenance draft/pending action; use that queue, not another greeting"
            elif pref.active_conversation and not pref.allow_active_conversation:
                reason = "Already in an active conversation; no extra festival touchpoint"
            if reason is not None:
                results.append(replace(item, reason=(reason,)))
                continue

            recent = contact.last_contact_at
            if recent is None and contact.last_contact is not None:
                # Date-only evidence conservatively anchors to the END of that local date.
                recent = parse_instant(datetime.combine(contact.last_contact + timedelta(days=1), time()).isoformat(), contact.timezone)
            not_before = event.not_before
            if recent and not pref.allow_recent_contact:
                not_before = max(not_before, recent + timedelta(hours=pref.recent_contact_hours))
                item = replace(item, recent_contact_suppressed=instant < not_before and recent + timedelta(hours=pref.recent_contact_hours) > instant)
            choices = []
            for channel in sorted(set(contact.channels) & set(festival.suggested_channels)):
                candidates = select_templates(templates, festival.id, pref.style, pref.locale, pref.audience, channel)
                for template in candidates:
                    reused = any(r.contact_id == contact.id and r.template_id == template.id
                                 and instant - r.greeted_at < timedelta(days=30) for r in snapshot.history)
                    if reused and event.cycle not in pref.reset_cycles:
                        item = replace(item, duplicate_suppressed=True)
                        continue
                    action = PendingAction(f"festival:{contact.id}:{event.cycle}", contact.id, channel,
                                           kind="relationship_maintenance", context=contact.context, not_before=not_before)
                    routed = route_one(contact, action, instant, settings, policy)
                    when = rested_window(contact, action, instant, settings, policy, base_timezone, event.expires_at)
                    choices.append((when is None, when or event.expires_at, -routed.score, template.id, channel, routed))
            if not choices:
                state = "BLOCKED" if not set(contact.channels) & set(festival.suggested_channels) else "SKIP"
                results.append(replace(item, state=state, not_before=not_before,
                                       reason=("No allowed greeting channel or eligible unused template for style/locale/audience",)))
                continue
            missing, when, _, template_id, channel, routed = min(choices, key=lambda c: c[:5])
            components = {"v2_timing_relationship_priority": routed.score, "explicit_festival_relevance": 1.0}
            if missing:
                state, explanation = "SKIP", "No joint recipient/sender-rest window before expiry within policy search horizon"
            else:
                state = "SUGGEST" if when <= instant else "WAIT"
                explanation = "Explicit opt-in; advisory light greeting, never permission to send"
            results.append(replace(item, state=state, not_before=not_before if missing else when,
                                   recommended_template_id=template_id, recommended_channel=channel,
                                   score=round(0.8 * routed.score + 0.2, 6), score_components=components,
                                   reason=(*routed.reasons, explanation, "Sender quiet hours are also protected")))
    order = {"SUGGEST": 0, "WAIT": 1, "REPLIED": 2, "GREETED": 3, "SKIP": 4, "CLOSED": 5, "BLOCKED": 6}
    return sorted(results, key=lambda r: (order[r.state], -r.score, r.not_before, r.contact_id, r.cycle)), sorted(set(warnings))
