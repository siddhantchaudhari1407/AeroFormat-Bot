import os
from pathlib import Path
from typing import Dict, List, Optional

IMAGE_EXTENSIONS = {
    "jpg", "jpeg", "png", "webp", "bmp", "tiff", "tif", "ico", "gif",
    "eps", "tga", "ppm", "pgm", "pbm", "pcx", "dds", "sgi", "im", "icns", "svg"
}

AUDIO_EXTENSIONS = {
    "mp3", "wav", "ogg", "aac", "flac", "m4a", "wma", "opus",
    "aiff", "alac", "ac3", "amr", "m4r"
}

VIDEO_EXTENSIONS = {
    "mp4", "mkv", "avi", "mov", "webm", "flv", "wmv", "3gp",
    "m4v", "ts", "mpg", "mpeg", "ogv", "vob"
}

DOCUMENT_EXTENSIONS = {
    "pdf", "docx", "doc", "txt", "rtf", "odt", "epub", "csv", "xlsx", "xls", "ods", "tsv"
}

DATA_EXTENSIONS = {
    "json", "yaml", "yml", "xml", "toml", "ini", "env"
}

CODE_EXTENSIONS = {
    "py", "js", "ts", "jsx", "tsx", "html", "htm", "css", "scss",
    "java", "c", "cpp", "h", "cs", "php", "rb", "go", "rs", "sh",
    "bat", "ps1", "sql", "md", "markdown", "log"
}

ARCHIVE_EXTENSIONS = {
    "zip", "tar", "gz", "tgz", "bz2", "tbz2", "xz", "txz", "7z", "rar"
}

def normalize_extension(ext: str) -> str:
    ext = ext.lower().strip().lstrip(".")
    if ext == "jpeg":
        return "jpg"
    if ext == "tif":
        return "tiff"
    if ext == "yml":
        return "yaml"
    if ext == "htm":
        return "html"
    if ext == "markdown":
        return "md"
    return ext

def detect_category(extension: str) -> str:
    norm_ext = normalize_extension(extension)
    if norm_ext in IMAGE_EXTENSIONS:
        return "image"
    if norm_ext in AUDIO_EXTENSIONS:
        return "audio"
    if norm_ext in VIDEO_EXTENSIONS:
        return "video"
    if norm_ext in DOCUMENT_EXTENSIONS:
        return "document"
    if norm_ext in DATA_EXTENSIONS:
        return "data"
    if norm_ext in CODE_EXTENSIONS:
        return "code"
    if norm_ext in ARCHIVE_EXTENSIONS:
        return "archive"
    return "other"

def get_available_conversions(extension: str) -> List[str]:
    norm_ext = normalize_extension(extension)
    cat = detect_category(norm_ext)
    
    if cat == "image":
        targets = ["png", "jpg", "webp", "bmp", "tiff", "ico", "pdf"]
        return [t for t in targets if t != norm_ext]

    elif cat == "audio":
        targets = ["mp3", "wav", "ogg", "aac", "flac", "m4a", "opus"]
        return [t for t in targets if t != norm_ext]

    elif cat == "video":
        targets = ["mp4", "avi", "mkv", "mov", "webm", "gif", "mp3 (extract)"]
        return [t for t in targets if t != norm_ext]

    elif cat == "document":
        if norm_ext == "pdf":
            return ["docx", "txt", "images.zip"]
        elif norm_ext in {"docx", "odt", "rtf"}:
            return ["pdf", "txt"]
        elif norm_ext == "txt":
            return ["pdf", "docx"]
        elif norm_ext in {"csv", "tsv"}:
            return ["xlsx", "json", "pdf"]
        elif norm_ext in {"xlsx", "xls", "ods"}:
            return ["csv", "json"]
        elif norm_ext == "epub":
            return ["txt", "pdf"]

    elif cat == "data":
        if norm_ext == "json":
            return ["yaml", "xml", "csv", "toml"]
        elif norm_ext == "yaml":
            return ["json", "xml", "toml"]
        elif norm_ext == "xml":
            return ["json", "yaml"]
        elif norm_ext == "toml":
            return ["json", "yaml"]
        elif norm_ext in {"ini", "env"}:
            return ["json", "yaml", "txt"]

    elif cat == "code":
        return ["pdf", "txt", "html", "zip"]

    elif cat == "archive":
        targets = ["zip", "tar.gz", "tar.bz2"]
        return [t for t in targets if t != norm_ext]

    # For any unknown file format, allow conversion to PDF or ZIP
    return ["zip", "txt", "pdf"]

def supports_compression(extension: str) -> bool:
    return True
