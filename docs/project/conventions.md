# Conventions

Source of truth for naming, principles, and layout in projects derived from this template. `README.md` and `CLAUDE.md` link here; they do not restate the rules. Re-read this file before answering rule or design questions — what worked two days ago may now be wrong.

## Naming

### Standard rules

These match mainstream Python and Git/GitHub practice.

| Kind | Rule | Example |
|---|---|---|
| Python source | `snake_case.py` | `apply.py`, `config_loader.py`, `logger.py` |
| Project-wide docs | lowercase, `snake_case.md` | `conventions.md`, `apply.md` |
| Repository-special docs | uppercase form (Git/GitHub treat the name specially) | `README.md`, `CLAUDE.md` |
| YAML | always `.yaml`, never `.yml` | `paths.yaml`, `apply.yaml` |
| Consumer stub files | `<name>.<ext>.example` (consumer copies, fills, drops the `.example` suffix) | `credentials.env.example`, `business_rules.md.example` |
| Credentials env | `<project>.env` under `<config_home>` | `~/.config/<project>.env` |
| Logs | `<script>.log` under `output/log/` | `output/log/apply.log` |
| No version suffixes | git history is the audit trail; no `_v2`, `_old`, `_backup` in filenames | — |

### Project-specific rules

These are project conventions, not industry standards. Read them: they change how scripts and processes behave.

**Project identity** — three surfaces carry the same identifier verbatim:

- Code: `~/Developer/github-juandedios/<project>/`
- Working data: `~/DataWork/github-juandedios/<project>/`
- GitHub: `github.com/github-juandedios/<project>`

The local layout mirrors the GitHub URL namespace: `~/Developer/github-juandedios/<repo>` ↔ `github.com/github-juandedios/<repo>`. Future identities (a second GitHub account, a work org) slot in as sibling directories under `~/Developer/` and `~/DataWork/`. If a project wires a cloud-sync target, name that target's root folder `<project>` to keep symmetry; the template ships no cloud-sync integration.

The project name is the workspace folder name, read from `Path.cwd()`. It is never declared in any YAML.

**Underscore prefix = skip marker.** A name starting with a single underscore (`_<name>`, where the second character is not another underscore) is:

- gitignored, and
- skipped by processes that walk the directory (currently `apply.py`; any future walker must honor the same rule).

Applies to any file or folder type — `.py`, `.csv`, `.pdf`, `.json`, directories. Use case: rename `notes.md` → `_notes.md` to exclude it temporarily; rename back to include it. Underscore-prefixed items sort to the top of `ls`, so all skipped items cluster visually.

Python's dunder convention (`__init__.py`, `__main__.py`, `__pycache__/`) starts with two underscores and is unrelated. The gitignore and skip patterns use `_[!_]*`, which matches single-underscore prefix only.

**Companion files** — share the basename and sit next to each other:

- `apply.py` and `apply.md` (documentation companion)
- `apply.py` and `apply.yaml` (configuration companion)

Configuration companions are loaded with `load_script_config(__file__)`; the loader returns `{}` when absent.

**Sidecar files outside the repo** — anything the workspace writes outside its own folder carries the project name in its path so removal is a single targeted `rm` and provenance is unambiguous. No global namespaces, no shared caches across projects.

| Sidecar | Path |
|---|---|
| Credentials env | `~/.config/<project>.env` |

Working data follows the same identity rule: `~/DataWork/github-juandedios/<project>/<stage>/`.

## Principles

How a derived project is expected to work. These are stances; the concrete rules they lean on live in [Naming](#naming) and [Layout](#layout).

### Evolution

- This project starts from a distillation of what worked elsewhere, not a fixed contract. Treat these principles as starting points; diverge when the project requires it.
- Paradigm shifts and refactors are the normal mode of progress, not exceptions. Expect rewrites of structure, not only tweaks.
- Re-read current state (this file, the setting YAMLs, the code) before deciding. What worked two days ago may now be wrong.

### Settings as YAML, code as reconciler

- Setup state lives in YAML; the only setup code is the reconciler (`apply.py`). It discovers every `settings/*.py`, runs each `run()` alphabetically, and is idempotent — re-run any time a YAML changes.
- Two layers by purpose: setup-time YAMLs (`apply.yaml`, `paths.yaml`, `python_env.yaml`, `git.yaml`, `vscode.yaml`) drive `apply.py`; the runtime YAML (`config.yaml`) is read by application scripts.
- Per-script parameters live in a `<script>.yaml` companion beside the script, loaded via `load_script_config(__file__)`.
- The project name is the workspace folder name, read from `Path.cwd()`. It is never declared in any YAML.

### Writing scripts

- One canonical scenario per script. No flags, no `--force`/`--skip` escape hatches. On failure, print the cause, print the fix, stop.
- Always `uv run python <script>`, never bare `python` — bare `python` is the system interpreter and misses the managed `.venv`.

### Naming stances

The rules live in [Naming](#naming). The anchor stance: names announce role, not implementation. `apply.py` not `reset_config.py` (reset implies wipe; the script reconciles); an opt-in slot like `settings/addons/` is named for the capability, not whatever payload fills it.

### Identity and sidecar isolation

- The workspace folder name, working data folder name, and GitHub repo name match exactly. A project is recognizable from any surface (Finder, GitHub URL) without translation.
- Sidecar state belongs to one project. Anything the workspace writes outside its own folder carries the project name in its path so removal is a single targeted `rm` and provenance is unambiguous. No global namespaces, no shared caches across projects.

### Versioning workflow

- Git is the version system; git history is the audit trail. Use commits and branches, not filename suffixes (`_v2`/`_old`/`_backup`), to track change.
- Retired-but-locally-useful code goes to `deprecated/` (tracked structure via `.gitkeep`, contents gitignored). The commit that moves a file there should state which file and why.

## Layout

Where things live. Working files inside the repo, data and credentials outside. A script's destination is derived from its source location (folder mirror); no per-script exceptions.

### In-repo

- `scripts/` — all Python code, organized by pipeline stage (`extract/`, `transform/`, `enrich/`, `load/`, `playground/`).
- `settings/` — YAML setup state and the reconciler. Per-step `.py` files are auto-discovered by `apply.py`.
- `output/` — script outputs, mostly gitignored. **Folder mirror**: a script in `scripts/<role>/` writes to `output/<role>/`. Subfolders are created on demand.
  - `output/log/` — operational telemetry. Log file basename mirrors the script. The one cross-cutting exception to the folder-mirror rule.
  - `output/playground/` — ad-hoc exploration outputs from `scripts/playground/`.
  - `output/artifacts/` — reserved for promoted scripts' deliverables. Do not write here until a script graduates out of `scripts/playground/` with stable end-state deliverables.
- `docs/` — documentation. `docs/project/` holds project-level meta-docs (conventions, business rules). Future categories slot in as siblings (`docs/api/`, `docs/architecture/`, etc.).
- `deprecated/` — retired code kept locally for reference. Tracked structure via `.gitkeep`; contents gitignored.

### Outside the repo

- `<datawork>/<project>/<stage>/` — pipeline data (`raw`, `extracted`, `transformed`, `enriched`, `loaded`, `playground`). Created by `apply.py` from `paths.yaml::datawork` (default `~/DataWork/github-juandedios`).
- `<datawork>/<project>/reference/` — dictionaries, schemas, research.
- `<config_home>/<project>.env` — real credentials (chmod 600). Default `<config_home>` is `~/.config`.

The folder-mirror rule applies to in-repo `output/`, not to working data under `<datawork>/`.
