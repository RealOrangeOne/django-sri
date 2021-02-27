import base64
import hashlib
from functools import lru_cache
from pathlib import Path

from sri.algorithm import Algorithm

HASHERS = {
    Algorithm.SHA256: hashlib.sha256,
    Algorithm.SHA384: hashlib.sha384,
    Algorithm.SHA512: hashlib.sha512,
}


@lru_cache()
def calculate_hash(path: Path, algorithm: Algorithm) -> str:
    hasher = HASHERS[algorithm]
    content = path.read_bytes()
    digest = hasher(content).digest()
    return base64.b64encode(digest).decode()
