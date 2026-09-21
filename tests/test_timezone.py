from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from ptime.core.timezone import get_zone, localize, parse_instant, require_aware


@pytest.mark.parametrize("zone,stamp,expected", [
    ("Europe/London", "2026-09-21T22:15", "2026-09-21T15:15:00+01:00"),
    ("Europe/London", "2026-12-21T22:15", "2026-12-21T14:15:00+00:00"),
    ("America/New_York", "2026-09-21T22:15", "2026-09-21T10:15:00-04:00"),
    ("America/New_York", "2026-12-21T22:15", "2026-12-21T09:15:00-05:00"),
    ("America/Los_Angeles", "2026-09-21T00:15", "2026-09-20T09:15:00-07:00"),
    ("Asia/Shanghai", "2026-09-21T23:30Z", "2026-09-22T07:30:00+08:00"),
])
def test_conversion_and_date_rollover(zone, stamp, expected):
    assert localize(parse_instant(stamp), zone).isoformat() == expected


@pytest.mark.parametrize("zone,stamp,expected", [
    ("Europe/London", "2026-03-29T00:59Z", "2026-03-29T00:59:00+00:00"),
    ("Europe/London", "2026-03-29T01:00Z", "2026-03-29T02:00:00+01:00"),
    ("Europe/London", "2026-10-25T00:59Z", "2026-10-25T01:59:00+01:00"),
    ("Europe/London", "2026-10-25T01:00Z", "2026-10-25T01:00:00+00:00"),
    ("America/New_York", "2026-03-08T06:59Z", "2026-03-08T01:59:00-05:00"),
    ("America/New_York", "2026-03-08T07:00Z", "2026-03-08T03:00:00-04:00"),
    ("America/New_York", "2026-11-01T05:59Z", "2026-11-01T01:59:00-04:00"),
    ("America/New_York", "2026-11-01T06:00Z", "2026-11-01T01:00:00-05:00"),
])
def test_actual_dst_boundaries(zone, stamp, expected):
    assert localize(parse_instant(stamp), zone).isoformat() == expected


@pytest.mark.parametrize("zone,stamp,error", [
    ("Europe/London", "2026-03-29T01:30", "Nonexistent"),
    ("Europe/London", "2026-10-25T01:30", "Ambiguous"),
    ("America/New_York", "2026-03-08T02:30", "Nonexistent"),
    ("America/New_York", "2026-11-01T01:30", "Ambiguous"),
])
def test_naive_dst_wall_times_not_guessed(zone, stamp, error):
    with pytest.raises(ValueError, match=error):
        parse_instant(stamp, zone)


def test_explicit_offsets_disambiguate_fold():
    a = parse_instant("2026-10-25T01:30+01:00", "Europe/London")
    b = parse_instant("2026-10-25T01:30+00:00", "Europe/London")
    assert (b - a).total_seconds() == 3600


@pytest.mark.parametrize("zone", ["Not/AZone", "CST", "EST", "+08:00", "../zone", None])
def test_invalid_zone(zone):
    with pytest.raises(ValueError):
        get_zone(zone)


@pytest.mark.parametrize("value", ["22:15", "2026-09-21", "not-a-date", "2026-09-31T12:00"])
def test_date_and_time_are_required(value):
    with pytest.raises(ValueError):
        parse_instant(value)


def test_no_naive_instants_in_agent_boundary():
    with pytest.raises(ValueError, match="aware"):
        require_aware(datetime(2026, 9, 21, 10))
    with pytest.raises(ValueError, match="Nonexistent"):
        require_aware(datetime(2026, 3, 29, 1, 30, tzinfo=ZoneInfo("Europe/London")))


def test_default_now_is_aware_and_current():
    before = datetime.now(timezone.utc)
    result = parse_instant(None)
    after = datetime.now(timezone.utc)
    assert before <= result <= after
