from pathlib import Path
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="playYT Web UI")

# Import services lazily to keep clear boundaries
from playyt.services.search import search_videos  # noqa: E402

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
        results = search_videos(q)
    return templates.TemplateResponse(
        "search.html",
        {"request": request, "title": "playYT", "query": q, "results": results},
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/search", response_class=JSONResponse)
def api_search(q: str = Query(..., alias="q")):
    return {"query": q, "results": search_videos(q)}

