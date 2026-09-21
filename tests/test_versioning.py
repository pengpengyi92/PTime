from pathlib import Path
import re
import tomllib

from ptime import __version__

ROOT = Path(__file__).parents[1]


def test_version_sources_and_release_docs_agree():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert re.fullmatch(r"\d+\.\d+\.\d+", version)
    assert version == __version__ == "2.0.0"
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["version"] == version
    assert "ptime.integrations" in project["tool"]["setuptools"]["packages"]
    assert "communication.example.yaml" in project["tool"]["setuptools"]["package-data"]["ptime_examples"]
    assert f"[{version}]" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    for file in ("AGENT.md", "README.md", "releases/V2.0.md"):
        assert "V2.0" in (ROOT / file).read_text(encoding="utf-8")
    assert "Not Released" in (ROOT / "releases/V1.0.md").read_text(encoding="utf-8")
