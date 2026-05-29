import os
import logging
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

FONTS_DIR = Path(__file__).resolve().parent.parent.parent / "fonts"
FONTS_DIR.mkdir(parents=True, exist_ok=True)

NOTO_SANS_KHMER_URL = (
    "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskhmer/"
    "NotoSansKhmer%5Bwdth%2Cwght%5D.ttf"
)
NOTO_SANS_KHMER_PATH = FONTS_DIR / "NotoSansKhmer.ttf"


def _download_font(url: str, dest: Path) -> bool:
    try:
        logger.info(f"Downloading font from {url} ...")
        urllib.request.urlretrieve(url, dest)
        logger.info(f"Font saved to {dest}")
        return True
    except Exception as e:
        logger.warning(f"Font download failed: {e}")
        return False


def ensure_khmer_font() -> Path | None:
    if NOTO_SANS_KHMER_PATH.is_file() and NOTO_SANS_KHMER_PATH.stat().st_size > 0:
        return NOTO_SANS_KHMER_PATH
    if _download_font(NOTO_SANS_KHMER_URL, NOTO_SANS_KHMER_PATH):
        if NOTO_SANS_KHMER_PATH.is_file() and NOTO_SANS_KHMER_PATH.stat().st_size > 0:
            return NOTO_SANS_KHMER_PATH
    return None
