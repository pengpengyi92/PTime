import json
from pathlib import Path

import pytest
import yaml

from ptime.__main__ import main
from ptime.adapters.base import parse_contacts
from ptime.adapters.pglobal import PGlobalSource
from ptime.adapters.plinkedin import PLinkedInSource
from ptime.adapters.pconnection import PConnectionSource
from ptime.agents.contact_adapter import GlobalContactAdapterAgent
from ptime.core.timezone import parse_instant
from ptime.models import Contact, Opportunity

ROW = {"name": "Fictional", "location": "London", "timezone": "Europe/London", "synthetic": True}


@pytest.mark.parametrize("adapter", [PGlobalSource, PLinkedInSource, PConnectionSource])
@pytest.mark.parametrize("suffix", [".json", ".yaml"])
def test_local_adapters(adapter, suffix, tmp_path):
    path = tmp_path / ("example" + suffix)
    data = {"contacts": [ROW]}
    path.write_text(json.dumps(data) if suffix == ".json" else yaml.safe_dump(data), encoding="utf-8")
    source = adapter(path)
    contacts = source.get_contacts()
    assert len(contacts) == 1
    assert contacts[0].source == source.source_name
    result = GlobalContactAdapterAgent().run(source, parse_instant("2026-09-21T22:15"))
    assert result[0].eligible_now


@pytest.mark.parametrize("record", [
    {}, {**ROW, "timezone": "London"}, {**ROW, "priority": "P9"},
    {**ROW, "relationship": "unknown"}, {**ROW, "topics": "not a list"},
    {**ROW, "last_contact": "tomorrow"}, {**ROW, "do_not_contact": "false"},
    {**ROW, "next_action": "send_money"}, {**ROW, "name": "Name\x1b[31m"},
    {**ROW, "unknown_field": "do not silently discard"}, {**ROW, "opportunities": {}},
])
def test_malformed_records_rejected(record):
    with pytest.raises(ValueError):
        parse_contacts([record], "test")


def test_unsafe_yaml_rejected(tmp_path):
    path = tmp_path / "unsafe.yaml"
    path.write_text("!!python/object/apply:os.system ['echo unsafe']", encoding="utf-8")
    with pytest.raises(yaml.YAMLError):
        PGlobalSource(path).get_contacts()


def test_oversized_local_file(tmp_path):
    path = tmp_path / "large.json"
    path.write_text(" " * 1_000_001, encoding="utf-8")
    with pytest.raises(ValueError, match="1 MB"):
        PGlobalSource(path).get_contacts()


def test_timezone_is_required_even_with_location():
    with pytest.raises(ValueError):
        parse_contacts([{"name": "Example", "location": "London"}], "test")


def test_now_cli_json(capsys):
    assert main(["now", "--at", "2026-09-21T22:15", "--regions", "London", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["regions"][0]["local_time"] == "15:15"
    assert data["base_timezone"] == "Asia/Shanghai"


def test_default_contacts_never_fakes_real_people(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["contacts", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["contact_count"] == 0
    assert data["recommendations"] == []


def test_demo_is_explicit_and_synthetic(capsys):
    main(["contacts", "--demo", "--at", "2026-09-21T22:15", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert data["data_mode"] == "synthetic_demo"
    assert data["eligible_count"] == 2
    assert data["deferred_count"] == 2
    assert all(r["synthetic"] for r in data["recommendations"] + data["deferred"])


@pytest.mark.parametrize("args", [
    ["now", "--base-timezone", "Invalid/Zone"],
    ["now", "--at", "2026-10-25T01:30", "--base-timezone", "Europe/London"],
    ["now", "--regions", "Moon"],
    ["contacts", "--contacts", "nonexistent.json"],
    ["contacts", "--limit", "0"],
    ["contacts", "--demo", "--source", "pglobal"],
])
def test_cli_errors_no_traceback(args, capsys):
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2
    assert "PTime error:" in capsys.readouterr().err


def test_plain_cli_outputs(capsys):
    main(["now", "--at", "2026-09-21T22:15"])
    assert "London" in capsys.readouterr().out
    main(["contacts", "--demo", "--at", "2026-09-21T22:15"])
    output = capsys.readouterr().out
    assert "NOW TO TALK" in output and "DEFER" in output
    assert "No messages sent" in output


def test_contact_and_opportunity_validation():
    assert Contact(**ROW).topics == ()
    with pytest.raises(ValueError):
        Opportunity("bad", "Demo", status="invented")
    with pytest.raises(ValueError):
        Contact(**ROW, opportunities=("not an opportunity",))


def test_public_fixtures_contain_only_explicitly_synthetic_people():
    path = Path(__file__).parents[1] / "data/contacts.example.yaml"
    contacts = parse_contacts(yaml.safe_load(path.read_text(encoding="utf-8")), "test")
    assert contacts and all(c.synthetic for c in contacts)
