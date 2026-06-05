# CLAUDE.md

Operational runbook for Claude inside a project derived from this template. If the factory's `CLAUDE.md` is loaded instead, that one applies.

This file ships as scaffolding, not a contract. On the very first init, the workspace has no project-specific content — `scripts/<stage>/` slots are empty, `docs/project/business_rules.md.example` is a placeholder, `output/artifacts/` is empty, and every rule below is a starting point. The template distills patterns that worked in prior projects; the derived project keeps, adjusts, or drops any of them as it matures. `docs/project/conventions.md`, the `settings/*.yaml` files, and explicit user instructions all override this file. Re-read current state before answering rule or design questions — what worked days ago may be wrong today.

The template ships the project structure, six YAMLs declaring the setup state, and an orchestrator (`settings/apply.py`) that discovers every `settings/*.py` and runs each one's `run()` function in alphabetical order, skipping any file matched by `apply.yaml::skip` (default: `shared.py`, the library imported by every step, and `_[!_]*`, the underscore skip rule). Each step is also runnable standalone. Initialization runs as one command (`uv run python settings/apply.py`). No opt-in capabilities ship by default; the `settings/addons/` slot is reserved for ones a project adds later.

## Project model

Data science project template. `scripts/extract|transform|enrich|load|playground/` ship empty (`.gitkeep` only) — real scripts are added per project. Working data lives outside the repo at `~/DataWork/github-juandedios/<project>/` (created by `apply.py`; configurable via `settings/paths.yaml::datawork`). The remaining in-repo placeholders (`output/artifacts/`, `docs/project/business_rules.md.example`) ship empty; their content is gitignored or out-of-scope at runtime and the consumer may rename, fill, or delete them. Naming rules (filenames, folders, namespace symmetry, sidecars) live in `docs/project/conventions.md#naming`.

## Python environment

`uv` does everything Python: interpreter install, virtualenv, lock resolution. No pyenv, no pip/venv.

- `.python-version` pins 3.12; `uv` installs it on first sync.
- `pyproject.toml` declares runtime deps (`pyyaml`). No dev tooling ships by default.
- `uv sync` — one-shot installer; rerun after changes to `pyproject.toml` or `uv.lock`.
- `uv run <cmd>` — execute inside the managed `.venv`; implicit sync if stale.
- `uv add <pkg>` / `uv add --group dev <pkg>` — add a dep; updates lockfile.

No tests, lint, or formatter ship with the template. Add tools (e.g., `pytest`, `ruff`) only when a project explicitly needs them, after deciding it does.

## Git

What ships, so a new project does not re-derive it:

- `settings/git.yaml` — declares `remote_host`, `branch`, `visibility`, `commit_message`. Edit before the first `apply.py` run. Defaults: `github.com`, `main`, `private`, `"Initial commit from template"`.
- `settings/git.py` (run by `apply.py`) — verifies global git identity, detects the GitHub user via SSH, then adopts an existing `git@<host>:<user>/<project>.git` remote or creates one via `gh repo create`. Refuses to run if a `.git` directory already points elsewhere. Idempotent.

Day-to-day: commits land on the branch declared in `git.yaml` (default `main`); branching is a project decision, not a template default. Git history is the audit trail — no `_v2`, `_old`, `_backup` filenames (see `docs/project/conventions.md#naming`). Do not append a `Co-Authored-By: Claude …` trailer (or any Claude co-author trailer) to commit messages; the user's authorship is what gets recorded.

## Naming and versioning

Filename, folder, underscore, companion, and sidecar rules live in `docs/project/conventions.md#naming`. Git is the version system — no `_v2`, `_old`, `_backup` filenames; git history is the audit trail.

## Common commands

```bash
uv sync                                              # standalone resync after lock changes (uv run does it implicitly)
uv run python settings/apply.py                      # reconcile the workspace to the YAMLs (idempotent)
uv run python scripts/utils/config_loader.py         # verify paths and creds
uv run python scripts/extract/<script>.py            # always invoke from project root
```

Always `uv run python ...`, never bare `python ...`. Bare `python` is the system interpreter and will not find `pyyaml`.

## Workspace layout

Everything a project needs lives under the workspace folder. The folder tree answers "where does X belong?"; no lookup required. Rationale for the layout — namespace symmetry across surfaces, underscore-prefix skip rule, sidecar isolation — lives in `docs/project/conventions.md`.

| Path | Purpose | Tracked? |
|---|---|---|
| `scripts/` | All Python code | Yes |
| `settings/` | YAML setup state + the reconciler | Yes |
| `settings/addons/` | Opt-in capabilities | Yes |
| `output/log/` | Log files | Tracked (add `*.log` to a project gitignore if logs grow) |
| `output/playground/` | Ad-hoc exploration outputs | Tracked |
| `output/artifacts/` | Generated reports, exports, large artifacts | Structure yes, content no |
| `settings/credentials.env.example` | Tracked example; copied once by `apply.py`, kept | Yes |
| `<config_home>/<project>.env` | Real credentials (chmod 600); set by `apply.py` | Outside repo |
| `<datawork>/<project>/<stage>/` | Pipeline data (raw, extracted, transformed, enriched, loaded, playground) | Outside repo |
| `<datawork>/<project>/reference/` | Dictionaries, schemas, research | Outside repo |

Defaults: `<config_home>` is `~/.config`, `<datawork>` is `~/DataWork/github-juandedios`. Override via `settings/paths.yaml`.

Resolve paths through `config_loader` instead of hardcoding:

```python
from scripts.utils.config_loader import get_paths, load_credentials
paths = get_paths()                          # data_root, raw, extracted, transformed, enriched, loaded, playground, reference
creds = load_credentials()                   # dict from <config_home>/<name>.env
raw   = paths["raw"] / "source_01" / "data.csv"
```

`get_paths()` raises `FileNotFoundError` if `<datawork>/<project>/` is missing — signals setup was skipped.

## Configuration

Six YAMLs, two layers by purpose:

**Setup-time** — read by `settings/apply.py` and its per-step scripts:

- `settings/apply.yaml` — `skip` list that excludes files from auto-discovery (default: `shared.py`).
- `settings/paths.yaml` — `config_home`, `datawork` (cross-cutting; also read by runtime `config_loader.py`).
- `settings/python_env.yaml` — `required_tools`.
- `settings/git.yaml` — `remote_host`, `branch`, `visibility`, `commit_message`.
- `settings/vscode.yaml` — `folders` (multi-root workspace) and `settings` (workspace-level VS Code settings, e.g., `python.defaultInterpreterPath` pinning the uv-managed `.venv`).

**Runtime** — read by application scripts:

- `settings/config.yaml` — `logging.level` (used by `logger.py`).

Project name is **not** in any YAML — it is the workspace folder name, read from `Path.cwd()`.

**Per-script** — companion `<script>.yaml` beside the script. Loaded via `load_script_config(__file__)`; returns `{}` when absent. Always `.yaml`, never `.yml`.

Credentials never go in any YAML. They live in `<config_home>/<project_name>.env` (`KEY=VALUE`, `#` comments).

## Logging

Call `setup_logging()` once at the top of an entry-point script, then use the stdlib logger anywhere:

```python
from scripts.utils.logger import setup_logging
setup_logging()                          # console; level from config.yaml
setup_logging(log_file="extract.log")    # also writes output/log/extract.log

import logging
logger = logging.getLogger(__name__)
logger.info("started")
```

Level resolves as: explicit arg > `settings/config.yaml::logging.level` > `INFO`. Relative `log_file` paths land under `output/log/` (created on demand); absolute paths are honored as given. Modules use `logging.getLogger(__name__)` and never configure handlers or call `print`; `setup_logging()` is idempotent and is the single configuration point. No JSON/dictConfig is shipped — add one only if a project genuinely needs it.

## Conventions

Naming, principles, and layout rules all live in `docs/project/conventions.md` (single source of truth, with `#naming`, `#principles`, `#layout` sections). Re-read before answering rule or design questions; this doc overrides the file you are reading now. Surface conflicts with the settings YAMLs instead of silently picking one.

Daily-work defaults:

- Scripts go under `scripts/<stage>/`, never the repo root. If a location is unclear, ask.
- Script outputs go under `output/`: logs to `output/log/`, exploration to `output/playground/`, large/generated artifacts to `output/artifacts/`.
- Catalog generators write the generated catalog alongside the source data, not into `output/`.
- No emojis. Executive-professional tone in Spanish for user-facing reports; technical English in code is fine.
- Every conclusion and artifact must be traceable to its inputs and the script that produced it. Avoid superlatives ("fully optimized", "guaranteed") and absolute completion language ("completed", "finalized") in reports.
- Add nothing the user did not ask for. Propose first, act after explicit approval. Default to less.

## Documentation map

- `settings/apply.md` — directory layout, YAML model, reconciler behavior (companion to `apply.py`)
- `docs/project/conventions.md` — naming rules, design principles, layout (single source of truth; sections `#naming`, `#principles`, `#layout`)
- `docs/project/business_rules.md.example` — placeholder for per-project business rules; consumer copies to `docs/project/business_rules.md` when filled
- `settings/addons/README.md` — addon catalog (none shipped; slot reserved for future opt-in capabilities)

First-run setup is driven by `README.md` and `settings/apply.py`; missing prerequisites (uv, SSH key, `gh`) are reported by `apply.py` with a `fix:` line. This workspace is self-contained — it carries no link back to the template factory it was generated from.
