"""
config_loader.py - load settings/config.yaml, resolve the working data root,
and read credentials.

Path convention: project name = workspace folder name. Working data lives
outside the repo at <datawork>/<project_name>/, with per-stage subdirs and a
reference/ sibling. Credentials live at <config_home>/<project_name>.env.

    <datawork>/<project_name>/<stage>/        # raw, extracted, ..., playground
    <datawork>/<project_name>/reference/
    <config_home>/<project_name>.env

Defaults: datawork=~/DataWork/github-juandedios, config_home=~/.config. Both
are declared in settings/paths.yaml; datawork.py creates the data root on
first run.

    from scripts.utils.config_loader import get_paths, load_credentials, load_script_config
    paths  = get_paths()                  # dict of pathlib.Path
    creds  = load_credentials()           # dict from the .env
    params = load_script_config(__file__) # companion <script>.yaml or {}
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

STAGES = ("raw", "extracted", "transformed", "enriched", "loaded", "playground")
REFERENCE_DIR_NAME = "reference"

DEFAULT_DATAWORK = "~/DataWork/github-juandedios"
DEFAULT_CONFIG_HOME = "~/.config"


def _repo_root(project_root: str = ".") -> Path:
    return Path(project_root).resolve()


def _project_name(project_root: str = ".") -> str:
    return _repo_root(project_root).name


def _load_paths(project_root: str = ".") -> dict[str, Any]:
    path = _repo_root(project_root) / "settings" / "paths.yaml"
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def _datawork(project_root: str = ".") -> Path:
    cfg = _load_paths(project_root)
    return Path(str(cfg.get("datawork", DEFAULT_DATAWORK))).expanduser()


def _config_home(project_root: str = ".") -> Path:
    cfg = _load_paths(project_root)
    return Path(str(cfg.get("config_home", DEFAULT_CONFIG_HOME))).expanduser()


def get_config(project_root: str = ".") -> dict[str, Any]:
    """Load settings/config.yaml. Raises FileNotFoundError / yaml.YAMLError / ValueError."""
    config_path = _repo_root(project_root) / "settings" / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    if not config:
        raise ValueError(f"Configuration file is empty: {config_path}")
    return config


def get_paths(project_root: str = ".") -> dict[str, Path]:
    """Return data_root + one entry per pipeline stage + reference."""
    name = _project_name(project_root)
    data_root = _datawork(project_root) / name
    if not data_root.exists():
        raise FileNotFoundError(
            f"Data directory does not exist: {data_root}\n"
            f"Run: uv run python settings/apply.py"
        )
    return {
        "data_root": data_root,
        **{stage: data_root / stage for stage in STAGES},
        "reference": data_root / REFERENCE_DIR_NAME,
    }


def load_credentials(project_root: str = ".") -> dict[str, str]:
    """Read KEY=VALUE pairs from <config_home>/<project_name>.env."""
    name = _project_name(project_root)
    env_file = _config_home(project_root) / f"{name}.env"
    creds: dict[str, str] = {}

    if not env_file.exists():
        logger.warning("credentials file not found: %s", env_file)
        return creds

    for line_num, line in enumerate(env_file.read_text().splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            logger.warning("skipping malformed line %d in %s: %s", line_num, env_file, line)
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        creds[key.strip()] = value

    return creds


def load_script_config(script_path: str) -> dict[str, Any]:
    """Load <script>.yaml beside the calling script. Returns {} if absent."""
    companion = Path(script_path).resolve().with_suffix(".yaml")
    if not companion.exists():
        return {}
    with open(companion) as f:
        return yaml.safe_load(f) or {}


if __name__ == "__main__":
    import sys

    try:
        print(f"[project] {_project_name()}")
        for key, path in get_paths().items():
            mark = "ok" if path.exists() else "MISSING"
            print(f"[path]    {key:11} {path}  ({mark})")
        creds = load_credentials()
        print(f"[creds]   {len(creds)} key(s) loaded")
    except Exception as exc:
        print(f"[error]   {exc}", file=sys.stderr)
        sys.exit(1)
