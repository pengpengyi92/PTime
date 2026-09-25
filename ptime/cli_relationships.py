"""Read-only V2.1 CLI; public calendars, explicit private snapshots, no sending."""

from collections import Counter
from dataclasses import asdict, replace
from datetime import date, datetime
import json
from pathlib import Path

import yaml

from ptime.core.channels import load_channels
from ptime.core.config import default_resource, read_document
from ptime.festivals.calendar import load_calendars, upcoming
from ptime.festivals.models import STYLES
from ptime.festivals.router import route_touchpoints
from ptime.festivals.snapshot import parse_relationship_snapshot
from ptime.followups.router import route_followups
from ptime.greetings.renderer import render
from ptime.greetings.templates import load_templates, select_templates

COMMANDS = {"festivals", "greetings", "touchpoints", "followups"}


def add_arguments(command, name):
    if name in {"festivals", "touchpoints"}:
        command.add_argument("--region", help="Explicit calendar view, not inferred contact culture")
        command.add_argument("--days", type=int, default=30)
        command.add_argument("--festival", help="Canonical festival ID")
    if name == "festivals":
        command.add_argument("--include-non-greeting", action="store_true")
    if name == "greetings":
        command.add_argument("--festival", required=True)
        command.add_argument("--style", choices=sorted(STYLES), default="general")
        command.add_argument("--locale", choices=["en", "zh-CN"], default="en")
        command.add_argument("--audience", default="general")
    if name in {"touchpoints", "followups"}:
        group = command.add_mutually_exclusive_group()
        group.add_argument("--input", type=Path)
        group.add_argument("--demo", action="store_true")
        command.add_argument("--limit", type=int, default=20)


def serial(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"Not serializable: {type(value)}")


def run_relationships(args, instant, settings, common):
    catalog = load_calendars(args.config_dir)
    templates = load_templates(args.config_dir)
    warnings = []
    if any(t.festival_id not in catalog.festivals for t in templates):
        raise ValueError("Template refers to unknown festival")
    mode = "public_configuration"
    if args.command == "festivals":
        values, warnings = upcoming(catalog, instant, args.days, args.region, args.festival,
                                    include_non_greeting=args.include_non_greeting)
        rows = [asdict(v) for v in values]
    elif args.command == "greetings":
        catalog.select(festival_id=args.festival)
        values = select_templates(templates, args.festival, args.style, args.locale, args.audience)
        rows = [{**asdict(v), "preview": render(v)} for v in values]
    else:
        if not 1 <= args.limit <= 1000:
            raise ValueError("--limit must be 1..1000")
        if args.demo:
            doc = yaml.safe_load(default_resource("touchpoints.example.yaml", "ptime_examples").read_text(encoding="utf-8"))
            mode = "synthetic_demo"
        else:
            path = args.input or Path("private/touchpoints.yaml")
            doc = ({key: [] for key in ("contacts", "pending_actions", "preferences", "history", "followups")}
                   if args.input is None and not path.exists() else read_document(path))
            mode = "explicit_local_data"
        snapshot = parse_relationship_snapshot(doc, catalog, templates, mode)
        if args.demo and not all(c.synthetic for c in snapshot.contacts):
            raise ValueError("Bundled fixtures must be explicitly synthetic")
        policy = load_channels(args.config_dir)
        followups = route_followups(snapshot, instant, settings, policy, common["base_timezone"])
        if args.command == "followups":
            values = followups
        else:
            values, warnings = route_touchpoints(snapshot, catalog, templates, instant, args.days, args.region,
                                                args.festival, settings, policy, common["base_timezone"])
            eligible_by_cycle = {}
            requests = {r.id: r for r in snapshot.followups}
            for f in followups:
                cycle = requests[f.id].cycle if f.id in requests else f.id.removeprefix(f"after:{f.contact_id}:")
                if cycle and f.followup_eligible_at:
                    eligible_by_cycle[(f.contact_id, cycle)] = f
            merged = []
            for item in values:
                follow = eligible_by_cycle.get((item.contact_id, item.cycle))
                if follow and item.state == "REPLIED":
                    item = replace(item, followup_eligible_at=follow.followup_eligible_at,
                                   state="FOLLOW_UP_ELIGIBLE" if follow.state == "FOLLOW_UP_ELIGIBLE" else "REPLIED")
                merged.append(item)
            states = {"SUGGEST": 0, "FOLLOW_UP_ELIGIBLE": 1, "WAIT": 2, "REPLIED": 3,
                      "GREETED": 4, "SKIP": 5, "CLOSED": 6, "BLOCKED": 7}
            values = sorted(merged, key=lambda r: (states[r.state], -r.score, r.contact_id, r.cycle))
        rows = [asdict(v) for v in values]
    total = len(rows)
    counts = dict(Counter(row["state"] for row in rows if "state" in row))
    rows = rows[:getattr(args, "limit", len(rows))]
    payload = {**common, "schema_version": "2.1", "command": args.command, "data_mode": mode,
               "total": total, "state_counts": counts, "items": rows, "warnings": warnings,
               "user_approval_required": True}
    if args.json:
        print(json.dumps(payload, default=serial, ensure_ascii=True, indent=2))
    else:
        print(f"PTIME {args.command.upper()} [{mode}] | {total} results")
        for row in rows:
            if args.command == "greetings":
                print(f"{row['id']}: {row['preview']}")
            elif args.command == "festivals":
                print(f"{row['cultural_date']} | {row['festival_id']} | {row['timezone']} | greeting={row['greeting_appropriate']}")
            else:
                window = row.get("followup_eligible_at") or row.get("not_before")
                print(f"{row['contact_id']} | {row.get('cycle', row.get('id'))} | {row['state']} | {window}")
                print("  " + "; ".join(row["reason"]))
        for warning in warnings:
            print("WARNING: " + warning)
        print(common["notice"])
    return 0
