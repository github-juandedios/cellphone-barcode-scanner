"""
vscode.py - generate the multi-root <project>.code-workspace at the repo root.

Reads settings/vscode.yaml (folders) and settings/paths.yaml (datawork).
Substitutes {project} -> workspace folder name and {datawork} -> the path
from paths.yaml. Relative paths resolve against the .code-workspace's
directory (the project root). Refuses to overwrite an existing workspace
file with different content.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared import REPO_ROOT, PROJECT_NAME, load_yaml, datawork, log  # noqa: E402


def _resolve_path(spec: str, dh: Path) -> str:
    rendered = spec.format(project=PROJECT_NAME, datawork=str(dh))
    if rendered.startswith("~"):
        return str(Path(rendered).expanduser())
    return rendered


def run() -> None:
    cfg = load_yaml("vscode.yaml")
    folders = cfg.get("folders") or []
    if not folders:
        log("config", "vscode.yaml: folders missing or empty")
        sys.exit(1)

    dh = datawork()
    payload = {
        "folders": [
            {
                "name": entry["name"].format(project=PROJECT_NAME),
                "path": _resolve_path(entry["path"], dh),
            }
            for entry in folders
        ],
        "settings": cfg.get("settings") or {},
    }
    content = json.dumps(payload, indent=2) + "\n"

    workspace_path = REPO_ROOT / f"{PROJECT_NAME}.code-workspace"
    rel = workspace_path.relative_to(REPO_ROOT)

    if workspace_path.exists():
        if workspace_path.read_text() == content:
            log("workspace", f"already up to date: {rel}")
            log("open", f"code {rel}")
            return
        log("abort", f"{rel} exists with different content")
        log("abort", f"to regenerate, first remove it: rm {workspace_path}")
        sys.exit(1)

    workspace_path.write_text(content)
    log("workspace", f"wrote {rel}")
    log("open", f"code {rel}")


if __name__ == "__main__":
    run()
