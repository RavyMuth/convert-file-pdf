import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from app.utils.validators import allowed_file

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(file) -> Optional[str]:
    """Save an uploaded file to the uploads directory with a timestamp prefix."""
    if not allowed_file(file.filename):
        logger.warning(f"Invalid file type: {file.filename}")
        return None

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{ts}_{file.filename}"
    filepath = str(UPLOAD_DIR / safe_name)

    try:
        contents = file.file.read()
        with open(filepath, "wb") as f:
            f.write(contents)
        logger.info(f"Saved upload: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save upload {file.filename}: {e}")
        return None


def get_output_path(filename: str, extension: str) -> str:
    """Generate a unique output file path with the given extension."""
    stem = Path(filename).stem
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"{stem}_{ts}.{extension}"
    return str(OUTPUT_DIR / out_name)


def cleanup_file(filepath: str) -> None:
    """Delete a file if it exists (used for temp file cleanup)."""
    try:
        if os.path.isfile(filepath):
            os.remove(filepath)
            logger.info(f"Deleted file: {filepath}")
    except Exception as e:
        logger.warning(f"Cleanup failed for {filepath}: {e}")
