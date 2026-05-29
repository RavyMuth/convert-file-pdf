import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """Custom exception raised when a conversion fails."""
    pass


def convert_to_docx(pdf_path: str, output_path: str) -> str:
    """Convert PDF to Word (.docx) using pdf2docx."""
    try:
        from pdf2docx import Converter
        cv = Converter(pdf_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
        logger.info(f"PDF -> DOCX: {output_path}")
        return output_path
    except Exception as e:
        raise ConversionError(f"DOCX conversion failed: {e}")


def convert_to_excel(pdf_path: str, output_path: str) -> str:
    """Extract tables from PDF and save as Excel (.xlsx)."""
    try:
        import pdfplumber
        import pandas as pd

        all_tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        all_tables.append((page_num, df))

        if not all_tables:
            raise ConversionError("No tables found in the PDF")

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for i, (page, df) in enumerate(all_tables, 1):
                sheet_name = f"Page{page}_Table{i}"[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        logger.info(f"PDF -> EXCEL: {output_path}")
        return output_path
    except ConversionError:
        raise
    except Exception as e:
        raise ConversionError(f"Excel conversion failed: {e}")


def convert_to_image(pdf_path: str, output_path: str, fmt: str = "png") -> str:
    """Render PDF pages as PNG/JPEG images using PyMuPDF."""
    try:
        import fitz

        doc = fitz.open(pdf_path)
        stem = Path(output_path).stem

        if len(doc) == 1:
            page = doc[0]
            pix = page.get_pixmap(dpi=300)
            pix.save(output_path)
        else:
            base = str(Path(output_path).parent / stem)
            ext = fmt.lower()
            for i, page in enumerate(doc, 1):
                pix = page.get_pixmap(dpi=300)
                page_path = f"{base}_page{i}.{ext}"
                pix.save(page_path)
                if i == 1:
                    output_path = page_path

        doc.close()
        logger.info(f"PDF -> IMAGE: {output_path}")
        return output_path
    except Exception as e:
        raise ConversionError(f"Image conversion failed: {e}")


def convert_to_text(pdf_path: str, output_path: str) -> str:
    """Extract text from PDF and save as a .txt file using PyMuPDF."""
    try:
        import fitz

        doc = fitz.open(pdf_path)
        text_parts = []
        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            text_parts.append(f"--- Page {page_num} ---\n{text}")
        doc.close()

        full_text = "\n\n".join(text_parts)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        logger.info(f"PDF -> TEXT: {output_path}")
        return output_path
    except Exception as e:
        raise ConversionError(f"Text conversion failed: {e}")


def convert_to_html(pdf_path: str, output_path: str) -> str:
    """Convert PDF to HTML using PyMuPDF's built-in HTML export."""
    try:
        import fitz

        doc = fitz.open(pdf_path)
        body = []
        for page_num, page in enumerate(doc, 1):
            html = page.get_text("html")
            body.append(f"<div class='page'>")
            body.append(f"<h2>Page {page_num}</h2>")
            body.append(html)
            body.append("</div>")

        full = [
            "<!DOCTYPE html><html><head><meta charset='utf-8'>",
            "<title>PDF Conversion</title>",
            "<style>",
            "body{font-family:sans-serif;margin:2em;}",
            ".page{margin-bottom:2em;border-bottom:1px solid #ccc;padding-bottom:1em;}",
            "</style></head><body>",
            *body,
            "</body></html>",
        ]
        doc.close()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(full))

        logger.info(f"PDF -> HTML: {output_path}")
        return output_path
    except Exception as e:
        raise ConversionError(f"HTML conversion failed: {e}")


# Maps format names (from URL) to converter functions
CONVERSION_MAP = {
    "docx": convert_to_docx,
    "xlsx": convert_to_excel,
    "excel": convert_to_excel,
    "png": convert_to_image,
    "jpg": convert_to_image,
    "jpeg": convert_to_image,
    "image": lambda p, o: convert_to_image(p, o, fmt="png"),
    "txt": convert_to_text,
    "text": convert_to_text,
    "html": convert_to_html,
}
