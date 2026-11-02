import subprocess
from pathlib import Path
from bot.config import FFMPEG_PATH

def convert_video(input_path: Path, target_format: str, output_dir: Path) -> Path:
    """Convert video format or extract audio from video."""
    target_format = target_format.lower().strip()
    
    if "mp3" in target_format:
        output_path = output_dir / f"{input_path.stem}.mp3"
        cmd = [
            FFMPEG_PATH, "-y",
            "-i", str(input_path),
            "-vn",
            "-c:a", "libmp3lame",
            "-q:a", "2",
            str(output_path)
        ]
    elif target_format == "gif":
        output_path = output_dir / f"{input_path.stem}.gif"
        # High quality 10fps palette GIF
        cmd = [
            FFMPEG_PATH, "-y",
            "-i", str(input_path),
            "-vf", "fps=10,scale='min(480,iw)':-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            str(output_path)
        ]
    else:
        norm_ext = target_format.lstrip(".")
        output_path = output_dir / f"{input_path.stem}.{norm_ext}"
        
        cmd = [
            FFMPEG_PATH, "-y",
            "-i", str(input_path),
        ]
        
        if norm_ext == "mp4":
            cmd.extend(["-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "128k"])
        elif norm_ext == "webm":
            cmd.extend(["-c:v", "libvpx-vp9", "-crf", "32", "-b:v", "0", "-c:a", "libopus"])
        elif norm_ext == "avi":
            cmd.extend(["-c:v", "mpeg4", "-q:v", "5", "-c:a", "mp3"])
        elif norm_ext == "mkv":
            cmd.extend(["-c:v", "libx264", "-c:a", "aac"])
        elif norm_ext == "mov":
            cmd.extend(["-c:v", "libx264", "-c:a", "aac"])
            
        cmd.append(str(output_path))
        
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg video conversion timed out after 180 seconds.")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg video conversion failed: {res.stderr}")
        
    return output_path

def compress_video(input_path: Path, mode: str, output_dir: Path) -> Path:
    """Compress video using CRF and resolution downscaling."""
    output_path = output_dir / f"{input_path.stem}_compressed.mp4"
    
    cmd = [
        FFMPEG_PATH, "-y",
        "-i", str(input_path),
        "-c:v", "libx264",
        "-c:a", "aac"
    ]
    
    if mode == "cmp_vid_light":
        # Light compression: CRF 26, audio 128k
        cmd.extend(["-crf", "26", "-preset", "faster", "-b:a", "128k"])
    elif mode == "cmp_vid_medium":
        # Medium compression: CRF 30, audio 96k
        cmd.extend(["-crf", "30", "-preset", "faster", "-b:a", "96k"])
    elif mode == "cmp_vid_high":
        # High compression: 720p max, CRF 34, audio 64k
        cmd.extend([
            "-vf", "scale='min(1280,iw)':-2",
            "-crf", "34",
            "-preset", "faster",
            "-b:a", "64k"
        ])
    else:
        cmd.extend(["-crf", "28", "-preset", "faster", "-b:a", "96k"])
        
    cmd.append(str(output_path))
    
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg video compression timed out after 180 seconds.")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg video compression failed: {res.stderr}")
        
    return output_path
