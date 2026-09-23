"""GitHub repository status — commit, CI, and deployment visibility.

Checks the latest commit, CI status, and test results for each POW
repository using the GitHub API (via `gh` CLI).

Requires: `gh` CLI authenticated, or GITHUB_TOKEN env var.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from typing import Optional


# All POW repositories
REPOS = {
    "powops": "prx0r/powops",
    "powk": "prx0r/powk",
    "powpowpow": "prx0r/powpowpow",
    "powuk": "prx0r/powuk",
    "powstock": "prx0r/powstock",
    "repair": "prx0r/repair",
    "powproducts": "prx0r/powproducts",
    "powrobots": "prx0r/powrobots",
    "powphysical": "prx0r/powphysical",
}


def _run_gh(args: list[str], timeout: int = 15) -> Optional[str]:
    """Run a gh CLI command and return stdout, or None on failure."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def _parse_json(text: str) -> Optional[dict | list]:
    """Parse JSON text, returning None on failure."""
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def get_repo_info(full_name: str) -> dict:
    """Get latest commit info for a repository.

    Returns:
        {
            "full_name": "prx0r/powops",
            "last_commit": {...},
            "ci_status": "success" | "failure" | "pending" | "none" | "unknown",
            "default_branch": "main",
        }
    """
    info = {
        "full_name": full_name,
        "last_commit": None,
        "ci_status": "unknown",
        "default_branch": "main",
    }

    # Get latest commit
    raw = _run_gh([
        "api", f"repos/{full_name}/commits",
        "--jq", ".[0] | {sha: .sha, message: .commit.message, author: .commit.author.name, date: .commit.author.date, url: .html_url}",
    ])
    if raw:
        commit = _parse_json(raw)
        if commit:
            info["last_commit"] = commit

    # Get default branch
    raw = _run_gh(["api", f"repos/{full_name}", "--jq", ".default_branch"])
    if raw:
        info["default_branch"] = raw.strip().strip('"')

    # Get latest CI status (check runs on default branch)
    branch = info["default_branch"]
    raw = _run_gh([
        "api", f"repos/{full_name}/commits/{branch}/check-runs",
        "--jq", ".check_runs[:3] | [.[] | {name: .name, status: .status, conclusion: .conclusion}]",
    ])
    if raw:
        checks = _parse_json(raw)
        if checks and isinstance(checks, list):
            # Determine overall status from check runs
            conclusions = [c.get("conclusion", "") for c in checks]
            statuses = [c.get("status", "") for c in checks]
            if any(c == "failure" for c in conclusions):
                info["ci_status"] = "failure"
            elif any(c == "success" for c in conclusions):
                info["ci_status"] = "success"
            elif any(s == "in_progress" for s in statuses):
                info["ci_status"] = "pending"
            elif all(s == "completed" for s in statuses):
                info["ci_status"] = "success" if all(c in ("success", "skipped") for c in conclusions) else "failure"
            else:
                info["ci_status"] = "none"
        else:
            info["ci_status"] = "none"
    else:
        # Fallback: check combined status
        raw = _run_gh([
            "api", f"repos/{full_name}/commits/{branch}/status",
            "--jq", ".state",
        ])
        if raw:
            info["ci_status"] = raw.strip().strip('"')
        else:
            info["ci_status"] = "unknown"

    return info


def get_all_repos() -> dict[str, dict]:
    """Get status for all POW repositories.

    Returns dict of repo_name -> info dict.
    """
    results = {}
    for name, full_name in REPOS.items():
        results[name] = get_repo_info(full_name)
    return results


def get_repo_status(repo_name: str) -> Optional[dict]:
    """Get status for a single repo by short name."""
    full_name = REPOS.get(repo_name)
    if not full_name:
        return None
    return get_repo_info(full_name)


def format_repo_table(repos: dict[str, dict]) -> str:
    """Format repo status as a readable table."""
    lines = []
    lines.append(f"  {'REPO':<16} {'COMMIT':<10} {'MESSAGE':<40} {'CI':<10} {'DATE'}")
    lines.append(f"  {'─'*16} {'─'*10} {'─'*40} {'─'*10} {'─'*19}")

    for name, info in sorted(repos.items()):
        commit = info.get("last_commit") or {}
        sha = (commit.get("sha", "") or "")[:8]
        msg = (commit.get("message", "") or "")[:38]
        date = (commit.get("date", "") or "")[:19]
        ci = info.get("ci_status", "unknown")
        lines.append(f"  {name:<16} {sha:<10} {msg:<40} {ci:<10} {date}")

    return "\n".join(lines)
