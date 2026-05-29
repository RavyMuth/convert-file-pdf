import os
from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has a .pdf extension."""
    if not filename or "." not in filename:
        return False
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def validate_pdf_content(filepath: str) -> bool:
    """Verify the file starts with the PDF magic bytes (%PDF-)."""
    try:
        with open(filepath, "rb") as f:
            header = f.read(5)
        return header == b"%PDF-"
    except Exception:
        return False
