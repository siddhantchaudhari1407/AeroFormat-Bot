from pathlib import Path
from bot.utils.format_detector import detect_category, normalize_extension
from bot.converters.image_converter import convert_image, compress_image
from bot.converters.audio_converter import convert_audio, compress_audio
from bot.converters.video_converter import convert_video, compress_video
from bot.converters.document_converter import (
    convert_pdf_to_docx, convert_pdf_to_txt, convert_pdf_to_images_zip,
    convert_txt_to_pdf, convert_docx_to_txt, convert_csv_to_xlsx,
    convert_xlsx_to_csv, compress_pdf
)
from bot.converters.data_converter import convert_data
from bot.converters.archive_converter import compress_to_zip, compress_to_targz, extract_archive

def convert_code_file(input_path: Path, target_format: str, output_dir: Path) -> Path:
    """Convert code/markdown/text file to PDF, TXT, HTML, or ZIP."""
    target = target_format.lower().lstrip(".")
    stem = input_path.stem

    if target == "pdf":
        return convert_txt_to_pdf(input_path, output_dir)
    elif target == "txt":
        output_path = output_dir / f"{stem}.txt"
        with open(input_path, "r", encoding="utf-8", errors="replace") as fin:
            with open(output_path, "w", encoding="utf-8") as fout:
                fout.write(fin.read())
        return output_path
    elif target == "html":
        import markdown
        output_path = output_dir / f"{stem}.html"
        with open(input_path, "r", encoding="utf-8", errors="replace") as fin:
            raw = fin.read()
        if input_path.suffix.lower() in {".md", ".markdown"}:
            body = markdown.markdown(raw, extensions=["tables", "fenced_code"])
        else:
            escaped = raw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            body = f"<pre><code>{escaped}</code></pre>"
        html_doc = f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{stem}</title><style>body{{font-family:sans-serif;padding:20px;line-height:1.6}}pre{{background:#f4f4f4;padding:15px;border-radius:6px;overflow-x:auto}}</style></head><body>{body}</body></html>"
        with open(output_path, "w", encoding="utf-8") as fout:
            fout.write(html_doc)
        return output_path
    elif target == "zip":
        return compress_to_zip(input_path, output_dir)

    raise ValueError(f"Cannot convert code file to {target}")

def execute_conversion(input_path: Path, target_format: str, output_dir: Path) -> Path:
    """Dispatches file conversion based on source extension and target format."""
    ext = normalize_extension(input_path.suffix)
    cat = detect_category(ext)
    target = target_format.lower().strip()

    if cat == "image":
        return convert_image(input_path, target, output_dir)
        
    elif cat == "audio":
        return convert_audio(input_path, target, output_dir)
        
    elif cat == "video":
        return convert_video(input_path, target, output_dir)
        
    elif cat == "document":
        if ext == "pdf":
            if target == "docx":
                return convert_pdf_to_docx(input_path, output_dir)
            elif target == "txt":
                return convert_pdf_to_txt(input_path, output_dir)
            elif "zip" in target:
                return convert_pdf_to_images_zip(input_path, output_dir)
        elif ext in {"docx", "odt", "rtf"}:
            if target == "txt":
                return convert_docx_to_txt(input_path, output_dir)
            elif target == "pdf":
                txt_file = convert_docx_to_txt(input_path, output_dir)
                return convert_txt_to_pdf(txt_file, output_dir)
        elif ext in {"txt", "md"}:
            if target == "pdf":
                return convert_txt_to_pdf(input_path, output_dir)
        elif ext in {"csv", "tsv"} and target in {"xlsx", "pdf", "json"}:
            if target == "xlsx":
                return convert_csv_to_xlsx(input_path, output_dir)
            elif target == "json":
                return convert_data(input_path, "json", output_dir)
            elif target == "pdf":
                return convert_txt_to_pdf(input_path, output_dir)
        elif ext in {"xlsx", "xls", "ods"} and target == "csv":
            return convert_xlsx_to_csv(input_path, output_dir)
            
    elif cat == "data":
        return convert_data(input_path, target, output_dir)

    elif cat == "code":
        return convert_code_file(input_path, target, output_dir)

    elif cat == "archive":
        if target == "zip":
            return compress_to_zip(input_path, output_dir)
        elif target in {"tar.gz", "targz"}:
            return compress_to_targz(input_path, output_dir)

    # Universal fallback: if user wants zip, txt, or pdf
    if target == "zip":
        return compress_to_zip(input_path, output_dir)
    elif target == "pdf":
        return convert_txt_to_pdf(input_path, output_dir)

    raise ValueError(f"Conversion from .{ext} to .{target} is not directly supported.")

def execute_compression(input_path: Path, mode: str, output_dir: Path) -> Path:
    """Dispatches file compression based on selected mode."""
    ext = normalize_extension(input_path.suffix)
    cat = detect_category(ext)
    
    if mode.startswith("cmp_img_"):
        return compress_image(input_path, mode, output_dir)
        
    elif mode.startswith("cmp_aud_"):
        return compress_audio(input_path, mode, output_dir)
        
    elif mode.startswith("cmp_vid_"):
        return compress_video(input_path, mode, output_dir)
        
    elif mode == "cmp_pdf_std":
        return compress_pdf(input_path, aggressive=False, output_dir=output_dir)
        
    elif mode == "cmp_pdf_agg":
        return compress_pdf(input_path, aggressive=True, output_dir=output_dir)
        
    elif mode == "cmp_arch_zip":
        return compress_to_zip(input_path, output_dir)
        
    elif mode == "cmp_arch_targz":
        return compress_to_targz(input_path, output_dir)
        
    # Default fallback
    return compress_to_zip(input_path, output_dir)
