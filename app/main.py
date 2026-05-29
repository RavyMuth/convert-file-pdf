import os
import sys
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Ensure the project root is on sys.path so we can import app.*
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.routes.converter import router as converter_router
from app.utils.file_handler import UPLOAD_DIR, OUTPUT_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pdf_converter.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="PDF Converter API",
    description="Convert PDF files to Word, Excel, Images, Text, and HTML",
    version="1.0.0",
)

# Allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routes under /api
app.include_router(converter_router, prefix="/api", tags=["Conversion"])

# Serve the static frontend at the root
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


@app.on_event("startup")
async def startup():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Upload directory: {UPLOAD_DIR}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info("PDF Converter API started")
