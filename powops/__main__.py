"""powops CLI entry point.

Usage:
    python -m powops status              # Show garden health
    python -m powops status --json       # JSON output
    python -m powops full                # Full check: status + history + alerts + volume
    python -m powops history             # Show check history
    python -m powops history --source X  # History for one source
    python -m powops uptime              # Uptime statistics
    python -m powops volume              # Volume summary
    python -m powops schemas             # Show known schemas
    python -m powops alerts              # Show alert state
    python -m powops backup              # Sync raw data to R2
    python -m powops check <source>      # Check a specific source
    python -m powops sources             # List all configured sources
"""

import argparse
import json
import sys


def main():
    from .config import ensure_dirs
    ensure_dirs()

    parser = argparse.ArgumentParser(
        prog="powops",
        description="Layer 1 command centre for POW gardens",
    )
    sub = parser.add_subparsers(dest="command")

    # status
    status_p = sub.add_parser("status", help="Show garden health status")
    status_p.add_argument("--json", action="store_true", help="Output as JSON")
    status_p.add_argument("--no-color", action="store_true", help="Disable colors")
    status_p.add_argument("--manifest", type=str, help="Path to sources.yaml")

    # full (check + record + alert)
    full_p = sub.add_parser("full", help="Full check: status + history + alerts + volume")
    full_p.add_argument("--json", action="store_true", help="Output as JSON")
    full_p.add_argument("--no-color", action="store_true", help="Disable colors")
    full_p.add_argument("--dry-run", action="store_true", help="Don't fire alerts")

    # history
    hist_p = sub.add_parser("history", help="Show check history")
    hist_p.add_argument("--source", help="Filter to one source")
    hist_p.add_argument("--garden", help="Filter to one garden")
    hist_p.add_argument("--days", type=int, default=7, help="Days back (default 7)")
    hist_p.add_argument("--status", help="Filter by status")
    hist_p.add_argument("--json", action="store_true", help="Output as JSON")

    # uptime
    uptime_p = sub.add_parser("uptime", help="Uptime statistics")
    uptime_p.add_argument("--source", help="Filter to one source")
    uptime_p.add_argument("--days", type=int, default=7, help="Days back (default 7)")
    uptime_p.add_argument("--json", action="store_true", help="Output as JSON")

    # volume
    vol_p = sub.add_parser("volume", help="Volume summary")
    vol_p.add_argument("--days", type=int, default=7, help="Days back (default 7)")
    vol_p.add_argument("--json", action="store_true", help="Output as JSON")

    # schemas
    sub.add_parser("schemas", help="Show known schemas")

    # alerts
    sub.add_parser("alerts", help="Show alert state")

    # check
    check_p = sub.add_parser("check", help="Check a specific source")
    check_p.add_argument("source_id", help="Source ID to check")
    check_p.add_argument("--no-color", action="store_true", help="Disable colors")

    # sources
    sub.add_parser("sources", help="List all configured sources")

    # backup
    backup_p = sub.add_parser("backup", help="Sync raw data to R2")
    backup_p.add_argument("--garden", help="Sync specific garden only")
    backup_p.add_argument("--dry-run", action="store_true", help="Dry run")

    # incidents
    inc_p = sub.add_parser("incidents", help="Show incidents")
    inc_p.add_argument("--status", default="open", help="Filter by status (open, resolved, all)")
    inc_p.add_argument("--garden", help="Filter to one garden")
    inc_p.add_argument("--source", help="Filter to one source")
    inc_p.add_argument("--json", action="store_true", help="Output as JSON")

    # events
    ev_p = sub.add_parser("events", help="Show recent events")
    ev_p.add_argument("--days", type=int, default=1, help="Days back (default 1)")
    ev_p.add_argument("--garden", help="Filter to one garden")
    ev_p.add_argument("--source", help="Filter to one source")
    ev_p.add_argument("--type", help="Filter by event type")
    ev_p.add_argument("--json", action="store_true", help="Output as JSON")

    # repos
    repos_p = sub.add_parser("repos", help="Show GitHub repo status")
    repos_p.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.command == "status":
        from .status import run_status
        path = args.manifest if hasattr(args, "manifest") and args.manifest else None
        from pathlib import Path
        run_status(
            use_color=not args.no_color,
            fmt="json" if args.json else "table",
            path=Path(path) if path else None,
        )

    elif args.command == "full":
        from .health import check_all_full
        from .status import render_status_table, render_json
        result = check_all_full(dry_run=args.dry_run)
        if args.json:
            output = {
                "overall": result["overall"],
                "gardens": result["gardens"],
                "actions": result["actions"],
                "sources": [
                    {
                        "source_id": r.source_id,
                        "garden": r.garden,
                        "status": r.status,
                        "last_success": r.last_success.isoformat() if r.last_success else None,
                        "age_seconds": int(r.age.total_seconds()) if r.age else None,
                        "records": r.records,
                        "error": r.error,
                    }
                    for r in result["results"]
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            print(render_status_table(result["results"], use_color=not args.no_color))
            alerts = result["actions"].get("alerts_fired", [])
            if alerts:
                print("  Alerts:")
                for a in alerts:
                    print(f"    {a['source_id']}: {a['action']}")

    elif args.command == "history":
        from .history import get_history
        entries = get_history(
            source_id=args.source,
            garden=args.garden,
            days=args.days,
            status_filter=args.status,
        )
        if args.json:
            print(json.dumps(entries, indent=2))
        else:
            if not entries:
                print("  No history found.")
            else:
                print(f"\n  {'TS':<22} {'SOURCE':<22} {'GARDEN':<12} {'STATUS':<10} {'AGE':<10}")
                print(f"  {'─'*22} {'─'*22} {'─'*12} {'─'*10} {'─'*10}")
                for e in entries:
                    ts = e.get("ts", "")[:19]
                    sid = e.get("source_id", "")
                    g = e.get("garden", "")
                    s = e.get("status", "")
                    age = f"{e.get('age_seconds', 0)}s" if "age_seconds" in e else "—"
                    print(f"  {ts:<22} {sid:<22} {g:<12} {s:<10} {age:<10}")
                print(f"\n  {len(entries)} entries")
                print()

    elif args.command == "uptime":
        from .history import get_uptime_stats, get_source_timeline
        from .health import load_manifest
        manifest = load_manifest()
        sources = manifest.get("sources", [])

        if args.source:
            sources = [s for s in sources if s["id"] == args.source]

        if args.json:
            stats = {}
            for s in sources:
                stats[s["id"]] = get_uptime_stats(s["id"], days=args.days)
            print(json.dumps(stats, indent=2))
        else:
            print(f"\n  {'SOURCE':<22} {'CHECKS':<8} {'OK%':<8} {'STALE':<8} {'ERR':<8} {'AVG AGE':<10}")
            print(f"  {'─'*22} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*10}")
            for s in sources:
                stats = get_uptime_stats(s["id"], days=args.days)
                if stats["total_checks"] == 0:
                    continue
                avg = f"{stats['mean_age_seconds']}s" if stats.get("mean_age_seconds") else "—"
                print(f"  {s['id']:<22} {stats['total_checks']:<8} {stats['uptime_pct']:<8.1f} {stats['stale']:<8} {stats['error']:<8} {avg:<10}")
            print()

    elif args.command == "volume":
        from .volume import get_volume_summary
        summary = get_volume_summary(days=args.days)
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            if not summary:
                print("  No volume data found.")
            else:
                print(f"\n  {'SOURCE':<22} {'MEAN':<10} {'STDDEV':<10} {'MIN':<10} {'MAX':<10} {'SAMPLES':<8}")
                print(f"  {'─'*22} {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*8}")
                for sid, stats in sorted(summary.items()):
                    print(f"  {sid:<22} {stats['mean']:<10} {stats['stddev']:<10} {stats['min']:<10} {stats['max']:<10} {stats['count']:<8}")
                print()

    elif args.command == "schemas":
        from .schema import list_schemas
        schemas = list_schemas()
        if not schemas:
            print("  No schemas recorded yet.")
        else:
            print(f"\n  {'SOURCE':<22} {'GARDEN':<12} {'SNAPSHOT':<22} {'COLUMNS'}")
            print(f"  {'─'*22} {'─'*12} {'─'*22} {'─'*30}")
            for s in schemas:
                cols = ", ".join(s.get("columns", [])[:5])
                if len(s.get("columns", [])) > 5:
                    cols += f" (+{len(s['columns'])-5})"
                print(f"  {s['source_id']:<22} {s['garden']:<12} {s['snapshot_at'][:19]:<22} {cols}")
            print()

    elif args.command == "alerts":
        from .alerts import get_alert_state
        state = get_alert_state()
        if not state:
            print("  No alert state (first run).")
        else:
            print(f"\n  {'SOURCE':<22} {'STATUS':<12} {'UPDATED'}")
            print(f"  {'─'*22} {'─'*12} {'─'*24}")
            for sid, info in sorted(state.items()):
                print(f"  {sid:<22} {info.get('status',''):<12} {info.get('updated_at','')[:19]}")
            print()

    elif args.command == "check":
        from .health import check_all
        from .status import render_status_table
        results = check_all()
        match = [r for r in results if r.source_id == args.source_id]
        if match:
            print(render_status_table(match, use_color=not args.no_color))
        else:
            print(f"Source '{args.source_id}' not found.")
            sys.exit(1)

    elif args.command == "sources":
        from .health import load_manifest
        manifest = load_manifest()
        sources = manifest.get("sources", [])
        print(f"\n  {'ID':<24} {'GARDEN':<12} {'AUTHORITY':<24} {'CADENCE':<12}")
        print(f"  {'─'*24} {'─'*12} {'─'*24} {'─'*12}")
        for s in sources:
            status = s.get("status", "")
            dim = "  " if status == "not_installed" else ""
            print(f"{dim}  {s['id']:<24} {s.get('garden',''):<12} {s.get('authority',''):<24} {s.get('cadence',''):<12}")
        print(f"\n  {len(sources)} sources configured")
        print()

    elif args.command == "backup":
        from .backup import run_backup, print_backup_status
        print("R2 Backup")
        print("=" * 40)
        results = run_backup(garden=args.garden, dry_run=args.dry_run)
        if results:
            print_backup_status(results)
        else:
            print("  No r2_sync.sh scripts found.")

    elif args.command == "incidents":
        from .incidents import get_incidents
        if args.status == "all":
            incidents = get_incidents(garden=args.garden, source_id=args.source)
        else:
            incidents = get_incidents(status=args.status, garden=args.garden, source_id=args.source)
        if args.json:
            print(json.dumps(incidents, indent=2))
        else:
            if not incidents:
                print("  No incidents found.")
            else:
                print(f"\n  {'ID':<34} {'SOURCE':<22} {'GARDEN':<12} {'STATUS':<10} {'SEVERITY':<10} {'OPENED'}")
                print(f"  {'─'*34} {'─'*22} {'─'*12} {'─'*10} {'─'*10} {'─'*19}")
                for inc in incidents:
                    iid = inc.get("incident_id", "")
                    sid = inc.get("source_id", "")
                    g = inc.get("garden", "")
                    st = inc.get("status", "")
                    sev = inc.get("severity", "")
                    opened = inc.get("opened_at", "")[:19]
                    print(f"  {iid:<34} {sid:<22} {g:<12} {st:<10} {sev:<10} {opened}")
                print(f"\n  {len(incidents)} incidents")
                print()

    elif args.command == "events":
        from .events import get_events
        events = get_events(
            days=args.days,
            garden=args.garden,
            source_id=args.source,
            event_type=args.type,
        )
        if args.json:
            print(json.dumps(events, indent=2))
        else:
            if not events:
                print("  No events found.")
            else:
                print(f"\n  {'TIME':<22} {'TYPE':<24} {'SOURCE':<22} {'GARDEN':<12} {'SEVERITY':<10}")
                print(f"  {'─'*22} {'─'*24} {'─'*22} {'─'*12} {'─'*10}")
                for e in events:
                    at = e.get("at", "")[:19]
                    t = e.get("type", "")
                    sid = e.get("source_id", "")
                    g = e.get("garden", "")
                    sev = e.get("severity", "")
                    print(f"  {at:<22} {t:<24} {sid:<22} {g:<12} {sev:<10}")
                print(f"\n  {len(events)} events")
                print()

    elif args.command == "repos":
        from .repos import get_all_repos, format_repo_table
        repos = get_all_repos()
        if args.json:
            print(json.dumps(repos, indent=2, default=str))
        else:
            print(format_repo_table(repos))
            print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
