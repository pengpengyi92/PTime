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
        assert current["version"] == "2.0.0"
        for command in ("talk", "email"):
            assert invoke(command, cwd=directory)["total_decisions"] == 0
        talk = invoke("talk", "--demo", "--at", at, cwd=directory)
        assert talk["decision_counts"] == {"SEND_NOW": 3, "WAIT": 2}
        email = invoke("email", "--demo", "--at", at, cwd=directory)
        assert email["decision_counts"] == {"SEND_NOW": 1, "WAIT": 1}
        assert email["deferred"][0]["next_window_local"] == "2026-09-22T09:00:00+08:00"
        assert all(row["requires_human_approval"] for row in email["recommendations"])
        print(f"Installed-wheel V2 smoke PASS: Python {sys.version.split()[0]}, all four commands, packaged channels, empty defaults and both synthetic demos")


if __name__ == "__main__":
    main()
