from pathlib import Path
from PIL import Image
from typing import Tuple

def convert_image(input_path: Path, target_format: str, output_dir: Path) -> Path:
    """Convert an image to target format."""
    target_format = target_format.lower().lstrip(".")
    if target_format == "jpeg":
        target_format = "jpg"
        
    stem = input_path.stem
    output_path = output_dir / f"{stem}.{target_format}"
    
    with Image.open(input_path) as img:
        # Handle RGBA/transparency when saving to formats that don't support it
        if target_format in {"jpg", "jpeg", "bmp"}:
            if img.mode in ("RGBA", "LA", "P"):
                # Create white background
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")
        elif target_format == "ico":
            # Resize icon to common sizes
            img = img.resize((256, 256), Image.Resampling.LANCZOS)
            
        save_kwargs = {}
        if target_format in ("jpg", "jpeg"):
            save_kwargs["quality"] = 95
            save_kwargs["optimize"] = True
        elif target_format == "png":
            save_kwargs["optimize"] = True
            
        # PIL format name
        pil_format = "JPEG" if target_format in ("jpg", "jpeg") else target_format.upper()
        if target_format == "pdf":
            pil_format = "PDF"
            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1])
                img = bg
                
        img.save(output_path, format=pil_format, **save_kwargs)
        
    return output_path

def compress_image(input_path: Path, mode: str, output_dir: Path) -> Path:
    """Compress image by quality reduction or downscaling."""
    stem = input_path.stem
    ext = input_path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        out_ext = ".jpg"
    elif ext == ".png":
        out_ext = ".png"
    elif ext == ".webp":
        out_ext = ".webp"
    else:
        out_ext = ".jpg" # fallback default for high compression
        
    output_path = output_dir / f"{stem}_compressed{out_ext}"
    
    with Image.open(input_path) as img:
        # Determine parameters
        quality = 85
        resize_ratio = 1.0
        
        if mode == "cmp_img_light":
            quality = 80
        elif mode == "cmp_img_medium":
            quality = 60
        elif mode == "cmp_img_high":
            quality = 30
        elif mode == "cmp_img_half":
            quality = 75
            resize_ratio = 0.5

        if resize_ratio != 1.0:
            new_w = max(1, int(img.width * resize_ratio))
            new_h = max(1, int(img.height * resize_ratio))
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
        if out_ext == ".jpg":
            if img.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")
            img.save(output_path, "JPEG", quality=quality, optimize=True)
        elif out_ext == ".webp":
            img.save(output_path, "WEBP", quality=quality, method=6)
        elif out_ext == ".png":
            # For PNG, convert to palette if high compression or optimize
            if mode in ("cmp_img_high", "cmp_img_medium"):
                quantized = img.quantize(colors=128 if mode == "cmp_img_medium" else 64)
                quantized.save(output_path, "PNG", optimize=True)
            else:
                img.save(output_path, "PNG", optimize=True)
                
    return output_path
