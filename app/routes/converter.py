import os
import urllib.parse
import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from app.models.conversion import ConversionResponse, UploadResponse
from app.utils.file_handler import (
    save_upload,
    get_output_path,
    cleanup_file,
    UPLOAD_DIR,
    OUTPUT_DIR,
)
from app.utils.validators import allowed_file, validate_pdf_content
from app.services.converter_service import (
    CONVERSION_MAP,
    ConversionError,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "pdf-converter"}


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a PDF file. Validates extension and PDF magic bytes."""
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are allowed.",
        )

    filepath = save_upload(file)
    if filepath is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to save uploaded file.",
        )

    if not validate_pdf_content(filepath):
        cleanup_file(filepath)
        raise HTTPException(
            status_code=400,
            detail="File is not a valid PDF.",
        )

    return UploadResponse(
        success=True,
        filename=Path(filepath).name,
        filepath=filepath,
        message="File uploaded successfully.",
    )


@router.post("/convert/{target_format}", response_model=ConversionResponse)
async def convert_file(
    target_format: str,
    filename: str = Form(...),
):
    """Convert an uploaded PDF to the specified format.

    Supported target_format values: docx, xlsx, excel, png, jpg,
    image, txt, text, html
    """
    target = target_format.lower()

    if target not in CONVERSION_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{target_format}'. "
                   f"Supported: {', '.join(CONVERSION_MAP.keys())}",
        )

    pdf_path = str(UPLOAD_DIR / filename)
    if not os.path.isfile(pdf_path):
        raise HTTPException(
            status_code=404,
            detail=f"File '{filename}' not found. Upload it first.",
        )

    ext_map = {
        "docx": "docx", "xlsx": "xlsx", "excel": "xlsx",
        "png": "png", "jpg": "jpg", "jpeg": "jpg",
        "image": "png", "txt": "txt", "text": "txt", "html": "html",
    }
    extension = ext_map.get(target, target)
    output_path = get_output_path(filename, extension)

    try:
        converter_func = CONVERSION_MAP[target]
        result_path = converter_func(pdf_path, output_path)

        # Delete the source PDF after successful conversion
        cleanup_file(pdf_path)

        encoded = urllib.parse.quote(Path(result_path).name)
        download_url = f"/api/download/{encoded}"
        return ConversionResponse(
            success=True,
            message=f"PDF converted to {target_format} successfully.",
            output_file=result_path,
            download_url=download_url,
        )

    except ConversionError as e:
        cleanup_file(output_path)
        logger.error(f"Conversion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        cleanup_file(output_path)
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")


@router.get("/download/{filename}")
async def download_file(filename: str):
    """Serve a converted file for download."""
    filepath = OUTPUT_DIR / filename
    if not filepath.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"File '{filename}' not found.",
        )
    return FileResponse(
        path=str(filepath),
        filename=filename,
        media_type="application/octet-stream",
    )


@router.get("/files")
async def list_files():
    """List all uploaded files (most recent first)."""
    files = []
    for f in sorted(UPLOAD_DIR.iterdir(), key=os.path.getmtime, reverse=True):
        if f.is_file():
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "uploaded_at": f.stat().st_mtime,
            })
    return {"files": files}
