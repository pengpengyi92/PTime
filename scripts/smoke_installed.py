"""Verify an installed wheel without relying on checkout imports or working directory."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def invoke(*args: str, cwd: str) -> dict:
    completed = subprocess.run(
        [sys.executable, "-m", "ptime", *args, "--json"],
        cwd=cwd, check=True, capture_output=True, text=True, timeout=30,
    )
    return json.loads(completed.stdout)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="ptime-wheel-") as directory:
        probe = subprocess.run(
            [sys.executable, "-c", "import ptime; print(ptime.__file__)"],
            cwd=directory, check=True, capture_output=True, text=True, timeout=30,
        )
        imported = Path(probe.stdout.strip()).resolve()
        assert not imported.is_relative_to(ROOT / "ptime"), imported
        at = "2026-09-21T22:15"
        now = invoke("now", "--at", at, cwd=directory)
        assert len(now["regions"]) == 9
        windows = {row["region"]: row for row in now["regions"]}
        assert windows["London"]["local_time"] == "15:15"
        assert windows["New York"]["local_time"] == "10:15"

        empty = invoke("contacts", cwd=directory)
        assert empty["contact_count"] == 0
        demo = invoke("contacts", "--demo", "--at", at, cwd=directory)
        assert demo["contact_count"] == 4
        assert demo["eligible_count"] == 2
        assert demo["deferred_count"] == 2
        assert all(row["synthetic"] for row in demo["recommendations"] + demo["deferred"])
        assert all(not row["calendar_verified"] for row in demo["recommendations"])
        current = invoke("now", cwd=directory)
        assert current["evaluated_at"]
        assert current["version"] == (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        for command in ("talk", "email"):
            assert invoke(command, cwd=directory)["total_decisions"] == 0
        talk = invoke("talk", "--demo", "--at", at, cwd=directory)
        assert talk["decision_counts"] == {"SEND_NOW": 3, "WAIT": 2}
        email = invoke("email", "--demo", "--at", at, cwd=directory)
        assert email["decision_counts"] == {"SEND_NOW": 1, "WAIT": 1}
        assert email["deferred"][0]["next_window_local"] == "2026-09-22T09:00:00+08:00"
        assert all(row["requires_human_approval"] for row in email["recommendations"])
        festival_at = "2026-09-25T10:00+08:00"
        for view in ("china", "global", "united_states", "united_kingdom"):
            events = invoke("festivals", "--region", view, "--days", "120", "--at", festival_at, cwd=directory)
            assert events["items"] and events["schema_version"] == "2.1"
        for style in ("general", "professional", "reconnect"):
            for locale in ("zh-CN", "en"):
                greeting = invoke("greetings", "--festival", "mid_autumn", "--style", style, "--locale", locale,
                                  "--at", festival_at, cwd=directory)
                assert greeting["items"][0]["preview"]
        for command in ("touchpoints", "followups"):
            assert invoke(command, cwd=directory)["total"] == 0
        touch = invoke("touchpoints", "--demo", "--festival", "mid_autumn", "--at", festival_at, cwd=directory)
        assert touch["state_counts"] == {"SUGGEST": 1, "FOLLOW_UP_ELIGIBLE": 1, "GREETED": 1, "SKIP": 1, "BLOCKED": 1}
        follow = invoke("followups", "--demo", "--at", festival_at, cwd=directory)
        assert follow["state_counts"] == {"FOLLOW_UP_ELIGIBLE": 1, "SKIP": 1}
        assert all(row["user_approval_required"] for row in follow["items"])
        # Verify the console entry point, not just python -m, in the installed environment.
        executable = Path(sys.executable).parent / ("ptime.exe" if sys.platform == "win32" else "ptime")
        version = subprocess.run([str(executable), "--version"], cwd=directory, check=True, capture_output=True, text=True)
        assert version.stdout.strip() == current["version"]
        print(f"Installed-wheel smoke PASS: Python {sys.version.split()[0]}, eight commands + console entry point, four calendars, six bilingual previews, empty defaults and three synthetic demos")


if __name__ == "__main__":
    main()
