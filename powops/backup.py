"""R2 sync coordination.

Coordinates backup of raw garden data to Cloudflare R2.
Each garden's raw data is synced independently.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from .config import STATE_DIR


def _load_garden_paths() -> List[Path]:
    """Load garden paths from sources.yaml."""
    try:
        import yaml
        sources_yaml = Path(__file__).parent / "sources.yaml"
        with open(sources_yaml) as f:
            manifest = yaml.safe_load(f)
        gardens = manifest.get("gardens", {})
        paths = []
        for gid, gcfg in gardens.items():
            if gcfg.get("status") != "not_installed":
                p = Path(gcfg.get("path", ""))
                if p:
                    paths.append(p)
        return paths
    except Exception:
        # Fallback to known paths
        return [
            Path("/home/ubuntu/powpowpow"),
            Path("/home/ubuntu/repair"),
            Path("/home/ubuntu/powuk"),
            Path("/home/ubuntu/powstock"),
        ]


def find_r2_sync_scripts() -> List[Path]:
    """Find r2_sync.sh scripts in all gardens."""
    scripts = []
    for g in _load_garden_paths():
        script = g / "r2_sync.sh"
        if script.exists():
            scripts.append(script)
    return scripts


def run_backup(garden: Optional[str] = None, dry_run: bool = False) -> dict:
    """Run R2 backup for one or all gardens.

    Returns dict of garden -> {status, output}.
    """
    scripts = find_r2_sync_scripts()
    results = {}

    for script in scripts:
        garden_name = script.parent.name
        if garden and garden_name != garden:
            continue

        cmd = ["bash", str(script)]
        if dry_run:
            cmd.append("--dry-run")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300,
            )
            status = "ok" if result.returncode == 0 else "error"
            results[garden_name] = {
                "status": status,
                "output": result.stdout[-500:] if result.stdout else "",
                "error": result.stderr[-500:] if result.stderr else "",
            }
            from .events import record_event
            record_event(
                event_type="backup_verified" if status == "ok" else "backup_failed",
                garden=garden_name,
                severity="info" if status == "ok" else "warning",
                details={"output": result.stdout[-200:] if result.stdout else ""},
            )
        except subprocess.TimeoutExpired:
            results[garden_name] = {
                "status": "timeout",
                "error": "Sync timed out after 300s",
            }
            from .events import record_event
            record_event(
                event_type="backup_failed",
                garden=garden_name,
                severity="warning",
                details={"error": "timeout"},
            )
        except Exception as e:
            results[garden_name] = {
                "status": "error",
                "error": str(e),
            }
            from .events import record_event
            record_event(
                event_type="backup_failed",
                garden=garden_name,
                severity="warning",
                details={"error": str(e)},
            )

    return results


def print_backup_status(results: dict) -> None:
    """Print backup results."""
    for garden, info in results.items():
        status = info["status"]
        icon = {"ok": "ok", "error": "ERR", "timeout": "TIMEOUT"}.get(status, "?")
        print(f"  {garden:15s} {icon}")
        if info.get("error"):
            for line in info["error"].strip().split("\n")[-3:]:
                print(f"                  {line}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="R2 backup coordination")
    parser.add_argument("--garden", help="Sync specific garden only")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    args = parser.parse_args()

    print("R2 Backup Status")
    print("=" * 40)
    results = run_backup(garden=args.garden, dry_run=args.dry_run)
    if results:
        print_backup_status(results)
    else:
        print("  No r2_sync.sh scripts found in any garden.")
