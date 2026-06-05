"""
python_env.py - verify the Python toolchain and ~/.config exist.

Reads settings/python_env.yaml (required_tools) and settings/paths.yaml
(config_home). Runs each declared tool check plus .python-version, .venv,
and config_home checks. Critical failures exit 1 with a fix: line.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared import REPO_ROOT, load_yaml, config_home, log  # noqa: E402


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    fix: str | None = None
    critical: bool = False


def _run(cmd: list[str], timeout: int = 5) -> tuple[int, str]:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return out.returncode, (out.stdout + out.stderr).strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 127, ""


def _check_homebrew() -> Check:
    if shutil.which("brew"):
        _, ver = _run(["brew", "--version"])
        first = ver.splitlines()[0] if ver else "brew"
        return Check("homebrew", True, first)
    return Check(
        "homebrew", False, "not installed",
        fix='/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        critical=True,
    )


def _check_uv() -> Check:
    if shutil.which("uv"):
        _, ver = _run(["uv", "--version"])
        return Check("uv", True, ver or "installed")
    return Check("uv", False, "not installed", fix="brew install uv", critical=True)


def check_tool(name: str) -> Check:
    if name == "homebrew":
        return _check_homebrew()
    if name == "uv":
        return _check_uv()
    if shutil.which(name):
        return Check(name, True, "installed")
    return Check(name, False, "not installed", fix=f"brew install {name}", critical=True)


def check_python_version() -> Check:
    pv_file = REPO_ROOT / ".python-version"
    if not pv_file.exists():
        return Check("python-version", False, ".python-version missing in repo")
    target = pv_file.read_text().strip()
    rc, _ = _run(["uv", "python", "find", target])
    if rc == 0:
        return Check("python-version", True, f"{target} available")
    return Check("python-version", True,
                 f"{target} not yet installed (uv sync will fetch it)")


def check_venv() -> Check:
    venv = REPO_ROOT / ".venv"
    if venv.exists():
        return Check("venv", True, str(venv.relative_to(REPO_ROOT)))
    return Check("venv", False, ".venv missing", fix="uv sync")


def check_config_home(path: Path) -> Check:
    if path.exists():
        return Check("config-home", True, str(path))
    return Check("config-home", False, "missing",
                 fix=f"mkdir -p {path} && chmod 700 {path}")


def run() -> None:
    cfg = load_yaml("python_env.yaml")
    tools = cfg.get("required_tools", []) or []

    checks: list[Check] = [check_tool(t) for t in tools]
    checks.append(check_python_version())
    checks.append(check_venv())
    checks.append(check_config_home(config_home()))

    print("\nEnvironment check")
    print("-" * 60)
    for c in checks:
        mark = "ok " if c.ok else ("ERR" if c.critical else "warn")
        print(f"  [{mark}] {c.name:18} {c.detail}")
        if not c.ok and c.fix:
            print(f"         fix: {c.fix}")
    print("-" * 60)

    if any((not c.ok) and c.critical for c in checks):
        print("\nCritical prerequisites missing. Fix the items above and re-run.")
        sys.exit(1)


if __name__ == "__main__":
    run()
