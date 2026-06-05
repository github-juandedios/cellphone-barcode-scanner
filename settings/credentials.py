"""
credentials.py - seed the project's .env credentials file.

Reads settings/paths.yaml (config_home). On first run, copies
settings/credentials.env.example -> <config_home>/<project>.env (chmod 600).
The .example source is kept as a reference for the keys the project expects.
On re-runs, the target is left as-is (no overwrite, no delete).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared import REPO_ROOT, PROJECT_NAME, config_home, log  # noqa: E402

ENV_EXAMPLE_PATH = REPO_ROOT / "settings" / "credentials.env.example"


def run() -> None:
    home = config_home()
    home.mkdir(parents=True, exist_ok=True)
    env_path = home / f"{PROJECT_NAME}.env"

    if env_path.exists():
        log("creds", f"exists, kept: {env_path}")
        return
    if not ENV_EXAMPLE_PATH.exists():
        log("creds", f"no target at {env_path} and no {ENV_EXAMPLE_PATH.name} to copy from")
        return

    env_path.write_text(ENV_EXAMPLE_PATH.read_text())
    try:
        env_path.chmod(0o600)
    except OSError:
        pass
    log("creds", f"wrote {env_path} from {ENV_EXAMPLE_PATH.name} (example kept for reference)")


if __name__ == "__main__":
    run()
