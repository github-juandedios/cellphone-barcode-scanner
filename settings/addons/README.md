# Addons

Opt-in scripts that layer capabilities on top of the bare workspace. Grouped by scope under `settings/addons/<group>/`; the canonical entry of each scope is `install.py`. Other files in the same directory are payloads invoked by that scope. Optional companion `<name>.yaml` for parameters. No orchestrator.

Each addon ships a single canonical scenario, no flags. If a project needs a custom path, run the underlying tools directly — the addon does not expose toggles.

Core setup (python env, git wiring, vscode workspace) is **not** an addon. It runs as `settings/apply.py`, driven by the YAMLs under `settings/`. Addons are opt-in capabilities that sit beside the core.

## Available

None currently shipped. The `settings/addons/` slot is reserved for opt-in capabilities a project adds when it needs them.

## Authoring a new addon

- Pick a scope: `settings/addons/<group>/`. Canonical entry is `install.py`. Workspace root is `Path(__file__).resolve().parents[N]` (count the levels from the script up; for `settings/addons/<group>/install.py` that is `parents[3]`).
- Payloads live alongside `install.py`. Each can be invoked directly; each handles its own preconditions.
- Print structured `[step] message` lines via a `log()` helper.
- Single happy path. No flags unless a real, current need forces one. On failure, print the cause and the fix command and stop — do not add `--force`/`--skip`.
- Be idempotent; document re-run behavior in the docstring.
- Optional companion `<name>.yaml` read with `scripts.utils.config_loader.load_script_config(__file__)`.
- Name the slot after the capability, not the payload, so the payload can swap without renaming.
- Add an entry under "Available" in this README.
