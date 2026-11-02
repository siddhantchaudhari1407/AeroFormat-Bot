import os
import shutil
import time
from pathlib import Path
from bot.config import TEMP_DIR

def create_user_workspace(user_id: int, file_id: str) -> Path:
    """Create an isolated workspace folder for a user transaction."""
    workspace = TEMP_DIR / str(user_id) / file_id
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace

def cleanup_workspace(workspace_path: Path):
    """Safely remove a temporary directory and its contents."""
    try:
        if workspace_path.exists() and workspace_path.is_dir():
            shutil.rmtree(workspace_path, ignore_errors=True)
    except Exception as e:
        print(f"Error cleaning up {workspace_path}: {e}")

def format_size(size_bytes: int) -> str:
    """Return human readable file size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def periodic_temp_cleanup(max_age_seconds: int = 3600):
    """Remove files in TEMP_DIR older than max_age_seconds."""
    now = time.time()
    try:
        for root, dirs, files in os.walk(TEMP_DIR, topdown=False):
            for name in files:
                filepath = os.path.join(root, name)
                try:
                    if os.path.getmtime(filepath) < now - max_age_seconds:
                        os.remove(filepath)
                except OSError:
                    pass
            for name in dirs:
                dirpath = os.path.join(root, name)
                try:
                    if not os.listdir(dirpath):
                        os.rmdir(dirpath)
                except OSError:
                    pass
    except Exception as e:
        print(f"Cleanup error: {e}")
