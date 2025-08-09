from typing import List

# Simple in-memory dataset for demo purposes
_SAMPLE_VIDEOS = [
    {"id": "a1", "title": "Getting started with FastAPI", "channel": "PlayYT Labs", "duration": "10:01"},
    {"id": "b2", "title": "Python 3 Basics Tutorial", "channel": "Code Academy", "duration": "14:22"},
    {"id": "c3", "title": "Understanding Async IO in Python", "channel": "Tech Explained", "duration": "9:45"},
    {"id": "d4", "title": "Top 10 FastAPI Tips", "channel": "PlayYT Labs", "duration": "7:30"},
]


def search_videos(query: str) -> List[dict]:
    if not query:
        return []
    q = query.lower()
    return [v for v in _SAMPLE_VIDEOS if q in v["title"].lower() or q in v["channel"].lower()]

