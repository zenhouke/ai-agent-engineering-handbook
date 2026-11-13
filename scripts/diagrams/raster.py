"""Render precise architecture drawings as PNGs without spawning an executable."""

import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path

import resvg_py

ROOT = Path(__file__).resolve().parents[2]
CACHE_PATH = ROOT / ".artifacts/raster-cache.json"


@lru_cache(maxsize=1)
def font() -> tuple[Path, str]:
    path = Path(
        os.environ.get(
            "HANDBOOK_FONT_FILE",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        )
    )
    if not path.is_file():
        raise RuntimeError(
            "PNG export needs Noto Sans CJK. Use Docker, install fonts-noto-cjk, "
            "or set HANDBOOK_FONT_FILE to the installed font file."
        )
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def cache() -> dict:
    try:
        return json.loads(CACHE_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def save_png(content: str, target: Path) -> None:
    font_path, font_hash = font()
    signature = hashlib.sha256(
        (content + font_hash + resvg_py.__version__ + ":2x").encode()
    ).hexdigest()
    key = target.relative_to(ROOT).as_posix()
    previous = cache().get(key, {})
    if (
        previous.get("source") == signature
        and target.is_file()
        and previous.get("png") == hashlib.sha256(target.read_bytes()).hexdigest()
    ):
        return
    png = resvg_py.svg_to_bytes(
        svg_string=content,
        zoom=2.0,
        skip_system_fonts=True,
        font_files=[str(font_path)],
        font_family="Noto Sans CJK SC",
    )
    target.write_bytes(png)
    cache()[key] = {"source": signature, "png": hashlib.sha256(png).hexdigest()}


def flush_cache() -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache(), sort_keys=True) + "\n")
