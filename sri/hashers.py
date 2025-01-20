import base64
import hashlib
from functools import lru_cache
from pathlib import Path

from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from django.core.cache.backends.base import InvalidCacheBackendError

from sri.algorithm import Algorithm

HASHERS = {
    Algorithm.SHA256: hashlib.sha256,
    Algorithm.SHA384: hashlib.sha384,
    Algorithm.SHA512: hashlib.sha512,
}

READ_BUFFER_SIZE = 2**18  # 256k - matches `hashlib.file_digest`


def calculate_hash(path: Path, algorithm: Algorithm) -> str:
    try:
        cache = caches["sri"]
    except InvalidCacheBackendError:
        cache = caches[DEFAULT_CACHE_ALIAS]

    cache_key = get_cache_key(path, algorithm)
    file_hash = cache.get(cache_key)
    if file_hash is None:
        # Cache miss, do the calculation
        with path.open("rb") as f:
            if hasattr(hashlib, "file_digest"):
                hasher = hashlib.file_digest(f, HASHERS[algorithm])
            else:
                hasher = HASHERS[algorithm]()
                while True:
                    data = f.read(READ_BUFFER_SIZE)
                    if not data:
                        break
                    hasher.update(data)
        file_hash = base64.b64encode(hasher.digest()).decode()
        cache.set(cache_key, file_hash)
    return file_hash


@lru_cache(maxsize=None)
def get_cache_key(path: Path, algorithm: Algorithm) -> str:
    path_hash = hashlib.sha1(str(path).encode(), usedforsecurity=False).hexdigest()
    return f"sri-{path_hash}-{algorithm.value}"
