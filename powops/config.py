"""POWOps configuration.

Centralizes all paths. No hard-coded usernames or home directories.

Environment variables:
    POWOPS_STATE_DIR  — runtime state (default: ~/.powops or /var/lib/powops)
    POW_ROOT          — POW system root (default: /srv/pow)
"""

import os
from pathlib import Path


def _default_state_dir() -> Path:
    """Determine default state directory."""
    # Check env var first
    env = os.environ.get("POWOPS_STATE_DIR")
    if env:
        return Path(env)
    # User-level default
    return Path.home() / ".powops"


STATE_DIR = _default_state_dir()
HISTORY_DIR = STATE_DIR / "history"
VOLUME_DIR = STATE_DIR / "volume"
SCHEMA_DIR = STATE_DIR / "schemas"
ALERT_STATE_FILE = STATE_DIR / "alerts.json"
HEALTH_DIR = STATE_DIR / "health"


def ensure_dirs():
    """Create all state directories."""
    for d in (STATE_DIR, HISTORY_DIR, VOLUME_DIR, SCHEMA_DIR, HEALTH_DIR):
        d.mkdir(parents=True, exist_ok=True)
