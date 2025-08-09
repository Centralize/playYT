from pathlib import Path
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel
import os
from pathlib import Path
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
from playyt.services.downloads import scan_downloads, delete_download, get_downloads_stats, get_downloads_directory  # noqa: E402

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


@app.get("/downloads", response_class=HTMLResponse)
def downloads_page(request: Request):
    """Display downloaded videos page"""
    downloads = scan_downloads()
    stats = get_downloads_stats()
    return templates.TemplateResponse(
        "downloads.html",
        {
            "request": request,
            "title": "Downloads - playYT",
            "downloads": downloads,
            "stats": stats
        },
    )


@app.delete("/api/downloads/{filename}", response_class=JSONResponse)
def delete_download_endpoint(filename: str):
    """Delete a downloaded file"""
    result = delete_download(filename)
    return result


@app.get("/api/downloads/{filename}/download")
def download_file_endpoint(filename: str):
    """Download a file from the downloads directory to user's workstation"""
    downloads_dir = get_downloads_directory()
    file_path = downloads_dir / filename

    # Security check: ensure file is in downloads directory
    try:
        file_path = file_path.resolve()
        downloads_dir = downloads_dir.resolve()

        if not str(file_path).startswith(str(downloads_dir)):
            raise HTTPException(status_code=400, detail="Invalid file path")

        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing file: {str(e)}")


@app.get("/player/{filename}", response_class=HTMLResponse)
def video_player_page(request: Request, filename: str):
    """Video player page for streaming videos"""
    downloads_dir = get_downloads_directory()
    file_path = downloads_dir / filename

    # Security check: ensure file is in downloads directory
    try:
        file_path = file_path.resolve()
        downloads_dir = downloads_dir.resolve()

        if not str(file_path).startswith(str(downloads_dir)):
            raise HTTPException(status_code=400, detail="Invalid file path")

        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Video not found")

        # Get video info
        video_info = {
            "filename": filename,
            "title": Path(filename).stem,
            "size": file_path.stat().st_size,
            "extension": Path(filename).suffix.lower()
        }

        return templates.TemplateResponse(
            "video_player.html",
            {
                "request": request,
                "title": f"Playing: {video_info['title']} - playYT",
                "video": video_info
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing video: {str(e)}")


@app.get("/api/stream/{filename}")
def stream_video(request: Request, filename: str):
    """Stream video file with range support for HTML5 video player"""
    downloads_dir = get_downloads_directory()
    file_path = downloads_dir / filename

    # Security check: ensure file is in downloads directory
    try:
        file_path = file_path.resolve()
        downloads_dir = downloads_dir.resolve()

        if not str(file_path).startswith(str(downloads_dir)):
            raise HTTPException(status_code=400, detail="Invalid file path")

        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Video not found")

        file_size = file_path.stat().st_size
        range_header = request.headers.get('range')

        # Determine content type based on file extension
        content_type_map = {
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.mkv': 'video/x-matroska',
            '.flv': 'video/x-flv',
            '.wmv': 'video/x-ms-wmv',
            '.m4v': 'video/x-m4v'
        }

        file_extension = Path(filename).suffix.lower()
        content_type = content_type_map.get(file_extension, 'video/mp4')

        if range_header:
            # Handle range requests for video seeking
            range_match = range_header.replace('bytes=', '').split('-')
            start = int(range_match[0]) if range_match[0] else 0
            end = int(range_match[1]) if range_match[1] else file_size - 1

            def generate_chunk():
                with open(file_path, 'rb') as video_file:
                    video_file.seek(start)
                    remaining = end - start + 1
                    while remaining:
                        chunk_size = min(8192, remaining)
                        chunk = video_file.read(chunk_size)
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk

            headers = {
                'Content-Range': f'bytes {start}-{end}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(end - start + 1),
                'Content-Type': content_type,
            }

            return StreamingResponse(
                generate_chunk(),
                status_code=206,
                headers=headers
            )
        else:
            # Serve entire file
            def generate_full():
                with open(file_path, 'rb') as video_file:
                    while True:
                        chunk = video_file.read(8192)
                        if not chunk:
                            break
                        yield chunk

            headers = {
                'Content-Length': str(file_size),
                'Accept-Ranges': 'bytes',
                'Content-Type': content_type,
            }

            return StreamingResponse(
                generate_full(),
                headers=headers
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streaming video: {str(e)}")

