from __future__ import annotations

import base64
import io
from typing import Optional

from PIL import Image


def decode_thumbnail(b64_str: Optional[str]) -> Optional[Image.Image]:
    """Decode a base64 string to an image."""
    if not b64_str:
        return None
    try:
        data = base64.b64decode(b64_str)
        return Image.open(io.BytesIO(data))
    except Exception:
        return None
