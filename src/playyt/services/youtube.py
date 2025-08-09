from __future__ import annotations
from typing import List, Optional, Dict, Any
from datetime import timedelta
import os
from pathlib import Path

try:
    from yt_dlp import YoutubeDL
except Exception:  # pragma: no cover - if yt-dlp missing
    YoutubeDL = None  # type: ignore


def _fmt_duration(seconds: Optional[int]) -> str:
    if not seconds and seconds != 0:
        return ""
    td = timedelta(seconds=int(seconds))
    total_seconds = int(td.total_seconds())
    m, s = divmod(total_seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"


def _choose_thumbnail(entry: Dict[str, Any]) -> Optional[str]:
    # Prefer 'thumbnail' if present; else pick the largest from 'thumbnails'
    thumb = entry.get("thumbnail")
    if thumb:
        return thumb
    thumbs = entry.get("thumbnails") or []
    if isinstance(thumbs, list) and thumbs:
        # Pick the largest by 'width' if available
        try:
            sorted_thumbs = sorted(
                thumbs, key=lambda t: (t.get("width") or 0, t.get("height") or 0)
            )
            return sorted_thumbs[-1].get("url")
        except Exception:
            return thumbs[-1].get("url")
    return None


def youtube_search(query: str, limit: int = 12) -> List[dict]:
    if not query:
        return []
    if YoutubeDL is None:
        return []
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
        # Avoid full nested extraction for speed; but keep enough data
        # "extract_flat": "in_playlist",
        "default_search": "ytsearch",
    }
    results: List[dict] = []
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        entries = info.get("entries", []) if isinstance(info, dict) else []
        for e in entries:
            results.append(
                {
                    "id": e.get("id"),
                    "title": e.get("title"),
                    "channel": e.get("uploader") or e.get("channel") or "",
                    "duration": _fmt_duration(e.get("duration")),
                    "thumbnail": _choose_thumbnail(e),
                }
            )
    return results


def get_video(video_id: str) -> Optional[dict]:
    if not video_id or YoutubeDL is None:
        return None
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            e = ydl.extract_info(url, download=False)
        except Exception:
            return None
        return {
            "id": e.get("id"),
            "title": e.get("title"),
            "channel": e.get("uploader") or e.get("channel") or "",
            "duration": _fmt_duration(e.get("duration")),
            "description": e.get("description") or "",
            "thumbnail": _choose_thumbnail(e),
            "webpage_url": e.get("webpage_url") or url,
        }


def get_video_formats(video_id: str) -> List[dict]:
    """Get available download formats for a video"""
    if not video_id or YoutubeDL is None:
        return []

    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception:
            return []

        formats = []
        for fmt in info.get("formats", []):
            if fmt.get("vcodec") != "none" or fmt.get("acodec") != "none":  # Skip metadata-only formats
                formats.append({
                    "format_id": fmt.get("format_id"),
                    "ext": fmt.get("ext"),
                    "quality": fmt.get("format_note") or fmt.get("quality") or "Unknown",
                    "filesize": fmt.get("filesize"),
                    "vcodec": fmt.get("vcodec"),
                    "acodec": fmt.get("acodec"),
                    "resolution": fmt.get("resolution"),
                })

        return formats


def download_video(video_id: str, format_id: str = "best", download_dir: str = "downloads") -> dict:
    """Download a video with specified format"""
    if not video_id or YoutubeDL is None:
        return {"success": False, "error": "yt-dlp not available"}

    # Create download directory if it doesn't exist
    Path(download_dir).mkdir(exist_ok=True)

    url = f"https://www.youtube.com/watch?v={video_id}"

    # Configure yt-dlp options
    ydl_opts = {
        "format": format_id,
        "outtmpl": os.path.join(download_dir, "%(title)s.%(ext)s"),
        "noplaylist": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "Unknown")

            # Download the video
            ydl.download([url])

            return {
                "success": True,
                "title": title,
                "message": f"Successfully downloaded: {title}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

