import json
from dataclasses import replace
from pathlib import Path
import socket

import pytest
import yaml

from ptime.__main__ import main
from ptime import __version__
from ptime.core.channels import load_channels
from ptime.integrations.base import MockCommunicationSource, parse_snapshot
from ptime.integrations.pemail import PEmailSource
from ptime.integrations.plinkedin import PLinkedInSource
from ptime.integrations.pconnection import PConnectionSource
from ptime.integrations.pglobal import PGlobalSource
from ptime.integrations.pkago import PKagoSource
from ptime.models import PendingAction

ROW = {"id": "demo", "name": "Example Person", "region": "London",
       "timezone": "Europe/London", "channels": ["email"], "synthetic": True}
ACTION = {"id": "draft", "contact_id": "demo", "channel": "email"}
DOC = {"contacts": [ROW], "pending_actions": [ACTION]}
ROOT = Path(__file__).parents[1]


@pytest.mark.parametrize("source", [PEmailSource, PLinkedInSource, PConnectionSource, PGlobalSource, PKagoSource])
@pytest.mark.parametrize("suffix", [".json", ".yaml"])
def test_local_integrations_share_snapshot_contract(source, suffix, tmp_path):
    path = tmp_path / ("input" + suffix)
    path.write_text(json.dumps(DOC) if suffix == ".json" else yaml.safe_dump(DOC), encoding="utf-8")
    instance = source(path)
    assert instance.get_contacts()[0].source == instance.source_name
    assert instance.get_pending_actions()[0].contact_id == "demo"
    # A file edit does not split the already-loaded contact/action snapshot.
    path.write_text("{}", encoding="utf-8")
    assert instance.get_contacts()[0].id == "demo"
    assert len(instance.get_pending_actions()) == 1


@pytest.mark.parametrize("doc", [
    {}, {"contacts": []}, {"contacts": {}, "pending_actions": []},
    {"contacts": [ROW, ROW], "pending_actions": []},
    {"contacts": [ROW], "pending_actions": [ACTION, ACTION]},
    {"contacts": [ROW], "pending_actions": [{**ACTION, "contact_id": "unknown"}]},
    {"contacts": [{**ROW, "id": ""}], "pending_actions": []},
    {"contacts": [{**ROW, "timezone": None}], "pending_actions": []},
    {"contacts": [{**ROW, "channels": ["sms"]}], "pending_actions": []},
    {"contacts": [{**ROW, "region": "London", "location": "Boston"}], "pending_actions": []},
    {"contacts": [ROW], "pending_actions": [{**ACTION, "due_at": "2026-09-21T12:00"}]},
    {"contacts": [ROW], "pending_actions": [{**ACTION, "unexpected": True}]},
])
def test_invalid_snapshot_rejected(doc):
    with pytest.raises(ValueError):
        parse_snapshot(doc, "test")


@pytest.mark.parametrize("change", [
    {"channels": "email"}, {"channels": ["email", "email"]},
    {"preferred_contact_windows": ["22:00-07:00"]},
    {"preferred_contact_windows": ["not-a-window"]},
    {"preferred_contact_windows": ["25:00-26:00"]},
    {"context": "made_up"}, {"source_systems": "PEmail"},
    {"last_contact_at": "2026-09-21T12:00"},
    {"last_contact": "2026-09-20", "last_contact_at": "2026-09-21T12:00Z"},
])
def test_contact_extensions_validated(change):
    with pytest.raises(ValueError):
        parse_snapshot({"contacts": [{**ROW, **change}], "pending_actions": []}, "test")


@pytest.mark.parametrize("change", [
    {"confirmed": True}, {"expected_reply": True},
    {"scheduled_at": "2026-09-21T12:00Z"},
    {"confirmed": "yes"},
    {"scheduled_at": "2026-09-21T12:00Z", "scheduled_until": "2026-09-21T11:00Z"},
    {"scheduled_at": "2026-09-21T12:00Z", "scheduled_until": "2026-09-21T13:00Z"},
])
def test_action_validation(change):
    with pytest.raises(ValueError):
        PendingAction(**{**ACTION, **change})


@pytest.mark.parametrize("command", ["talk", "email"])
def test_cli_empty_by_default_and_no_network(command, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: pytest.fail("Unexpected network call"))
    assert main([command, "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total_decisions"] == 0 and data["recommendations"] == []
    assert data["version"] == __version__
    assert data["schema_version"] == "2.0"
    assert "No messages sent" in data["notice"]


@pytest.mark.parametrize("command,ready,deferred", [("talk", 3, 2), ("email", 1, 1)])
def test_demo_commands(command, ready, deferred, capsys):
    main([command, "--demo", "--at", "2026-09-21T22:15", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert len(data["recommendations"]) == ready and len(data["deferred"]) == deferred
    assert all(row["synthetic"] for row in data["recommendations"] + data["deferred"])
    assert all(row["requires_human_approval"] for row in data["recommendations"])


@pytest.mark.parametrize("args", [
    ["talk", "--input", "missing.yaml"], ["email", "--limit", "0"],
    ["talk", "--demo", "--source", "pemail"],
])
def test_cli_errors(args, capsys):
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2
    assert "PTime error:" in capsys.readouterr().err


@pytest.mark.parametrize("command", ["talk", "email"])
def test_text_cli_reports_next_date_and_no_sending(command, capsys):
    main([command, "--demo", "--at", "2026-09-21T22:15"])
    output = capsys.readouterr().out
    assert "2026-09-22T09:00:00+08:00" in output
    assert "No messages sent" in output


@pytest.mark.parametrize("source", ["pemail", "plinkedin", "pconnection", "pglobal", "pkago"])
def test_cli_explicit_source_file(source, tmp_path, capsys):
    path = tmp_path / "input.json"
    path.write_text(json.dumps(DOC), encoding="utf-8")
    main(["email", "--source", source, "--input", str(path),
          "--at", "2026-09-21T22:15", "--json"])
    result = json.loads(capsys.readouterr().out)
    assert result["total_decisions"] == 1
    assert source + "_communication_export" in result["recommendations"][0]["source_systems"]


def test_mock_returns_copies_and_demo_is_synthetic():
    doc = yaml.safe_load((ROOT / "data/communication.example.yaml").read_text(encoding="utf-8"))
    contacts, actions = parse_snapshot(doc, "synthetic_demo")
    assert all(contact.synthetic for contact in contacts)
    source = MockCommunicationSource(contacts, actions)
    source.get_contacts().clear()
    assert len(source.get_contacts()) == 5


@pytest.mark.parametrize("mutation", ["channel", "context", "score", "sync", "overlap", "days", "unknown"])
def test_channel_config_errors(mutation, tmp_path):
    doc = yaml.safe_load((ROOT / "config/channels.yaml").read_text(encoding="utf-8"))
    if mutation == "channel":
        del doc["channels"]["email"]
    elif mutation == "context":
        doc["contexts"]["professional"]["working_days_only"] = "yes"
    elif mutation == "score":
        doc["channels"]["email"]["score"] = float("nan")
    elif mutation == "sync":
        doc["channels"]["email"]["synchronous"] = True
    elif mutation == "overlap":
        doc["channels"]["email"]["windows"] = ["09:00-12:00", "11:00-13:00"]
    elif mutation == "days":
        doc["search_days"] = 100
    else:
        doc["extra"] = "not silently accepted"
    (tmp_path / "channels.yaml").write_text(yaml.safe_dump(doc), encoding="utf-8")
    with pytest.raises(ValueError):
        load_channels(tmp_path)
