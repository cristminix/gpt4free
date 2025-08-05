from __future__ import annotations

import re
from urllib.parse import unquote
import os

from .cookies import get_cookies_dir

def secure_filename(filename: str) -> str:
    """
    Input: " My File!@#.txt " → Output: "My_File.txt"
    Fungsi ini mencegah masalah keamanan (seperti path traversal) dan memastikan kompatibilitas nama file.
    """
    if filename is None:
        return None
    # Keep letters, numbers, basic punctuation and all Unicode chars
    filename = re.sub(
        r'[^\w.,_+-]+',
        '_',
        unquote(filename).strip(),
        flags=re.UNICODE
    )
    encoding = 'utf-8'
    max_length = 100
    encoded = filename.encode(encoding)[:max_length]
    decoded = encoded.decode(encoding, 'ignore')
    return decoded.strip(".,_+-")

def get_bucket_dir(*parts):
    return os.path.join(get_cookies_dir(), "buckets", *[secure_filename(part) for part in parts if part])
