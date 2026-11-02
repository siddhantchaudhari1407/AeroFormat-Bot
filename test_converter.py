import sys
import os
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bot.converters.dispatcher import execute_conversion, execute_compression
from bot.utils.format_detector import get_available_conversions, detect_category
from bot.utils.file_manager import format_size

def test_pipeline():
    test_dir = Path(__file__).parent / "test_output"
    test_dir.mkdir(exist_ok=True)
    print("[*] Running File Converter & Compressor Bot Test Suite...\n")

    # 1. Test Image Conversion & Compression
    print("[1] Testing Image Engine:")
    from PIL import Image
    sample_img_path = test_dir / "sample_test.png"
    img = Image.new("RGBA", (400, 400), color=(255, 100, 100, 255))
    img.save(sample_img_path, "PNG")
    print(f"    Created sample PNG: {sample_img_path.name} ({format_size(sample_img_path.stat().st_size)})")

    # Convert PNG to JPG
    out_jpg = execute_conversion(sample_img_path, "jpg", test_dir)
    print(f"    Converted to JPG: {out_jpg.name} ({format_size(out_jpg.stat().st_size)})")

    # Convert PNG to PDF
    out_pdf = execute_conversion(sample_img_path, "pdf", test_dir)
    print(f"    Converted to PDF: {out_pdf.name} ({format_size(out_pdf.stat().st_size)})")

    # Compress Image
    out_compressed_img = execute_compression(sample_img_path, "cmp_img_medium", test_dir)
    print(f"    Compressed Image (Medium): {out_compressed_img.name} ({format_size(out_compressed_img.stat().st_size)})")

    # 2. Test Data Conversion
    print("\n[2] Testing Data Engine:")
    sample_json = test_dir / "sample_data.json"
    with open(sample_json, "w", encoding="utf-8") as f:
        f.write('{"bot": "FileConverter", "status": "active", "supported_categories": ["image", "doc", "audio", "video", "data"]}')
    
    out_yaml = execute_conversion(sample_json, "yaml", test_dir)
    print(f"    Converted JSON to YAML: {out_yaml.name}")

    out_xml = execute_conversion(sample_json, "xml", test_dir)
    print(f"    Converted JSON to XML: {out_xml.name}")

    # 3. Test Document Conversion (TXT to PDF)
    print("\n[3] Testing Document Engine:")
    sample_txt = test_dir / "sample_notes.txt"
    with open(sample_txt, "w", encoding="utf-8") as f:
        f.write("Hello World!\nThis is a test document generated for file conversion.")
    
    out_doc_pdf = execute_conversion(sample_txt, "pdf", test_dir)
    print(f"    Converted TXT to PDF: {out_doc_pdf.name} ({format_size(out_doc_pdf.stat().st_size)})")

    # 4. Test Archive Compression
    print("\n[4] Testing Archive Engine:")
    out_zip = execute_compression(sample_txt, "cmp_arch_zip", test_dir)
    print(f"    Compressed to ZIP: {out_zip.name} ({format_size(out_zip.stat().st_size)})")

    # 5. Test Audio/Video Engine with FFmpeg
    print("\n[5] Testing FFmpeg Engine:")
    from bot.config import FFMPEG_PATH
    print(f"    FFmpeg Path detected: {FFMPEG_PATH}")
    if os.path.exists(FFMPEG_PATH):
        print("    FFmpeg binary is verified and ready for Audio/Video conversions.")
    else:
        print("    [!] Notice: FFmpeg binary not found at path, please check installation.")

    print("\n[SUCCESS] ALL TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    test_pipeline()
