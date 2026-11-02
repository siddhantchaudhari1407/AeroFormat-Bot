import zipfile
from pathlib import Path
import pandas as pd

def convert_pdf_to_docx(input_path: Path, output_dir: Path) -> Path:
    from pdf2docx import Converter
    output_path = output_dir / f"{input_path.stem}.docx"
    cv = Converter(str(input_path))
    cv.convert(str(output_path), start=0, end=None)
    cv.close()
    return output_path

def convert_pdf_to_txt(input_path: Path, output_dir: Path) -> Path:
    import fitz # PyMuPDF
    output_path = output_dir / f"{input_path.stem}.txt"
    doc = fitz.open(str(input_path))
    text_content = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text_content.append(f"--- Page {page_num + 1} ---\n")
        text_content.append(page.get_text())
    doc.close()
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(text_content))
    return output_path

def convert_pdf_to_images_zip(input_path: Path, output_dir: Path) -> Path:
    import fitz
    doc = fitz.open(str(input_path))
    zip_path = output_dir / f"{input_path.stem}_images.zip"
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=150)
            img_filename = f"page_{i+1:03d}.png"
            img_path = output_dir / img_filename
            pix.save(str(img_path))
            zipf.write(img_path, arcname=img_filename)
            try:
                img_path.unlink()
            except OSError:
                pass
    doc.close()
    return zip_path

def convert_txt_to_pdf(input_path: Path, output_dir: Path) -> Path:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    output_path = output_dir / f"{input_path.stem}.pdf"
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.fontSize = 10
    normal_style.leading = 14
    
    story = []
    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            clean_line = line.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if not clean_line:
                story.append(Spacer(1, 10))
            else:
                story.append(Paragraph(clean_line, normal_style))
                
    doc.build(story)
    return output_path

def convert_docx_to_txt(input_path: Path, output_dir: Path) -> Path:
    import docx
    doc = docx.Document(str(input_path))
    output_path = output_dir / f"{input_path.stem}.txt"
    full_text = [para.text for para in doc.paragraphs]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))
    return output_path

def convert_csv_to_xlsx(input_path: Path, output_dir: Path) -> Path:
    output_path = output_dir / f"{input_path.stem}.xlsx"
    df = pd.read_csv(input_path)
    df.to_excel(output_path, index=False)
    return output_path

def convert_xlsx_to_csv(input_path: Path, output_dir: Path) -> Path:
    output_path = output_dir / f"{input_path.stem}.csv"
    df = pd.read_excel(input_path)
    df.to_csv(output_path, index=False)
    return output_path

def compress_pdf(input_path: Path, aggressive: bool, output_dir: Path) -> Path:
    import fitz
    output_path = output_dir / f"{input_path.stem}_compressed.pdf"
    doc = fitz.open(str(input_path))
    
    if aggressive:
        # Downscale images in document
        for page in doc:
            for img in page.get_images():
                xref = img[0]
                try:
                    pix = fitz.Pixmap(doc, xref)
                    if pix.width > 1200 or pix.height > 1200:
                        scale = min(1200 / pix.width, 1200 / pix.height)
                        new_pix = fitz.Pixmap(pix, int(pix.width * scale), int(pix.height * scale), 0)
                        doc.update_stream(xref, new_pix.tobytes())
                except Exception:
                    pass
        doc.save(str(output_path), garbage=4, deflate=True, clean=True)
    else:
        doc.save(str(output_path), garbage=3, deflate=True)
        
    doc.close()
    return output_path
