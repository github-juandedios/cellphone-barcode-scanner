"""
shared.py - common utilities for the settings/ step scripts.

Imported by apply.py and by each per-step script (python_env.py, credentials.py,
datawork.py, git.py, vscode.py, verify.py). Each step file does:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from shared import REPO_ROOT, PROJECT_NAME, log, load_yaml, load_paths
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECT_NAME = REPO_ROOT.name
SETTINGS_DIR = REPO_ROOT / "settings"


def log(step: str, msg: str) -> None:
    print(f"[{step}] {msg}")


def load_yaml(name: str, required: bool = True) -> dict:
    """Load a YAML from settings/. Exit 1 if required and missing."""
    path = SETTINGS_DIR / name
    if not path.exists():
        if required:
            log("config", f"missing: settings/{name}")
            sys.exit(1)
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_paths() -> dict:
    """Cross-cutting paths declared in settings/paths.yaml."""
    return load_yaml("paths.yaml")


def config_home() -> Path:
    return Path(str(load_paths().get("config_home", "~/.config"))).expanduser()


def datawork() -> Path:
    return Path(str(load_paths().get("datawork", "~/DataWork/github-juandedios"))).expanduser()
