"""
logger.py - standardized logging for the workspace.

Call setup_logging() ONCE at the top of an entry-point script, then use the
stdlib logger anywhere:

    from scripts.utils.logger import setup_logging
    setup_logging()                          # console; level from config.yaml
    setup_logging(log_file="extract.log")    # also writes output/log/extract.log

    import logging
    logger = logging.getLogger(__name__)
    logger.info("started")

Level resolves as: explicit arg > settings/config.yaml::logging.level > INFO.
Relative log_file paths land under output/log/ (created on demand); absolute
paths are used as given. setup_logging() is idempotent: once the root logger
has handlers, calling it again is a no-op.
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_LOG_DIR = REPO_ROOT / "output" / "log"
CONFIG_PATH = REPO_ROOT / "settings" / "config.yaml"

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LEVEL = "INFO"


def _level_from_config() -> str:
    if not CONFIG_PATH.exists():
        return DEFAULT_LEVEL
    try:
        cfg = yaml.safe_load(CONFIG_PATH.read_text()) or {}
    except yaml.YAMLError:
        return DEFAULT_LEVEL
    return str((cfg.get("logging") or {}).get("level", DEFAULT_LEVEL)).upper()


def _resolve_log_path(log_file: str | Path) -> Path:
    path = Path(log_file)
    if not path.is_absolute():
        path = OUTPUT_LOG_DIR / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def setup_logging(level: str | int | None = None, log_file: str | Path | None = None) -> None:
    """Configure the root logger once. Call at the entry point, before logging."""
    root = logging.getLogger()
    if root.handlers:
        return

    if level is None:
        level = _level_from_config()
    if isinstance(level, str):
        level = level.upper()
    root.setLevel(level)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    if log_file:
        file_handler = logging.FileHandler(_resolve_log_path(log_file), encoding="utf-8")
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
