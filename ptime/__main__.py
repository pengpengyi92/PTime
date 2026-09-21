"""On-demand CLI. No automatic messages, background tasks or network calls."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

import yaml

from ptime import __version__
from ptime.cli_routing import COMMUNICATION_SOURCES, run_routing
from ptime.adapters.base import LocalContactSource, parse_contacts
from ptime.adapters.pglobal import PGlobalSource
from ptime.adapters.plinkedin import PLinkedInSource
from ptime.adapters.pconnection import PConnectionSource
from ptime.agents.contact_adapter import GlobalContactAdapterAgent
from ptime.agents.time_adapter import TimeAdapterAgent
from ptime.core.config import default_resource, load_settings
from ptime.core.timezone import localize, parse_instant
from ptime.core.recommender import recommend

NOTICE = "Heuristic windows, not calendar availability. No messages sent. Human approval required."
SOURCES = {"local": LocalContactSource, "pglobal": PGlobalSource, "plinkedin": PLinkedInSource, "pconnection": PConnectionSource}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="ptime", description="Global time -> people -> suggested communication actions")
    root.add_argument("--version", action="version", version=__version__)
    sub = root.add_subparsers(dest="command", required=True)
    for name in ("now", "contacts", "talk", "email"):
        command = sub.add_parser(name)
        command.add_argument("--at", help="ISO datetime; naive times use --base-timezone, DST ambiguity is rejected")
        command.add_argument("--base-timezone", help="IANA zone, default Asia/Shanghai")
        command.add_argument("--config-dir", type=Path, help="Config directory; talk/email also require channels.yaml")
        command.add_argument("--json", action="store_true", help="Structured output; contains private names if supplied locally")
        if name == "now":
            command.add_argument("--regions", nargs="+", help="Region IDs, e.g. London NewYork")
        elif name in {"talk", "email"}:
            source = command.add_mutually_exclusive_group()
            source.add_argument("--input", type=Path, help="Normalized communication YAML/JSON snapshot")
            source.add_argument("--demo", action="store_true", help="Use fictional communication examples")
            command.add_argument("--source", choices=list(COMMUNICATION_SOURCES), default="local")
            command.add_argument("--limit", type=int, default=10)
        else:
            source = command.add_mutually_exclusive_group()
            source.add_argument("--contacts", type=Path, help="Explicit normalized YAML/JSON file")
            source.add_argument("--demo", action="store_true", help="Use clearly fictional bundled examples")
            command.add_argument("--source", choices=list(SOURCES), default="local")
            command.add_argument("--limit", type=int, default=10)
    return root


def main(argv: list[str] | None = None) -> int:
    args_parser = parser()
    args = args_parser.parse_args(argv)
    try:
        settings = load_settings(args.config_dir)
        base_zone = args.base_timezone or settings.base_timezone
        instant = parse_instant(args.at, base_zone)
        base = localize(instant, base_zone)
        common = {"version": __version__, "evaluated_at": instant.isoformat(), "base_timezone": base_zone, "base_time": base.isoformat(timespec="seconds"), "notice": NOTICE}
        if args.command in {"talk", "email"}:
            return run_routing(args, instant, settings, common)
        if args.command == "now":
            windows = TimeAdapterAgent(settings).run(instant, args.regions)
            if args.json:
                print(json.dumps({**common, "regions": [asdict(w) for w in windows]}, ensure_ascii=True, indent=2))
            else:
                print("PTime - Global Communication Window")
                print(f"Base: {base.isoformat(timespec='minutes')} [{base_zone}]")
                print(f"{'REGION':22} {'LOCAL DATE/TIME':18} {'OFFSET':7} {'STATUS':10} SCORE")
                for window in windows:
                    print(f"{window.region:22} {window.local_date} {window.local_time}   {window.utc_offset:7} {window.working_status:10} {window.communication_score:.2f}")
                print(NOTICE)
            return 0
        if args.limit <= 0:
            raise ValueError("--limit must be a positive integer")
        if args.demo and args.source != "local":
            raise ValueError("--demo cannot claim an external source adapter")
        if args.demo:
            document = yaml.safe_load(default_resource("contacts.example.yaml", "ptime_examples").read_text(encoding="utf-8"))
            contacts = parse_contacts(document, "synthetic_demo")
            if not all(c.synthetic for c in contacts):
                raise ValueError("Bundled demo must contain synthetic contacts only")
            results = recommend(contacts, instant, settings)
            mode = "synthetic_demo"
        else:
            path = args.contacts or Path("private/contacts.yaml")
            if args.contacts is None and not path.exists():
                results = []
            else:
                results = GlobalContactAdapterAgent(settings).run(SOURCES[args.source](path), instant)
            mode = "explicit_local_data"
        eligible = [r for r in results if r.eligible_now]
        deferred = [r for r in results if not r.eligible_now]
        if args.json:
            print(json.dumps({
                **common, "data_mode": mode, "contact_count": len(results),
                "eligible_count": len(eligible), "deferred_count": len(deferred),
                "recommendations": [asdict(r) for r in eligible[:args.limit]],
                "deferred": [asdict(r) for r in deferred[:args.limit]],
            }, ensure_ascii=True, indent=2))
        else:
            print(f"PTime - Who can I talk to? [{mode}]")
            print(f"Base: {base.isoformat(timespec='minutes')} [{base_zone}]")
            if not results:
                print("No contacts loaded. Use --contacts private/contacts.yaml or --demo (fictional people).")
            else:
                print("NOW TO TALK (suggestions, not appointments)")
                if not eligible:
                    print("No suitable contact windows now.")
                for index, item in enumerate(eligible[:args.limit], 1):
                    print(f"{index}. {item.person} | {item.location} | {item.local_datetime}")
                    print(f"   {item.priority} | rank {item.final_score:.3f} | availability heuristic {item.availability_score:.3f}")
                    print(f"   Action: {item.recommended_action.recommendation}")
                    print("   Why: " + "; ".join(item.reason))
                if deferred:
                    print("DEFER / DO NOT CONTACT")
                    for item in deferred[:args.limit]:
                        print(f"- {item.person} | {item.local_datetime}: {item.recommended_action.recommendation}")
            print(NOTICE)
        return 0
    except (ValueError, TypeError, OSError, yaml.YAMLError) as exc:
        args_parser.exit(2, f"PTime error: {exc}\n")


if __name__ == "__main__":
    sys.exit(main())
