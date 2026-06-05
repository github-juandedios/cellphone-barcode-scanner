"""
verify.py - sanity-check that config_loader can resolve paths and credentials.

Imports scripts/utils/config_loader and calls get_paths() and
load_credentials(). Warnings (e.g., empty credentials file) do not abort;
import or resolution failures do.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared import REPO_ROOT, log  # noqa: E402


def run() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from scripts.utils.config_loader import get_paths, load_credentials
    except ImportError as e:
        log("verify", f"could not import config_loader: {e}")
        sys.exit(1)
    try:
        paths = get_paths(str(REPO_ROOT))
        creds = load_credentials(str(REPO_ROOT))
    except Exception as e:
        log("verify", f"config_loader raised: {e}")
        sys.exit(1)
    log("verify", f"data root resolves to {paths['data_root']}")
    log("verify", f"credentials loaded: {len(creds)} keys")


if __name__ == "__main__":
    run()
