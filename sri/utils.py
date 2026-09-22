import base64
import hashlib
import os
from functools import lru_cache

from django.conf import settings
from django.contrib.staticfiles.finders import find as find_static_file
from django.contrib.staticfiles.storage import ManifestFilesMixin, staticfiles_storage

HASHERS = {
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
}


def get_static_path(path: str) -> str:
    """
    Resolves a path commonly passed to `{% static %}` into a filesystem path
    """

    if isinstance(staticfiles_storage, ManifestFilesMixin):
        path = staticfiles_storage.stored_name(path)

    collected_file_path = staticfiles_storage.path(path)
    if os.path.exists(collected_file_path):
        return collected_file_path

    source_static_file_path = find_static_file(path)
    if source_static_file_path is not None:
        return source_static_file_path

    raise FileNotFoundError(path)


def get_sri_for_file(path: str, algorithm: str) -> str:
    # If not using SRI, don't cache to avoid issues with changing static files
    if getattr(settings, "USE_SRI", not settings.DEBUG):
        return _cached_get_sri_for_file(path, algorithm)
    return _get_sri_for_file(path, algorithm)


def _get_sri_for_file(path: str, algorithm: str) -> str:
    if algorithm not in HASHERS:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    with open(path, mode="rb") as f:
        hasher = hashlib.file_digest(f, HASHERS[algorithm])

    return base64.b64encode(hasher.digest()).decode()


_cached_get_sri_for_file = lru_cache(maxsize=1000)(_get_sri_for_file)
