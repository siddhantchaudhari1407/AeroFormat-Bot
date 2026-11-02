import zipfile
import tarfile
from pathlib import Path

def compress_to_zip(input_path: Path, output_dir: Path) -> Path:
    """Compress file or directory to a ZIP archive with highest deflate level."""
    output_path = output_dir / f"{input_path.stem}.zip"
    
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        if input_path.is_file():
            zipf.write(input_path, arcname=input_path.name)
        else:
            for item in input_path.rglob("*"):
                zipf.write(item, arcname=item.relative_to(input_path))
                
    return output_path

def compress_to_targz(input_path: Path, output_dir: Path) -> Path:
    """Compress file or directory to TAR.GZ archive."""
    output_path = output_dir / f"{input_path.stem}.tar.gz"
    
    with tarfile.open(output_path, "w:gz", compresslevel=9) as tar:
        arcname = input_path.name
        tar.add(input_path, arcname=arcname)
        
    return output_path

def compress_to_tarbz2(input_path: Path, output_dir: Path) -> Path:
    """Compress file or directory to TAR.BZ2 archive."""
    output_path = output_dir / f"{input_path.stem}.tar.bz2"
    
    with tarfile.open(output_path, "w:bz2", compresslevel=9) as tar:
        arcname = input_path.name
        tar.add(input_path, arcname=arcname)
        
    return output_path

def extract_archive(input_path: Path, output_dir: Path) -> Path:
    """Extract zip, tar, or gz archive to a folder."""
    extracted_folder = output_dir / f"{input_path.stem}_extracted"
    extracted_folder.mkdir(parents=True, exist_ok=True)
    
    if zipfile.is_zipfile(input_path):
        with zipfile.ZipFile(input_path, "r") as zipf:
            zipf.extractall(extracted_folder)
    elif tarfile.is_tarfile(input_path):
        with tarfile.open(input_path, "r:*") as tar:
            tar.extractall(extracted_folder)
    else:
        raise ValueError("Unsupported archive format for extraction.")
        
    return extracted_folder
