import shutil
from pathlib import Path

import pytest
import yaml

from ptime.core.config import load_settings, minute
from ptime.models import unit


@pytest.fixture
def config_dir(tmp_path):
    source = Path(__file__).parents[1] / "config"
    for path in source.glob("*.yaml"):
        shutil.copyfile(path, tmp_path / path.name)
    return tmp_path


@pytest.mark.parametrize("kind", ["weights", "nan", "gap", "overlap", "weekdays", "zero_days", "region"])
def test_bad_config_is_rejected(config_dir, kind):
    filename = "scoring.yaml" if kind in {"weights", "nan", "zero_days"} else "regions.yaml" if kind == "region" else "working_windows.yaml"
    path = config_dir / filename
    data = yaml.safe_load(path.read_text())
    if kind == "weights":
        data["weights"]["time_score"] = 0.9
    elif kind == "nan":
        data["weights"]["time_score"] = float("nan")
    elif kind == "gap":
        data["windows"][1]["start"] = "07:30"
    elif kind == "overlap":
        data["windows"][1]["start"] = "06:30"
    elif kind == "weekdays":
        data["working_weekdays"] = [True]
    elif kind == "zero_days":
        data["recency_days"] = 0
    elif kind == "region":
        data["London"]["timezone"] = "Not/AZone"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_settings(config_dir)


@pytest.mark.parametrize("value", [True, float("nan"), float("inf"), -0.1, 1.1, "0.5"])
def test_scores_finite_and_bounded(value):
    with pytest.raises(ValueError):
        unit(value, "test")


@pytest.mark.parametrize("value", ["9:00", "24:30", "25:00", "10:99", "12:00:00", 900])
def test_window_minute_validation(value):
    with pytest.raises(ValueError):
        minute(value)
