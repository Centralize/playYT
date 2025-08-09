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

## Features

- **YouTube Search**: Real-time search with thumbnails and metadata
- **Video Downloads**: Download videos in various formats using yt-dlp
- **Downloads Management**: View and manage downloaded videos
- **Dark/Light Theme**: Toggle between themes with persistent preference
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Built with Bulma CSS framework

## Downloads

Downloaded videos are stored in the `downloads/` directory. This directory is excluded from git tracking to prevent large video files from being committed to the repository.

## Status

- Fully functional YouTube client with search, download, and management features.

## License

CC BY-NC 4.0 — see LICENSE.md.

