"""
git.py - verify git identity, detect the GitHub user, and wire origin.

Reads settings/git.yaml (remote_host, branch, visibility, commit_message).
Adopts an existing remote `git@<host>:<user>/<project>.git` if one exists,
otherwise creates it via `gh repo create`. Refuses to run on a workspace
that already has a `.git` directory pointing elsewhere.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared import REPO_ROOT, PROJECT_NAME, load_yaml, log  # noqa: E402


def _git(cmd: list[str], check: bool = False) -> tuple[int, str]:
    out = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    text = (out.stdout + out.stderr).strip()
    if check and out.returncode != 0:
        log("git", f"command failed: {' '.join(cmd)}")
        log("git", text)
        sys.exit(out.returncode)
    return out.returncode, text


def check_git_identity() -> bool:
    rc_n, name = _git(["git", "config", "--global", "user.name"])
    rc_e, email = _git(["git", "config", "--global", "user.email"])
    if rc_n == 0 and name and rc_e == 0 and email:
        log("identity", f"{name} <{email}>")
        return True
    log("identity", "global user.name or user.email not set")
    log("identity", 'fix: git config --global user.name "Your Name"')
    log("identity", '     git config --global user.email "you@example.com"')
    return False


def check_gh() -> bool:
    if not shutil.which("gh"):
        log("gh", "not installed. fix: brew install gh && gh auth login")
        return False
    rc, _ = _git(["gh", "auth", "status"])
    if rc != 0:
        log("gh", "not authenticated. fix: gh auth login")
        return False
    log("gh", "installed and authenticated")
    return True


def detect_github_user() -> str | None:
    """Parse 'Hi <user>!' from `ssh -T git@github.com`."""
    try:
        out = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-T", "git@github.com"],
            capture_output=True, text=True, timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    blob = (out.stdout + out.stderr).strip()
    match = re.match(r"^Hi ([^!]+)!", blob)
    return match.group(1) if match else None


def remote_exists(url: str) -> bool:
    rc, _ = _git(["git", "ls-remote", url, "HEAD"])
    return rc == 0


def adopt_remote(url: str, branch: str) -> int:
    _git(["git", "init"], check=True)
    _git(["git", "remote", "add", "origin", url], check=True)
    rc, out = _git(["git", "fetch", "--depth", "1", "origin", branch])
    if rc != 0:
        log("fetch", f"failed: {out}")
        log("fetch", f"verify the remote has a '{branch}' branch.")
        return 1
    _git(["git", "clean", "-fd"], check=True)
    rc, out = _git(["git", "checkout", "-b", branch, "FETCH_HEAD"])
    if rc != 0:
        log("checkout", f"failed: {out}")
        return 1
    _git(["git", "branch", "--set-upstream-to", f"origin/{branch}", branch])
    log("adopt", f"workspace now tracks origin/{branch} of {url}")
    return 0


def create_remote(user: str, repo: str, cfg: dict) -> int:
    if not check_gh():
        return 1
    branch = cfg.get("branch", "main")
    visibility = cfg.get("visibility", "private")
    commit_message = cfg.get("commit_message", "Initial commit from template")

    _git(["git", "init"], check=True)
    _git(["git", "add", "."], check=True)
    rc, out = _git(["git", "commit", "-m", commit_message])
    if rc != 0 and "nothing to commit" not in out:
        log("commit", f"commit failed: {out}")
        return 1
    log("commit", f"created initial commit: {commit_message!r}")

    _git(["git", "branch", "-M", branch], check=True)

    full_name = f"{user}/{repo}"
    rc, out = _git(
        ["gh", "repo", "create", full_name, f"--{visibility}", "--source", str(REPO_ROOT), "--push"]
    )
    if rc == 0:
        log("create", f"created {visibility} repo: {full_name}")
        log("push", "pushed initial branch")
        return 0
    log("create", f"gh failed: {out}")
    return 1


def run() -> None:
    cfg = load_yaml("git.yaml")

    if not check_git_identity():
        sys.exit(1)

    user = detect_github_user()
    if not user:
        log("ssh", "could not detect GitHub user via 'ssh -T git@github.com'")
        log("ssh", "fix: register an SSH key with GitHub, then retry")
        sys.exit(1)
    log("ssh", f"detected GitHub user: {user}")

    remote_host = cfg.get("remote_host", "github.com")
    branch = cfg.get("branch", "main")
    repo = REPO_ROOT.name
    url = f"git@{remote_host}:{user}/{repo}.git"

    if (REPO_ROOT / ".git").exists():
        rc, current_origin = _git(["git", "remote", "get-url", "origin"])
        if rc == 0 and current_origin == url:
            log("done", f"workspace already wired to {url}")
            return
        log("abort", ".git directory exists; workspace is not fresh.")
        if rc == 0:
            log("abort", f"origin = {current_origin}, expected = {url}")
        else:
            log("abort", "no origin remote configured.")
        log("abort", "this step only runs on a freshly-created workspace.")
        log("abort", "to start over: rm -rf .git, then re-run.")
        sys.exit(1)

    if remote_exists(url):
        log("remote", f"exists; replacing local content with {url}")
        rc = adopt_remote(url, branch)
    else:
        log("remote", f"does not exist; creating: {url}")
        rc = create_remote(user, repo, cfg)

    if rc != 0:
        log("git", "did not complete; re-run after fixing the cause above")
        sys.exit(rc)


if __name__ == "__main__":
    run()
