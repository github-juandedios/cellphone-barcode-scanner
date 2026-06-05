"""
datawork.py - create the working data root for the project.

Reads settings/paths.yaml (datawork). Creates one subdir per pipeline stage
(the canonical list lives in scripts/utils/config_loader.STAGES) plus a
reference/ sibling under <datawork>/<project>/, on first run, dropping an
`_outside_git_scope` note in each newly created subdir. Idempotent: missing
subdirs are added, existing content is never touched.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared import PROJECT_NAME, REPO_ROOT, datawork, log  # noqa: E402

MARKER_NAME = "_outside_git_scope"
MARKER_NOTE = (
    "This folder is outside the repository (it lives under ~/DataWork/), so its\n"
    "contents are not tracked by git.\n\n"
    "To bring working data under version control, point `datawork` in\n"
    "settings/paths.yaml to a location inside the repo, then re-run\n"
    "settings/apply.py.\n"
)


def run() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from scripts.utils.config_loader import STAGES, REFERENCE_DIR_NAME  # noqa: E402

    project_root = datawork() / PROJECT_NAME

    created: list[str] = []
    for sub in (*STAGES, REFERENCE_DIR_NAME):
        target = project_root / sub
        if not target.exists():
            created.append(sub)
            target.mkdir(parents=True, exist_ok=True)
            (target / MARKER_NAME).write_text(MARKER_NOTE)
        else:
            target.mkdir(parents=True, exist_ok=True)

    if created:
        log("data", f"created {project_root} (subdirs: {', '.join(created)})")
    else:
        log("data", f"exists, kept: {project_root}")


if __name__ == "__main__":
    run()
