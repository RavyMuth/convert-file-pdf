from pydantic import BaseModel
from typing import Optional


class ConversionResponse(BaseModel):
    success: bool
    message: str
    output_file: Optional[str] = None
    download_url: Optional[str] = None
    error: Optional[str] = None


class UploadResponse(BaseModel):
    success: bool
    filename: str
    filepath: str
    message: str
