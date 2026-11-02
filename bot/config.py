import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = Path(os.getenv("TEMP_STORAGE_DIR", BASE_DIR / "temp_downloads"))
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Bot token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

# Limits (Telegram standard Bot API allows max 20MB download)
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 20))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
CLEANUP_INTERVAL_SECONDS = int(os.getenv("CLEANUP_INTERVAL_SECONDS", 3600))

# Try locating ffmpeg
def get_ffmpeg_path():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        # Fallback to system ffmpeg if available
        import shutil
        sys_ffmpeg = shutil.which("ffmpeg")
        return sys_ffmpeg or "ffmpeg"

FFMPEG_PATH = get_ffmpeg_path()
