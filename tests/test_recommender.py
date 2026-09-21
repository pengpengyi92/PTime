from dataclasses import replace
from datetime import date, datetime

import pytest

from ptime.core.config import load_settings
from ptime.core.recommender import recommend
from ptime.core.timezone import parse_instant
from ptime.models import Contact, Opportunity

BASE = Contact("Fictional Person", "London", "Europe/London", relationship="recruiter", priority="P1", synthetic=True)
MONDAY = parse_instant("2026-09-21T22:15")


def test_empty_database():
    assert recommend([], MONDAY) == []


def test_empty_database_still_requires_aware_time():
    with pytest.raises(ValueError):
        recommend([], datetime(2026, 9, 21))


def test_ranking_explained_and_weighted():
    high = replace(BASE, name="High priority", priority="P0", last_contact=date(2026, 9, 1),
                   opportunities=(Opportunity("demo", "Fictional role"),))
    low = replace(BASE, name="Low priority", priority="P3", last_contact=date(2026, 9, 20))
    results = recommend([low, high], MONDAY)
    assert results[0].person == "High priority"
    settings = load_settings()
    assert results[0].final_score == pytest.approx(sum(results[0].components[k] * v for k, v in settings.weights.items()))
    assert any("Follow-up due" in reason for reason in results[0].reason)
    assert any("Fictional role" in reason for reason in results[0].reason)
    assert results[0].availability_score == pytest.approx(0.95 * 0.9)
    assert results[0].recommended_action.requires_human_approval
    assert not results[0].calendar_verified


@pytest.mark.parametrize("clock", ["00:00", "06:30", "07:30", "21:30", "23:30"])
def test_p0_does_not_override_quiet_or_early_hours(clock):
    contact = replace(BASE, timezone="Asia/Shanghai", location="China", priority="P0",
                      opportunities=(Opportunity("role", "Fictional priority role"),))
    result = recommend([contact], parse_instant(f"2026-09-21T{clock}"))[0]
    assert not result.eligible_now
    assert result.final_score == 0
    assert result.availability_score == 0
    assert result.recommended_action.status == "defer"


def test_do_not_contact_overrides_everything():
    result = recommend([replace(BASE, do_not_contact=True, priority="P0")], MONDAY)[0]
    assert not result.eligible_now
    assert "Do-not-contact" in result.recommended_action.recommendation


def test_professional_weekend_and_informal_friend():
    weekend = parse_instant("2026-09-20T22:15")
    friend = replace(BASE, name="Friend", relationship="friend", next_action="informal_chat")
    results = recommend([BASE, friend], weekend)
    assert results[0].person == "Friend"
    assert results[0].eligible_now
    assert not results[1].eligible_now


def test_weekend_evening_professional_is_deferred():
    result = recommend([BASE], parse_instant("2026-09-20T19:30+01:00"))[0]
    assert not result.eligible_now


def test_weekend_does_not_override_early_hours_for_friends():
    friend = replace(BASE, relationship="friend", next_action="informal_chat", priority="P0")
    result = recommend([friend], parse_instant("2026-09-20T07:30+01:00"))[0]
    assert not result.eligible_now
    assert result.final_score == 0


@pytest.mark.parametrize("kind", ["interview", "coffee_chat"])
def test_lunch_not_a_synchronous_meeting(kind):
    result = recommend([replace(BASE, next_action=kind)], parse_instant("2026-09-21T12:30+01:00"))[0]
    assert not result.eligible_now


def test_lunch_follow_up_is_async_only():
    result = recommend([BASE], parse_instant("2026-09-21T12:30+01:00"))[0]
    assert result.eligible_now
    assert "asynchronous" in result.recommended_action.recommendation


def test_same_day_follow_up_suppressed_in_contact_timezone():
    result = recommend([replace(BASE, last_contact=date(2026, 9, 21))], MONDAY)[0]
    assert not result.eligible_now
    assert "Already contacted" in result.recommended_action.recommendation


def test_future_last_contact_rejected():
    with pytest.raises(ValueError, match="after the evaluation"):
        recommend([replace(BASE, last_contact=date(2026, 9, 22))], MONDAY)


def test_unknown_recency_and_closed_or_expired_opportunity():
    contact = replace(BASE, opportunities=(
        Opportunity("closed", "Fictional closed", "closed"),
        Opportunity("expired", "Fictional elapsed deadline", deadline=date(2026, 9, 20)),
    ))
    result = recommend([contact], MONDAY)[0]
    assert result.components["recency_score"] == 0.5
    assert result.components["opportunity_score"] == 0


def test_score_ties_are_deterministic():
    alice, zed = replace(BASE, name="Alice"), replace(BASE, name="Zed")
    assert recommend([zed, alice], MONDAY) == recommend([alice, zed], MONDAY)
    assert recommend([zed, alice], MONDAY)[0].person == "Alice"


def test_duplicate_exports_fail_visibly():
    with pytest.raises(ValueError, match="Duplicate"):
        recommend([BASE, BASE], MONDAY)


def test_weights_are_configurable():
    settings = load_settings()
    weights = {key: float(key == "contact_priority") for key in settings.weights}
    result = recommend([BASE], MONDAY, replace(settings, weights=weights))[0]
    assert result.final_score == settings.priorities["P1"]
