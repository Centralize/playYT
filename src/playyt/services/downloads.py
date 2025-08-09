from __future__ import annotations
from typing import List, Dict, Any, Optional
from pathlib import Path
import os
import time
from datetime import datetime


def get_downloads_directory() -> Path:
    """Get the downloads directory path"""
    return Path("downloads")


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_video_info_from_filename(filename: str) -> Dict[str, Any]:
    """Extract video information from filename"""
    # Remove extension
    name_without_ext = Path(filename).stem
    
    # Try to extract basic info (this is a simple approach)
    # In a real app, you might store metadata separately
    return {
        "title": name_without_ext,
        "original_filename": filename
    }


def scan_downloads() -> List[Dict[str, Any]]:
    """Scan downloads directory and return list of video files with metadata"""
    downloads_dir = get_downloads_directory()
    
    if not downloads_dir.exists():
        return []
    
    video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    video_files = []
    
    try:
        for file_path in downloads_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                try:
                    stat = file_path.stat()
                    file_info = {
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "size_formatted": format_file_size(stat.st_size),
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "modified_formatted": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "extension": file_path.suffix.lower(),
                    }
                    
                    # Add video info extracted from filename
                    video_info = get_video_info_from_filename(file_path.name)
                    file_info.update(video_info)
                    
                    video_files.append(file_info)
                    
                except (OSError, PermissionError):
                    # Skip files we can't access
                    continue
                    
    except (OSError, PermissionError):
        # Can't access downloads directory
        return []
    
    # Sort by modification time (newest first)
    video_files.sort(key=lambda x: x["modified"], reverse=True)
    
    return video_files


def delete_download(filename: str) -> Dict[str, Any]:
    """Delete a downloaded file"""
    downloads_dir = get_downloads_directory()
    file_path = downloads_dir / filename
    
    # Security check: ensure file is in downloads directory
    try:
        file_path = file_path.resolve()
        downloads_dir = downloads_dir.resolve()
        
        if not str(file_path).startswith(str(downloads_dir)):
            return {"success": False, "error": "Invalid file path"}
        
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            return {"success": True, "message": f"Deleted {filename}"}
        else:
            return {"success": False, "error": "File not found"}
            
    except (OSError, PermissionError) as e:
        return {"success": False, "error": f"Permission denied: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Error deleting file: {str(e)}"}


def get_downloads_stats() -> Dict[str, Any]:
    """Get statistics about downloads"""
    files = scan_downloads()
    
    total_files = len(files)
    total_size = sum(f["size"] for f in files)
    
    return {
        "total_files": total_files,
        "total_size": total_size,
        "total_size_formatted": format_file_size(total_size),
        "latest_download": files[0]["modified_formatted"] if files else None
    }
