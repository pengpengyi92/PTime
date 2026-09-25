from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import json
import shutil

import pytest
import yaml

from ptime.__main__ import main
from ptime.core.config import default_resource, load_settings
from ptime.core.timezone import parse_instant
from ptime.festivals.calendar import festival_date, load_calendars, occurrence, upcoming
from ptime.festivals.models import Festival, GreetingPreference, GreetingRecord, HolidayPeriod
from ptime.festivals.router import route_touchpoints
from ptime.festivals.snapshot import RelationshipSnapshot, parse_relationship_snapshot
from ptime.followups.models import FollowupRequest
from ptime.followups.router import route_followups
from ptime.greetings.models import GreetingTemplate
from ptime.greetings.renderer import render
from ptime.greetings.templates import load_templates, select_templates
from ptime.models import Contact, PendingAction

AT = parse_instant("2026-09-25T10:00+08:00")


@pytest.fixture(scope="module")
def catalog():
    return load_calendars()


@pytest.fixture(scope="module")
def templates():
    return load_templates()


def contact(**kw):
    values = dict(name="Fictional Person", location="Shenzhen", timezone="Asia/Shanghai",
                  id="fictional", channels=("email", "wechat"), synthetic=True)
    return Contact(**(values | kw))


def snapshot(c=None, pref=None, history=(), followups=(), pending=()):
    c = c or contact()
    pref = pref or GreetingPreference(c.id, festival_ids=("mid_autumn",), style="professional", locale="en")
    return RelationshipSnapshot((c,), tuple(pending), (pref,), tuple(history), tuple(followups))


def record(**kw):
    values = dict(contact_id="fictional", festival_id="mid_autumn", cycle="mid_autumn:2026",
                  template_id="mid_autumn.professional.en", channel="email",
                  greeted_at=AT - timedelta(days=2))
    return GreetingRecord(**(values | kw))


def route(s, catalog, templates, at=AT, **kw):
    return route_touchpoints(s, catalog, templates, at, festival_id="mid_autumn", **kw)[0][0]


@pytest.mark.parametrize("id,year,expected", [
    ("mid_autumn", 2026, "2026-09-25"), ("mid_autumn", 2027, "2027-09-15"),
    ("spring_festival", 2026, "2026-02-17"), ("spring_festival", 2027, "2027-02-06"),
    ("lantern", 2026, "2026-03-03"), ("lantern", 2027, "2027-02-20"),
    ("dragon_boat", 2026, "2026-06-19"), ("dragon_boat", 2027, "2027-06-09"),
    ("christmas", 2031, "2031-12-25"), ("new_year", 2027, "2027-01-01"),
    ("thanksgiving", 2026, "2026-11-26"), ("thanksgiving", 2027, "2027-11-25"),
    ("independence_day", 2026, "2026-07-04"), ("memorial_day", 2026, "2026-05-25"),
    ("labor_day", 2026, "2026-09-07"), ("easter", 2026, "2026-04-05"),
    ("easter", 2027, "2027-03-28"), ("early_may_bank_holiday", 2026, "2026-05-04"),
    ("spring_bank_holiday", 2027, "2027-05-31"), ("summer_bank_holiday", 2027, "2027-08-30"),
])
def test_calendar_dates(catalog, id, year, expected):
    assert festival_date(catalog.festivals[id], year) == date.fromisoformat(expected)


def test_four_views_and_no_duplicate_global_ids(catalog):
    for view in ("china", "global", "united_states", "united_kingdom"):
        assert "new_year" in catalog.views[view]
    assert len(catalog.festivals) == 15
    assert catalog.festivals["summer_bank_holiday"].country_or_region == "GB-ENG-WLS"
    values, _ = upcoming(catalog, parse_instant("2026-12-31T12:00+08:00"), 2, "china")
    new_year = next(i for i in values if i.festival_id == "new_year")
    assert new_year.timezone == "Asia/Shanghai"


def test_unknown_lunar_year_is_visible(catalog):
    assert festival_date(catalog.festivals["mid_autumn"], 2028) is None
    events, warnings = upcoming(catalog, parse_instant("2028-09-01T10:00Z"), festival_id="mid_autumn")
    assert not events and "UNKNOWN" in warnings[0]


def test_official_period_is_not_cultural_day(catalog):
    event = occurrence(catalog.festivals["spring_festival"], 2026)
    assert event.cultural_date == date(2026, 2, 17)
    assert event.official_holiday_period[0].start == date(2026, 2, 15)
    assert event.official_holiday_period[0].end == date(2026, 2, 23)
    assert occurrence(catalog.festivals["spring_festival"], 2027).official_holiday_period == ()
    event = occurrence(catalog.festivals["independence_day"], 2026)
    assert event.cultural_date == date(2026, 7, 4)
    assert event.official_holiday_period[0].start == date(2026, 7, 3)


def test_recipient_timezone_boundaries_and_year_rollover(catalog):
    festival = replace(catalog.festivals["mid_autumn"], lead_days=0, valid_window_days=1)
    china = occurrence(festival, 2026, "Asia/Shanghai")
    us = occurrence(festival, 2026, "America/New_York")
    assert us.not_before - china.not_before == timedelta(hours=12)
    start = parse_instant("2026-12-31T12:00Z")
    events, _ = upcoming(catalog, start, 2, "global")
    assert any(e.cycle == "new_year:2027" for e in events)
    assert all(e.expires_at > start for e in events)


def test_dst_window_uses_real_local_midnights(catalog):
    f = replace(catalog.festivals["new_year"], cultural_date_rule={"type": "fixed", "month": 3, "day": 8}, lead_days=0, valid_window_days=1)
    event = occurrence(f, 2026, "America/New_York")
    assert event.expires_at - event.not_before == timedelta(hours=23)


def test_non_greeting_holidays_not_promoted(catalog, templates):
    at = parse_instant("2026-05-20T12:00Z")
    events, _ = upcoming(catalog, at, region="united_states")
    assert "memorial_day" not in {e.festival_id for e in events}
    events, _ = upcoming(catalog, at, region="united_states", include_non_greeting=True)
    assert "memorial_day" in {e.festival_id for e in events}


@pytest.mark.parametrize("style", ["general", "professional", "reconnect"])
@pytest.mark.parametrize("locale", ["en", "zh-CN"])
def test_bilingual_styles(templates, style, locale):
    selected = select_templates(templates, "mid_autumn", style, locale)
    assert len(selected) == 1
    assert render(selected[0]) == selected[0].message
    assert "referral" not in render(selected[0]).lower()


def test_all_greeting_enabled_festivals_have_six_templates(catalog, templates):
    assert len(templates) == 54
    for f in catalog.festivals.values():
        if f.greeting_appropriate:
            assert len([t for t in templates if t.festival_id == f.id]) == 6


def test_safe_renderer_and_slot_validation():
    template = GreetingTemplate("test", "new_year", "general", "en", "general", "email", "Hello {name}", ("name",))
    assert render(template, {"name": "Fictional A"}) == "Hello Fictional A"
    for values in ({}, {"name": "A\nB"}, {"name": "A", "extra": "B"}):
        with pytest.raises(ValueError):
            render(template, values)
    for msg in ("{name.__class__}", "{name!r}", "{name:>50}"):
        with pytest.raises(ValueError):
            replace(template, message=msg)


def test_opt_in_suggestion(catalog, templates):
    item = route(snapshot(), catalog, templates)
    assert item.state == "SUGGEST" and item.user_approval_required
    assert not item.calendar_verified and item.score_components


@pytest.mark.parametrize("location,zone", [("Shenzhen", "Asia/Shanghai"), ("Boston", "America/New_York"), ("London", "Europe/London")])
def test_location_never_infers_festival(catalog, templates, location, zone):
    item = route(snapshot(contact(location=location, timezone=zone), GreetingPreference("fictional")), catalog, templates)
    assert item.state == "SKIP" and "location is not consent" in item.reason[0]


@pytest.mark.parametrize("channel", ["email", "wechat", "linkedin"])
def test_duplicate_cycle_across_channels(catalog, templates, channel):
    item = route(snapshot(contact(channels=(channel,)), history=(record(),)), catalog, templates)
    assert item.state == "GREETED" and item.duplicate_suppressed


def test_reset_only_duplicate_not_dnc(catalog, templates):
    pref = GreetingPreference("fictional", festival_ids=("mid_autumn",), reset_cycles=("mid_autumn:2026",), allow_recent_contact=True)
    assert route(snapshot(pref=pref, history=(record(),)), catalog, templates).state == "SUGGEST"
    assert route(snapshot(contact(do_not_contact=True, priority="P0"), pref, history=(record(),)), catalog, templates).state == "BLOCKED"


def test_same_template_used_in_another_cycle(catalog, templates):
    r = record(cycle="mid_autumn:2025")
    item = route(snapshot(history=(r,)), catalog, templates)
    assert item.state == "SKIP"


def test_recent_contact_and_date_only_evidence(catalog, templates):
    c = contact(last_contact_at=AT - timedelta(hours=1))
    item = route(snapshot(c), catalog, templates)
    assert item.recent_contact_suppressed and item.state != "SUGGEST"
    c = contact(last_contact=date(2026, 9, 24))
    item = route(snapshot(c), catalog, templates)
    assert item.recent_contact_suppressed


def test_active_conversation_and_explicit_override(catalog, templates):
    pref = GreetingPreference("fictional", festival_ids=("mid_autumn",), active_conversation=True)
    assert route(snapshot(pref=pref), catalog, templates).state == "SKIP"
    assert route(snapshot(pref=replace(pref, allow_active_conversation=True)), catalog, templates).state == "SUGGEST"


def test_excluded_preference_wins(catalog, templates):
    pref = GreetingPreference("fictional", festival_ids=("mid_autumn",), excluded_festival_ids=("mid_autumn",))
    assert route(snapshot(pref=pref), catalog, templates).state == "SKIP"


@pytest.mark.parametrize("channels", [(), ("phone",), ("telegram",)])
def test_channel_restriction(catalog, templates, channels):
    assert route(snapshot(contact(channels=channels)), catalog, templates).state == "BLOCKED"


@pytest.mark.parametrize("status", ["sent", "completed", "canceled"])
def test_terminal_v2_action_blocks_greeting(catalog, templates, status):
    action = PendingAction("done", "fictional", "email", kind="relationship_maintenance", status=status)
    assert route(snapshot(pending=(action,)), catalog, templates).state == "CLOSED"


def test_preferred_window_and_priority(catalog, templates):
    c = contact(priority="P0", preferred_contact_windows=("14:00-16:00",))
    item = route(snapshot(c), catalog, templates)
    assert item.state == "WAIT"
    assert item.not_before == parse_instant("2026-09-25T14:00+08:00")


def test_sender_rest_even_when_recipient_is_active(catalog, templates):
    at = parse_instant("2026-09-24T23:30+08:00")
    c = contact(location="London", timezone="Europe/London", priority="P0")
    item = route(snapshot(c), catalog, templates, at)
    assert item.state == "WAIT" and item.not_before > at
    assert item.not_before == parse_instant("2026-09-25T08:00+01:00") or item.not_before == parse_instant("2026-09-25T09:00+01:00")


def test_upcoming_outside_search_horizon_waits(catalog, templates):
    item = route(snapshot(), catalog, templates, parse_instant("2026-09-01T10:00+08:00"), days=30)
    assert item.state == "WAIT" and item.not_before == parse_instant("2026-09-23T09:00+08:00")


def test_expiry_and_disabled(catalog, templates):
    events, _ = upcoming(catalog, parse_instant("2026-09-27T00:00+08:00"), festival_id="mid_autumn", zone="Asia/Shanghai")
    assert not events
    disabled = replace(catalog, festivals={**catalog.festivals, "mid_autumn": replace(catalog.festivals["mid_autumn"], enabled=False)})
    events, _ = upcoming(disabled, AT, festival_id="mid_autumn")
    assert not events


def test_reply_eligibility_no_immediate_ask():
    r = record(reply_state="replied", replied_at=AT - timedelta(hours=1))
    item = route_followups(snapshot(history=(r,)), AT)[0]
    assert item.state == "WAIT" and item.followup_eligible_at > AT
    r = replace(r, replied_at=AT - timedelta(hours=30))
    assert route_followups(snapshot(history=(r,)), AT)[0].state == "FOLLOW_UP_ELIGIBLE"


def test_no_reply_never_auto_chases_and_manual_cooldown():
    s = snapshot(history=(record(),))
    assert route_followups(s, AT)[0].state == "SKIP"
    request = FollowupRequest("manual", "fictional", "email", cycle="mid_autumn:2026", user_requested_at=AT,
                              due_at=AT - timedelta(hours=1), opportunity_urgency=3)
    item = route_followups(replace(s, followups=(request,)), AT)[0]
    assert item.state == "WAIT" and item.overdue
    assert item.followup_eligible_at >= record().greeted_at + timedelta(days=7)


def test_followup_frequency_is_cross_channel():
    r = record(reply_state="replied", replied_at=AT - timedelta(hours=30))
    done = FollowupRequest("earlier", "fictional", "wechat", cycle="mid_autumn:2026", status="completed", last_followup_at=AT - timedelta(days=1))
    request = FollowupRequest("next", "fictional", "email", cycle="mid_autumn:2026")
    items = route_followups(snapshot(history=(r,), followups=(done, request)), AT)
    item = next(i for i in items if i.id == "next")
    assert item.state == "WAIT" and item.followup_eligible_at >= AT + timedelta(days=6)


@pytest.mark.parametrize("flag", ["closed", "declined", "dnc", "channel"])
def test_followup_hard_blocks(flag):
    r = record(reply_state="replied", replied_at=AT - timedelta(hours=30))
    c = contact()
    if flag == "closed":
        r = replace(r, closed=True)
    elif flag == "declined":
        r = replace(r, reply_state="declined", replied_at=None)
    elif flag == "dnc":
        c = replace(c, do_not_contact=True)
    else:
        c = replace(c, channels=("phone",))
    assert route_followups(snapshot(c, history=(r,)), AT)[0].state in {"CLOSED", "BLOCKED"}


def test_asset_reference_without_loading_pcv():
    request = FollowupRequest("intro", "fictional", "email", user_requested_at=AT,
                              communication_asset_type="self_introduction", asset_ref="pcv:self_intro.en")
    item = route_followups(snapshot(followups=(request,)), AT)[0]
    assert item.state == "FOLLOW_UP_ELIGIBLE" and item.asset_ref == "pcv:self_intro.en"


def test_future_evidence_rejected(catalog, templates):
    for s in (snapshot(contact(last_contact_at=AT + timedelta(hours=1))), snapshot(history=(record(greeted_at=AT + timedelta(hours=1)),))):
        with pytest.raises(ValueError):
            route(s, catalog, templates)
    with pytest.raises(ValueError):
        route_followups(snapshot(followups=(FollowupRequest("f", "fictional", "email", user_requested_at=AT + timedelta(hours=1)),)), AT)


def test_demo_and_snapshot_validation(catalog, templates):
    doc = yaml.safe_load(default_resource("touchpoints.example.yaml", "ptime_examples").read_text(encoding="utf-8"))
    s = parse_relationship_snapshot(doc, catalog, templates)
    assert len(s.contacts) == 5 and all(c.synthetic and c.name.startswith("Fictional") for c in s.contacts)
    for bad in (dict(doc, unknown=[]), dict(doc, history=[dict(doc["history"][0], contact_id="missing")]),
                dict(doc, preferences=[dict(doc["preferences"][0], festival_ids=["unknown"])])):
        with pytest.raises(ValueError):
            parse_relationship_snapshot(bad, catalog, templates)


@pytest.mark.parametrize("command,args", [
    ("festivals", ["--region", "china"]),
    ("greetings", ["--festival", "mid_autumn", "--locale", "zh-CN"]),
    ("touchpoints", ["--demo", "--festival", "mid_autumn"]), ("followups", ["--demo"]),
])
def test_cli_deterministic(capsys, command, args):
    argv = [command, *args, "--at", "2026-09-25T10:00+08:00", "--json"]
    assert main(argv) == 0
    first = capsys.readouterr().out
    assert main(argv) == 0 and capsys.readouterr().out == first
    doc = json.loads(first)
    assert doc["user_approval_required"] and doc["items"]
    assert doc["schema_version"] == "2.1"


def test_cli_empty_defaults(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    for command in ("touchpoints", "followups"):
        assert main([command, "--json"]) == 0
        assert json.loads(capsys.readouterr().out)["total"] == 0


@pytest.mark.parametrize("args", [
    ["festivals", "--region", "unknown"], ["festivals", "--days", "-1"],
    ["festivals", "--days", "367"], ["greetings", "--festival", "unknown"],
    ["touchpoints", "--limit", "0"], ["touchpoints", "--input", "absent.yaml"],
])
def test_cli_invalid_arguments_fail_closed(args):
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2


def test_custom_calendar_extensibility(tmp_path):
    source = Path(__file__).parents[1] / "config"
    shutil.copytree(source / "festivals", tmp_path / "festivals")
    example = default_resource("festivals.example.yaml", "ptime_examples").read_text(encoding="utf-8")
    (tmp_path / "festivals" / "custom.yaml").write_text(example, encoding="utf-8")
    custom = load_calendars(tmp_path)
    assert len(custom.select("example_region")) == 2


@pytest.mark.parametrize("kw", [
    {"lead_days": -1}, {"valid_window_days": 0}, {"enabled": "yes"},
    {"suggested_channels": ("phone",)}, {"default_timezone": "CST"},
    {"cultural_date_rule": {"type": "lunar_magic"}},
    {"cultural_date_rule": {"type": "fixed", "month": 2, "day": 31}},
    {"cultural_date_rule": {"type": "dates", "dates": {2026: "2027-01-01"}}},
    {"cultural_date_rule": {"type": "dates", "dates": {2026: None}}},
])
def test_calendar_validation(catalog, kw):
    with pytest.raises(ValueError):
        replace(catalog.festivals["mid_autumn"], **kw)


def test_empty_snapshot_still_validates_filters(catalog, templates):
    empty = RelationshipSnapshot((), (), (), (), ())
    for kw in ({"days": -1}, {"region": "typo"}, {"festival_id": "typo"}):
        with pytest.raises(ValueError):
            route_touchpoints(empty, catalog, templates, AT, **kw)


@pytest.mark.parametrize("status", ["sent", "completed", "canceled"])
def test_existing_v2_followup_terminal_state_is_authoritative(status):
    r = record(reply_state="replied", replied_at=AT - timedelta(hours=30))
    action = PendingAction("old", "fictional", "email", kind="follow_up", status=status)
    assert route_followups(snapshot(history=(r,), pending=(action,)), AT)[0].state == "CLOSED"


def test_followup_stale_reply_requires_new_user_action():
    r = record(greeted_at=AT - timedelta(days=40), reply_state="replied", replied_at=AT - timedelta(days=35))
    assert route_followups(snapshot(history=(r,)), AT)[0].state == "SKIP"


def test_weekend_not_overridden_by_holiday(catalog, templates):
    at = parse_instant("2026-09-26T10:00+08:00")
    item = route(snapshot(), catalog, templates, at)
    assert item.state == "SKIP"  # professional window would resume after festival expiry


@pytest.mark.parametrize("hour", [0, 5, 23])
def test_recipient_quiet_time_no_priority_override(catalog, templates, hour):
    at = parse_instant(f"2026-09-24T{hour:02d}:30+08:00")
    item = route(snapshot(contact(priority="P0")), catalog, templates, at)
    assert item.state == "WAIT" and item.not_before > at


def test_unsupported_template_locale_does_not_fallback(catalog, templates):
    pref = GreetingPreference("fictional", festival_ids=("mid_autumn",), style="general", locale="zh-CN")
    english_only = [t for t in templates if t.locale == "en"]
    item = route(snapshot(pref=pref), catalog, english_only)
    assert item.state == "SKIP" and item.recommended_template_id is None


def test_cli_text_commands(capsys):
    cases = [("festivals", "--region", "united_kingdom", "--days", "120"),
             ("greetings", "--festival", "christmas", "--style", "professional", "--locale", "en"),
             ("touchpoints", "--festival", "mid_autumn", "--demo"), ("followups", "--demo")]
    for args in cases:
        assert main([*args, "--at", "2026-09-25T10:00+08:00"]) == 0
        output = capsys.readouterr().out
        assert "No messages sent" in output and "PTIME" in output


def test_existing_pending_maintenance_is_not_duplicated(catalog, templates):
    action = PendingAction("existing", "fictional", "email", kind="relationship_maintenance", not_before=AT + timedelta(days=1))
    item = route(snapshot(pending=(action,)), catalog, templates)
    assert item.state == "SKIP" and item.recommended_channel is None


def test_professional_context_cannot_use_general_style_to_bypass_policy(catalog, templates):
    f = replace(catalog.festivals["mid_autumn"], professional_greeting_appropriate=False)
    changed = replace(catalog, festivals={**catalog.festivals, f.id: f})
    pref = GreetingPreference("fictional", festival_ids=("mid_autumn",), style="general")
    assert route(snapshot(pref=pref), changed, templates).state == "SKIP"


def test_v21_cli_never_opens_network(monkeypatch, capsys):
    import socket
    def forbidden(*args, **kwargs):
        raise AssertionError("PTime must not open a network connection")
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    for command in ("touchpoints", "followups"):
        assert main([command, "--demo", "--at", "2026-09-25T10:00+08:00", "--json"]) == 0
        assert json.loads(capsys.readouterr().out)["items"]
