import os
from pathlib import Path

from django.contrib.staticfiles.finders import find as find_static_file
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from django.core.cache.backends.base import InvalidCacheBackendError


def get_static_path(path: str) -> Path:
    """
    Resolves a path commonly passed to `{% static %}` into a filesystem path
    """

    if hasattr(staticfiles_storage, "stored_name"):
        path = staticfiles_storage.stored_name(path)
        collected_file_path = staticfiles_storage.path(path)
        if os.path.exists(collected_file_path):
            return Path(collected_file_path)

    source_static_file_path = find_static_file(path)
    if source_static_file_path is not None:
        return Path(source_static_file_path)

    raise FileNotFoundError(path)


def get_cache():
    try:
        return caches["sri"]
    except InvalidCacheBackendError:
        return caches[DEFAULT_CACHE_ALIAS]
