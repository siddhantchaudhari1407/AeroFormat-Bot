import subprocess
from pathlib import Path
from bot.config import FFMPEG_PATH

def convert_audio(input_path: Path, target_format: str, output_dir: Path) -> Path:
    """Convert audio file to target format using ffmpeg."""
    target_format = target_format.lower().lstrip(".")
    output_path = output_dir / f"{input_path.stem}.{target_format}"
    
    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i", str(input_path),
        "-vn" # No video stream
    ]
    
    if target_format == "mp3":
        cmd.extend(["-c:a", "libmp3lame", "-q:a", "2"])
    elif target_format == "aac":
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])
    elif target_format == "ogg":
        cmd.extend(["-c:a", "libvorbis", "-q:a", "4"])
    elif target_format == "flac":
        cmd.extend(["-c:a", "flac"])
    elif target_format == "wav":
        cmd.extend(["-c:a", "pcm_s16le"])
    elif target_format == "m4a":
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        
    cmd.append(str(output_path))
    
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg audio conversion timed out after 180 seconds.")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg audio conversion failed: {res.stderr}")
        
    return output_path

def compress_audio(input_path: Path, mode: str, output_dir: Path) -> Path:
    """Compress audio using specified bitrate."""
    bitrate = "128k"
    if mode == "cmp_aud_64":
        bitrate = "64k"
    elif mode == "cmp_aud_128":
        bitrate = "128k"
    elif mode == "cmp_aud_192":
        bitrate = "192k"
        
    ext = input_path.suffix.lower()
    # Default to mp3 for high compatibility if format isn't standard
    out_ext = ext if ext in {".mp3", ".m4a", ".ogg", ".aac"} else ".mp3"
    output_path = output_dir / f"{input_path.stem}_compressed{out_ext}"
    
    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i", str(input_path),
        "-vn",
        "-b:a", bitrate,
        str(output_path)
    ]
    
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg audio compression timed out after 180 seconds.")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg audio compression failed: {res.stderr}")
        
    return output_path
