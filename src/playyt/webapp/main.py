from pathlib import Path
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="playYT Web UI")


class DownloadRequest(BaseModel):
    format_id: str = "best"

# Import services lazily to keep clear boundaries
# Prefer real YouTube search if available; fall back to in-memory demo
try:
    from playyt.services.youtube import (
        youtube_search as real_search,
        get_video as real_get_video,
        get_video_formats,
        download_video
    )  # type: ignore
except Exception:  # pragma: no cover
    real_search = None
    real_get_video = None
    get_video_formats = None
    download_video = None

from playyt.services.search import search_videos as demo_search, get_video as demo_get_video  # noqa: E402

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "playYT",
            "message": "Welcome to playYT Web UI (FastAPI)",
        },
    )


@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request, q: str | None = Query(default=None, alias="q")):
    results = None
    if q:
        if real_search:
            results = real_search(q)
        else:
            results = demo_search(q)
    return templates.TemplateResponse(
        "search.html",
        {"request": request, "title": "playYT", "query": q, "results": results},
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/search", response_class=JSONResponse)
def api_search(q: str = Query(..., alias="q")):
    if real_search:
        results = real_search(q)
    else:
        results = demo_search(q)
    return {"query": q, "results": results}


@app.get("/video/{video_id}", response_class=HTMLResponse)
def video_detail(request: Request, video_id: str):
    # Prefer real online fetch
    if real_get_video:
        video = real_get_video(video_id)
    else:
        video = demo_get_video(video_id)
    if not video:
        return templates.TemplateResponse(
            "video_detail.html",
            {"request": request, "title": "Not found - playYT", "video": None},
            status_code=404,
        )
    return templates.TemplateResponse(
        "video_detail.html",
        {"request": request, "title": video["title"] + " - playYT", "video": video},
    )


@app.get("/api/video/{video_id}/formats", response_class=JSONResponse)
def get_formats(video_id: str):
    """Get available download formats for a video"""
    if get_video_formats:
        formats = get_video_formats(video_id)
        return {"video_id": video_id, "formats": formats}
    else:
        return {"video_id": video_id, "formats": [], "error": "Download functionality not available"}


@app.post("/api/video/{video_id}/download", response_class=JSONResponse)
def download_video_endpoint(video_id: str, request: DownloadRequest):
    """Download a video with specified format"""
    if download_video:
        result = download_video(video_id, request.format_id)
        return result
    else:
        return {"success": False, "error": "Download functionality not available"}

