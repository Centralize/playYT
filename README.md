# playYT

A highly customizable YouTube client in Python 3 with a modular architecture.

This README is for quickstart and user-facing documentation. For the project planning and technical outline, see PROJECT.md. The license is in LICENSE.md (CC BY-NC 4.0).

## Quick Start

- Requires Python 3.x
- Create a virtual environment and install dependencies:

```bash
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
# macOS/Linux
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### Run the Web UI (dev)

```bash
uvicorn --app-dir src playyt.webapp.main:app --reload --port 8000
```

Then open http://localhost:8000 in your browser.

## Status

- Early scaffolding phase. Core code and modules will be added incrementally.

## License

CC BY-NC 4.0 — see LICENSE.md.

