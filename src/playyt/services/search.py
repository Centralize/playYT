from typing import List

# Simple in-memory dataset for demo purposes
_SAMPLE_VIDEOS = [
    {"id": "a1", "title": "Getting started with FastAPI", "channel": "PlayYT Labs", "duration": "10:01", "description": "A beginner-friendly intro to FastAPI."},
    {"id": "b2", "title": "Python 3 Basics Tutorial", "channel": "Code Academy", "duration": "14:22", "description": "Learn Python 3 fundamentals."},
    {"id": "c3", "title": "Understanding Async IO in Python", "channel": "Tech Explained", "duration": "9:45", "description": "Concepts and patterns for async IO."},
    {"id": "d4", "title": "Top 10 FastAPI Tips", "channel": "PlayYT Labs", "duration": "7:30", "description": "Tips and tricks for building with FastAPI."},
]


def search_videos(query: str) -> List[dict]:
    if not query:
        return []
    q = query.lower()
    return [v for v in _SAMPLE_VIDEOS if q in v["title"].lower() or q in v["channel"].lower()]


def get_video(video_id: str) -> dict | None:
    for v in _SAMPLE_VIDEOS:
        if v["id"] == video_id:
            return v
    return None

