## playYT Project Overview

playYT is a highly customizable YouTube client written in Python 3. It focuses on modularity, extensibility, and portability across generic operating systems. This document is the project-level plan and technical outline. User-facing documentation lives in README.md. License details are in LICENSE.md.

### Goals
- Offer a clean, scriptable YouTube client with optional modules for features like search, playback, downloading, playlists, history, and integrations.
- Keep the core small; enable features via modules/plugins.
- Run on a generic OS environment (Windows, macOS, Linux) with Python 3.
- Provide an Ansible playbook for simple remote deployment.

### Non-Goals (Initial)
- Building a full GUI out of the gate (CLI first; GUI may be added via a module later).
- Bundling proprietary assets or shipping platform-specific installers in v0.x.

---

## Architecture

### Components
- Core: command dispatch, configuration, logging, module discovery, and lifecycle management.
- Module system: loadable Python modules that register capabilities (commands, hooks, services).
- IO/Adapters: optional adapters to external tools (e.g., yt-dlp/ffmpeg) exposed via modules.

### Module System (Concept)
- Modules live under src/playyt/modules/ or an equivalent package path.
- Each module exposes a `register()` function that returns metadata and handlers (e.g., commands, hooks).
- Core discovers modules by scanning an enabled list in a config file (YAML/TOML) and importing them dynamically using `importlib`.
- Modules should be self-contained and avoid side effects upon import; initialization happens in `register()`.

Example module shape (illustrative):
- module_name/
  - __init__.py (defines register())
  - commands.py (CLI commands)
  - services.py (reusable services)
  - config_schema.(py|json|yaml)

### Configuration
- Global config file (e.g., config.yaml) defines:
  - enabled_modules: [list]
  - module-specific settings (namespaced)
  - runtime options (cache dir, download dir, etc.)
- Environment variables may override select settings.

### Logging
- Use Python logging with structured output where helpful.
- Verbosity flags in the CLI (e.g., -v, -q).

---

## Technology
- Language: Python 3.x
- OS: Generic (Windows/macOS/Linux)
- Packaging: start with venv + pip; consider Poetry later
- Dependencies: kept minimal in core; modules can declare their own

---

## Directory Layout (proposed)
- src/playyt/ (core package)
- src/playyt/modules/ (first-party modules)
- tests/ (unit/integration tests)
- scripts/ (helper scripts)
- config/ (sample configs)
- ansible/ (deployment playbook, inventory)

This is a proposal; evolve as needed during implementation.

---

## Development Workflow
- Version control: Git
- Branching: trunk-based or GitHub Flow
  - main: always releasable
  - feature/*: short-lived branches merged via PR
- Conventional Commits recommended
- Code style: Black + isort + Ruff (optional, to be added)
- Testing: pytest

Suggested commands:
- python -m venv .venv && .venv/bin/pip install -U pip
- pip install -r requirements.txt (if present)
- pytest

---

## Versioning & Releases
- Semantic Versioning (SemVer): MAJOR.MINOR.PATCH
- Changelog derived from commits or PR titles

---

## Deployment (Ansible)
- Ansible playbook is provided under ansible/playbook.yml
- Inventory sample at ansible/inventory.ini
- Variables:
  - repo_url: Git URL to this repository (https/ssh)
  - app_dir: Remote path for deployment (e.g., /opt/playyt)
  - branch: Git branch to deploy (e.g., main)
  - venv_path: Virtual environment path (e.g., /opt/playyt/.venv)

High-level steps in playbook:
1) Ensure dependencies (git, python3) exist (best-effort, OS generic)
2) Clone/Update repo at app_dir
3) Create Python venv and install requirements if present

Notes:
- The playbook is intentionally generic; adapt to your OS and service manager as needed.
- For production use, add service management (systemd, supervisord), secrets handling, and proper logging.

---

## Roadmap (MVP → v0.1)
- Core CLI bootstrap and config loading
- Module loader + example hello-world module
- Basic YouTube search/download via yt-dlp module (optional)
- Tests and CI (lint + unit tests)
- Packaging basics and first release

---

## Contributing
- Open issues for discussion
- Small, focused PRs
- Ensure tests pass locally

---

## License
- CC BY-NC 4.0. See LICENSE.md for details.

