# Project Name

Data science workspace. Code under `~/Developer/github-juandedios/<project>/`; working data under `~/DataWork/github-juandedios/<project>/`; credentials at `~/.config/<project>.env`.

## Prerequisites

`uv` installed (`brew install uv`). For the git step, an SSH key registered with GitHub. `apply.py` checks these on first run and prints a `fix:` line for anything missing.

## Configure

Everything the workspace needs to wire itself sits in `settings/`. Open the YAMLs, edit to fit the project, then run the reconciler.

| File | Sets |
|---|---|
| `settings/paths.yaml` | Credentials home, data home (cross-cutting) |
| `settings/python_env.yaml` | Required tools |
| `settings/git.yaml` | Branch, visibility, remote host, initial commit message |
| `settings/vscode.yaml` | Multi-root workspace folders |
| `settings/config.yaml` | Runtime logging level |

```bash
uv run python settings/apply.py
```

Idempotent. Project name = workspace folder name; rename the folder to change it.

After the first run, open `~/.config/<project>.env` and replace the placeholders with real values.

The reconciler also writes `<project>.code-workspace` at the repo root. Double-click it in Finder to open the multi-root VS Code workspace, or run `code <project>.code-workspace` from the terminal.

## Optional addons

None ship by default. The `settings/addons/` slot is reserved for opt-in capabilities a project adds when it needs them, each invoked as `uv run python <path>` from the project root.

Details: [settings/addons/README.md](settings/addons/README.md).

## Deeper

- [CLAUDE.md](CLAUDE.md) — operational runbook.
- [settings/apply.md](settings/apply.md) — reconciler companion (layout, YAML model, troubleshooting).
- [docs/project/conventions.md](docs/project/conventions.md) — naming, principles, layout (single source of truth).
