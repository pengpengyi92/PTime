from dataclasses import replace
from datetime import datetime

import pytest

from ptime.core.channels import ChannelRule, ContextRule, load_channels
from ptime.core.config import load_settings
from ptime.core.contact_router import route
from ptime.core.timezone import parse_instant
from ptime.models import CHANNELS, Contact, PendingAction

C = Contact("Fictional Contact", "London", "Europe/London", id="demo",
            channels=("email",), priority="P0", synthetic=True)
A = PendingAction("draft", "demo", "email")
NOW = parse_instant("2026-09-21T15:00+01:00")


def one(contact=C, action=A, at=NOW, **kwargs):
    return route([contact], [action], at, **kwargs)[0]


@pytest.mark.parametrize("channel", sorted(CHANNELS))
def test_channels_support_professional_window(channel):
    result = one(replace(C, channels=(channel,)), replace(A, channel=channel))
    assert result.decision == "SEND_NOW"
    assert result.requires_human_approval and not result.calendar_verified


@pytest.mark.parametrize("clock,channel,expected", [
    ("07:59", "linkedin", "WAIT"), ("08:00", "linkedin", "SEND_NOW"),
    ("08:59", "email", "WAIT"), ("09:00", "email", "SEND_NOW"),
    ("17:59", "email", "SEND_NOW"), ("18:00", "email", "WAIT"),
    ("19:59", "linkedin", "SEND_NOW"), ("20:00", "linkedin", "WAIT"),
    ("12:00", "phone", "WAIT"), ("13:59", "phone", "WAIT"),
    ("14:00", "phone", "SEND_NOW"),
])
def test_half_open_channel_and_meeting_boundaries(clock, channel, expected):
    result = one(replace(C, channels=(channel,)), replace(A, channel=channel),
                 parse_instant(f"2026-09-21T{clock}+01:00"))
    assert result.decision == expected


def test_context_distinguishes_professional_and_personal_chat():
    c = replace(C, relationship="friend", channels=("wechat",))
    at = parse_instant("2026-09-21T20:30+01:00")
    assert one(c, replace(A, channel="wechat"), at).decision == "WAIT"
    assert one(c, replace(A, channel="wechat", context="personal"), at).decision == "SEND_NOW"


@pytest.mark.parametrize("context,expected", [
    ("professional", "WAIT"), ("semi_professional", "WAIT"),
    ("informal", "SEND_NOW"), ("personal", "SEND_NOW"),
])
def test_four_contexts_at_evening_boundary(context, expected):
    c = replace(C, relationship="friend", channels=("wechat",))
    a = replace(A, channel="wechat", context=context)
    assert one(c, a, parse_instant("2026-09-21T20:30+01:00")).decision == expected


def test_next_morning_has_date_timezone_and_utc():
    c = replace(C, location="Shenzhen", timezone="Asia/Shanghai")
    result = one(c, at=parse_instant("2026-09-21T22:15"))
    assert result.decision == "WAIT"
    assert result.next_window_local == "2026-09-22T09:00:00+08:00"
    assert result.next_window_at == "2026-09-22T01:00:00+00:00"


def test_weekend_waits_until_monday():
    result = one(at=parse_instant("2026-09-25T18:00+01:00"))
    assert result.next_window_local == "2026-09-28T09:00:00+01:00"


def test_personal_preference_intersects_channel_policy():
    c = replace(C, preferred_contact_windows=("10:17-11:00",))
    result = one(c, at=parse_instant("2026-09-21T09:30+01:00"))
    assert result.next_window_local == "2026-09-21T10:17:00+01:00"


def test_empty_intersection_has_no_invented_next_window():
    result = one(replace(C, preferred_contact_windows=("22:00-22:30",)))
    assert result.decision == "WAIT" and result.next_window_at is None
    assert any("No suitable" in reason for reason in result.reasons)


@pytest.mark.parametrize("clock", ["00:30", "06:30", "23:30"])
def test_priority_expected_reply_and_preference_cannot_override_quiet(clock):
    c = replace(C, relationship="friend", preferred_contact_windows=("00:00-24:00",))
    result = one(c, replace(A, kind="reply", expected_reply=True),
                 parse_instant(f"2026-09-21T{clock}+01:00"))
    assert result.decision == "WAIT"


def test_expected_reply_explicit_late_exception():
    at = parse_instant("2026-09-21T22:30+01:00")
    assert one(at=at).decision == "WAIT"
    result = one(action=replace(A, kind="reply", expected_reply=True), at=at)
    assert result.decision == "SEND_NOW"
    assert "expected-reply" in " ".join(result.reasons)


def test_reply_without_context_needs_review():
    assert one(action=replace(A, kind="reply")).decision == "REVIEW"


def test_late_friend_requires_explicit_preference():
    c = replace(C, relationship="friend", channels=("whatsapp",))
    a = replace(A, channel="whatsapp", context="informal", kind="informal_chat")
    at = parse_instant("2026-09-21T22:30+01:00")
    assert one(c, a, at).decision == "WAIT"
    assert one(replace(c, preferred_contact_windows=("21:30-23:00",)), a, at).decision == "SEND_NOW"


@pytest.mark.parametrize("kind", ["interview", "coffee_chat"])
def test_late_friend_preference_does_not_override_meeting_action(kind):
    c = replace(C, relationship="friend", preferred_contact_windows=("21:00-23:00",))
    a = replace(A, context="personal", kind=kind)
    assert one(c, a, parse_instant("2026-09-21T22:30+01:00")).decision == "WAIT"


def test_queue_kind_controls_followup_explanation():
    c = replace(C, last_contact_at="2026-09-01T10:00Z")
    result = one(c, replace(A, kind="research_discussion"))
    assert not any("Follow-up due" in reason for reason in result.reasons)


@pytest.mark.parametrize("confirmed", [False, True])
def test_meeting_requires_explicit_confirmation(confirmed):
    c = replace(C, channels=("video_call",))
    a = replace(A, channel="video_call", kind="interview", confirmed=confirmed,
                scheduled_at="2026-09-21T22:30+01:00", scheduled_until="2026-09-21T23:15+01:00")
    at = parse_instant("2026-09-21T23:00+01:00")
    result = one(c, a, at)
    assert result.decision == ("SEND_NOW" if confirmed else "REVIEW")
    assert not result.calendar_verified


def test_confirmed_meeting_not_shifted_or_repeated():
    c = replace(C, channels=("phone",))
    a = replace(A, channel="phone", kind="interview", confirmed=True,
                scheduled_at="2026-09-21T22:37+01:00", scheduled_until="2026-09-21T23:07+01:00")
    result = one(c, a)
    assert result.next_window_local == "2026-09-21T22:37:00+01:00"
    assert one(c, a, parse_instant("2026-09-21T23:07+01:00")).decision == "SKIP"
    assert one(replace(c, do_not_contact=True), a).decision == "BLOCKED"


@pytest.mark.parametrize("status", ["sent", "completed", "canceled"])
def test_terminal_queue_actions_do_not_generate_fallback_outreach(status):
    results = route([C], [replace(A, status=status)], NOW)
    assert len(results) == 1 and results[0].decision == "SKIP"


def test_same_day_followup_waits_but_expected_reply_can_respond():
    c = replace(C, last_contact_at="2026-09-21T10:30+01:00")
    assert one(c).next_window_local == "2026-09-22T09:00:00+01:00"
    assert one(c, replace(A, kind="reply", expected_reply=True)).decision == "SEND_NOW"


def test_future_last_contact_timestamp_rejected_same_day():
    with pytest.raises(ValueError, match="evaluation instant"):
        one(replace(C, last_contact_at="2026-09-21T16:00+01:00"))


def test_not_before_is_not_due_at():
    a = replace(A, not_before="2026-09-21T16:17+01:00", due_at="2026-09-21T16:30+01:00")
    result = one(action=a)
    assert result.next_window_local == "2026-09-21T16:17:00+01:00"
    assert not result.overdue
    assert one(action=replace(A, due_at="2026-09-21T14:00+01:00")).overdue


def test_missing_or_unapproved_channel_needs_review():
    assert route([replace(C, channels=())], [], NOW)[0].decision == "REVIEW"
    result = one(action=replace(A, channel="linkedin"))
    assert result.decision == "REVIEW" and result.next_window_at is None
    blocked = route([replace(C, channels=(), do_not_contact=True)], [], NOW)[0]
    assert blocked.decision == "BLOCKED"


def test_email_routes_only_real_email_queue_records():
    assert route([C], [], NOW, email_only=True) == []
    c = replace(C, channels=("email", "linkedin"))
    actions = [A, replace(A, id="linked", channel="linkedin")]
    result = route([c], actions, NOW, email_only=True)
    assert len(result) == 1 and result[0].channel == "email"


def test_best_channel_and_alternatives_no_duplicate_person_suggestions():
    result = route([replace(C, channels=("linkedin", "email"))], [], NOW)
    assert len(result) == 1
    assert result[0].channel == "email"
    assert result[0].available_channels == ("email", "linkedin")


def test_ranking_deterministic_and_explained():
    c2 = replace(C, id="demo-2", name="Fictional Other", priority="P3")
    left = route([c2, C], [], NOW)
    assert left == route([C, c2], [], NOW)
    assert left[0].contact_id == C.id
    assert left[0].components and left[0].reasons


def test_empty_still_requires_aware_instant():
    with pytest.raises(ValueError):
        route([], [], datetime(2026, 9, 21))


@pytest.mark.parametrize("zone,friday,expected", [
    ("Europe/London", "2026-03-27T18:00Z", "2026-03-30T09:00:00+01:00"),
    ("Europe/London", "2026-10-23T18:00+01:00", "2026-10-26T09:00:00+00:00"),
    ("America/New_York", "2026-03-06T18:00-05:00", "2026-03-09T09:00:00-04:00"),
    ("America/New_York", "2026-10-30T18:00-04:00", "2026-11-02T09:00:00-05:00"),
])
def test_next_window_recomputes_dst(zone, friday, expected):
    result = one(replace(C, timezone=zone), at=parse_instant(friday))
    assert result.next_window_local == expected


def transition_policy(start, end):
    p = load_channels()
    return replace(p, quiet=((0, 1),), channels={**p.channels, "email": ChannelRule(((start, end),), 1, False)},
                   contexts={**p.contexts, "personal": ContextRule(((start, end),), False)})


def test_dst_gap_search_enters_window_at_actual_transition():
    c = replace(C, relationship="friend")
    a = replace(A, kind="informal_chat", context="personal")
    result = one(c, a, parse_instant("2026-03-29T00:45Z"), policy=transition_policy(90, 180))
    # London 01:30 does not exist. 02:00 is the first valid instant within 01:30-03:00.
    assert result.next_window_local == "2026-03-29T02:00:00+01:00"
    assert result.next_window_at == "2026-03-29T01:00:00+00:00"


def test_dst_fold_search_preserves_second_occurrence():
    c = replace(C, relationship="friend")
    a = replace(A, kind="informal_chat", context="personal")
    result = one(c, a, parse_instant("2026-10-25T01:50+01:00"), policy=transition_policy(90, 100))
    assert result.next_window_local == "2026-10-25T01:30:00+00:00"
