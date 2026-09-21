"""Presentation for routing commands, separate from the compatible V0.1 CLI."""

from collections import Counter
from dataclasses import asdict
from pathlib import Path
import json

import yaml

from ptime.agents.time_adapter import TimeAdapterAgent
from ptime.core.channels import load_channels
from ptime.core.config import default_resource
from ptime.core.contact_router import route
from ptime.integrations.base import LocalCommunicationSource, MockCommunicationSource, parse_snapshot
from ptime.integrations.pemail import PEmailSource
from ptime.integrations.plinkedin import PLinkedInSource
from ptime.integrations.pconnection import PConnectionSource
from ptime.integrations.pglobal import PGlobalSource
from ptime.integrations.pkago import PKagoSource

COMMUNICATION_SOURCES = {
    "local": LocalCommunicationSource, "pemail": PEmailSource, "plinkedin": PLinkedInSource,
    "pconnection": PConnectionSource, "pglobal": PGlobalSource, "pkago": PKagoSource,
}


def run_routing(args, instant, settings, common) -> int:
    if args.limit <= 0:
        raise ValueError("--limit must be a positive integer")
    if args.demo and args.source != "local":
        raise ValueError("--demo cannot claim an external source")
    policy = load_channels(args.config_dir)
    if args.demo:
        document = yaml.safe_load(default_resource("communication.example.yaml", "ptime_examples").read_text(encoding="utf-8"))
        contacts, actions = parse_snapshot(document, "synthetic_demo")
        if not all(contact.synthetic for contact in contacts):
            raise ValueError("Bundled demo must contain synthetic contacts only")
        source = MockCommunicationSource(contacts, actions)
        mode = "synthetic_demo"
    else:
        path = args.input or Path("private/communication.yaml")
        if args.input is None and not path.exists():
            source = MockCommunicationSource([], [])
        else:
            source = COMMUNICATION_SOURCES[args.source](path)
        mode = "explicit_local_data"
    contacts, actions = source.get_contacts(), source.get_pending_actions()
    results = route(contacts, actions, instant, settings, policy, email_only=args.command == "email")
    ready = [item for item in results if item.decision == "SEND_NOW"]
    deferred = [item for item in results if item.decision != "SEND_NOW"]
    windows = TimeAdapterAgent(settings).run(instant)
    if args.json:
        print(json.dumps({
            **common, "schema_version": "2.0", "data_mode": mode, "command": args.command,
            "contact_count": len(contacts), "queued_action_count": len(actions),
            "decision_counts": dict(Counter(item.decision for item in results)),
            "total_decisions": len(results),
            "recommendations": [asdict(item) for item in ready[:args.limit]],
            "deferred": [asdict(item) for item in deferred[:args.limit]],
            "global_windows": [asdict(window) for window in windows],
        }, ensure_ascii=True, indent=2))
        return 0
    print(f"PTIME {args.command.upper()} [{mode}]")
    print(f"Base: {common['base_time']} [{common['base_timezone']}]")
    if args.command == "talk":
        print("GLOBAL WINDOWS")
        for window in sorted(windows, key=lambda item: -item.communication_score):
            print(f"- {window.region}: {window.local_datetime} {window.working_status}")
    print("SEND NOW (timing suggestion only; human approval required)")
    if not ready:
        print("No eligible drafts or contact suggestions.")
    for item in ready[:args.limit]:
        channels = " / ".join(item.available_channels) or item.channel
        print(f"- {item.person} | {item.local_datetime} | {channels} | score {item.score:.3f}")
        print(f"  Action: {item.suggested_action}")
        if item.topics:
            print("  Topics: " + ", ".join(item.topics))
        print("  Why: " + "; ".join(item.reasons))
    print("WAIT / REVIEW / BLOCKED / SKIP")
    for item in deferred[:args.limit]:
        print(f"- {item.person} | {item.channel or 'no channel'} | {item.decision}: {item.suggested_action}")
        if item.next_window_at:
            print(f"  Next: {item.next_window_local} [{item.timezone}] / {item.next_window_at} UTC")
    if not contacts:
        print("No contacts loaded. Use --input private/communication.yaml or --demo (fictional people).")
    elif args.command == "email" and not results:
        print("No email actions in the supplied queue. PTime does not create drafts.")
    print(common["notice"])
    return 0
