from dataclasses import replace
from datetime import datetime

import pytest

from ptime.agents.time_adapter import TimeAdapterAgent
from ptime.core.config import load_settings
from ptime.core.timezone import parse_instant
from ptime.models import Region

CHINA = Region("China", "Asia/Shanghai")


@pytest.mark.parametrize("clock,expected", [
    ("00:00", "avoid"), ("06:59", "avoid"), ("07:00", "early"),
    ("08:59", "early"), ("09:00", "active"), ("11:59", "active"),
    ("12:00", "soft"), ("13:59", "soft"), ("14:00", "active"),
    ("17:59", "active"), ("18:00", "informal"), ("20:59", "informal"),
    ("21:00", "weak"), ("22:59", "weak"), ("23:00", "avoid"), ("23:59", "avoid"),
])
def test_every_window_boundary(clock, expected):
    window = TimeAdapterAgent().window_for(parse_instant(f"2026-09-21T{clock}"), CHINA)
    assert window.working_status == expected
    assert 0 <= window.communication_score <= 1


def test_default_nine_regions():
    result = TimeAdapterAgent().run(parse_instant("2026-09-21T22:15"))
    assert len(result) == 9
    assert {r.region for r in result} >= {"London", "New York", "Boston", "Greenwich, CT"}
    assert all(r.calendar_verified is False for r in result)


def test_recipient_weekday_not_base_weekday():
    # Monday in China, still Sunday in California.
    result = TimeAdapterAgent().run(parse_instant("2026-09-21T00:15"), ["SanFrancisco"])[0]
    assert result.local_date == "2026-09-20"
    assert result.weekday == "Sunday"
    assert result.working_status == "weekend"
    assert result.communication_score == pytest.approx(0.95 * 0.45)
    assert "interview" not in result.recommended_modes


def test_configurable_week():
    config = replace(load_settings(), working_weekdays=(6,))
    window = TimeAdapterAgent(config).window_for(parse_instant("2026-09-20T10:00"), CHINA)
    assert window.working_status == "active"


def test_region_selection_empty_unique_and_invalid():
    agent = TimeAdapterAgent()
    instant = parse_instant("2026-09-21T22:15")
    assert agent.run(instant, []) == []
    assert len(agent.run(instant, ["London", "London"])) == 1
    with pytest.raises(ValueError, match="Unknown region"):
        agent.run(instant, ["Unknown"])


def test_empty_region_selection_still_requires_aware_time():
    with pytest.raises(ValueError, match="timezone-aware"):
        TimeAdapterAgent().run(datetime(2026, 9, 21), [])
