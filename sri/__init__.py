import base64
import hashlib
from pathlib import Path

from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS, InvalidCacheBackendError, caches

from .utils import get_cache_key, get_static_path

__all__ = ["get_sri", "get_sri_of_static"]


HASHERS = {
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
}


def get_default_algorithm() -> str:
    return getattr(settings, "SRI_ALGORITHM", "sha256")


def get_sri(path: Path, algorithm: str | None = None) -> str:
    if algorithm is None:
        algorithm = get_default_algorithm()

    algorithm = algorithm.lower()

    return f"{algorithm}-{calculate_hash(path, algorithm)}"


def get_sri_of_static(
    static_path: str, algorithm: str | None = None
) -> str:
    return get_sri(get_static_path(static_path), algorithm)


def calculate_hash(path: Path, algorithm: str) -> str:
    if algorithm not in HASHERS:
        raise ValueError(f"Unknown algorithm: {algorithm}")

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
