import base64
import hashlib
from enum import Enum, unique
from pathlib import Path

from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS, InvalidCacheBackendError, caches

from .utils import get_cache_key, get_static_path

__all__ = ["calculate_integrity", "calculate_integrity_of_static", "Algorithm"]


@unique
class Algorithm(Enum):
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"

    @classmethod
    def get_default(cls) -> "Algorithm":
        return Algorithm(getattr(settings, "SRI_ALGORITHM", Algorithm.SHA256))


HASHERS = {
    Algorithm.SHA256: hashlib.sha256,
    Algorithm.SHA384: hashlib.sha384,
    Algorithm.SHA512: hashlib.sha512,
}


def calculate_integrity(path: Path, algorithm: Algorithm | None = None) -> str:
    if algorithm is None:
        algorithm = Algorithm.get_default()

    return f"{algorithm.value}-{calculate_hash(path, algorithm)}"


def calculate_integrity_of_static(
    static_path: str, algorithm: Algorithm | None = None
) -> str:
    return calculate_integrity(get_static_path(static_path), algorithm)


def calculate_hash(path: Path, algorithm: "Algorithm") -> str:
    try:
        cache = caches["sri"]
    except InvalidCacheBackendError:
        cache = caches[DEFAULT_CACHE_ALIAS]

    cache_key = get_cache_key(path, algorithm)
    file_hash: str | None = cache.get(cache_key)
    if file_hash is None:
        # Cache miss, do the calculation
        with path.open("rb") as f:
            hasher = hashlib.file_digest(f, HASHERS[algorithm])
        file_hash = base64.b64encode(hasher.digest()).decode()
        cache.set(cache_key, file_hash)
    return file_hash
