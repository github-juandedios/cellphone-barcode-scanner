# apply.md

Companion to `apply.py`. Describes the orchestrator only. Each step's behavior is documented in its own `<step>.py` docstring, and each step's configuration is the literal contents of `<step>.yaml`.

## How it works

`apply.py` discovers steps with `Path("settings").glob("*.py")`, excludes any name matching `apply.yaml::skip` (default: `shared.py`, `_[!_]*`) and `apply.py` itself, then sorts the remainder alphabetically. Each discovered file must expose a callable `run()`. Steps run in order; a step raising `SystemExit(1)` stops the run.

Each step is also runnable standalone:

```bash
uv run python settings/<step>.py
```

The orchestrator is idempotent. Re-run any time a YAML changes:

```bash
uv run python settings/apply.py
```

When only one YAML moved, running that step standalone is equivalent.

## Adding a step

1. Create `settings/<name>.py` with a `run()` function. Import what you need from `shared.py`. Raise `SystemExit(1)` on critical failure.
2. If the step has configuration, add `settings/<name>.yaml` and load it via `shared.load_yaml("<name>.yaml")`.
3. `apply.py` picks it up on the next invocation.

Order matters only when one step depends on another. The current set sorts naturally; if a future step is order-sensitive, prefix with a digit (e.g., `00_bootstrap.py`).

To hide a Python file from discovery (libraries, helpers), add a pattern to `apply.yaml::skip`. Work-in-progress drafts are already hidden by the underscore-prefix skip rule; see `docs/project/conventions.md#naming` for what `_<name>` means.
