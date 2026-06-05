"""
apply.py - discover every step in settings/ and run it.

A step is any `settings/*.py` file whose name does not match a pattern in
`settings/apply.yaml::skip`. Steps run in alphabetical order. apply.py
never runs itself.

Each step must expose a callable named `run()`. Each step is also runnable
standalone:
    uv run python settings/<step>.py

Adding a new step: drop a `<name>.py` in `settings/` with a `run()`
function. apply.py picks it up on the next invocation. To hide a Python
file from discovery (libraries, stubs), prefix its name with `_`.

Usage:
    uv run python settings/apply.py
"""

from __future__ import annotations

import fnmatch
import importlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import PROJECT_NAME, load_yaml, log  # noqa: E402

SETTINGS_DIR = Path(__file__).resolve().parent
SELF = Path(__file__).resolve()
NAME_PATTERN = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]*")


def discover_steps() -> list[Path]:
    cfg = load_yaml("apply.yaml", required=False)
    skip_patterns: list[str] = cfg.get("skip", []) or []

    def is_step(p: Path) -> bool:
        if p.resolve() == SELF:
            return False
        return not any(fnmatch.fnmatch(p.name, pat) for pat in skip_patterns)

    return sorted(p for p in SETTINGS_DIR.glob("*.py") if is_step(p))


def main() -> int:
    print("=" * 60)
    print(f"apply - reconciling workspace '{PROJECT_NAME}'")
    print("=" * 60)

    if not NAME_PATTERN.fullmatch(PROJECT_NAME):
        log("init", f"workspace folder '{PROJECT_NAME}' is not a valid project name")
        log("init", "fix: rename to letters/digits/'-'/'_' (must start alphanumeric)")
        return 1

    step_files = discover_steps()
    log("apply", f"discovered {len(step_files)} step(s): {', '.join(p.stem for p in step_files)}")

    for i, step_path in enumerate(step_files):
        if i > 0:
            print("-" * 60)
        module = importlib.import_module(step_path.stem)
        if not hasattr(module, "run") or not callable(module.run):
            log("apply", f"skipping {step_path.name}: no run() function")
            continue
        module.run()

    print("=" * 60)
    print(f"[done] project '{PROJECT_NAME}' reconciled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
