from pathlib import Path

from django.contrib.staticfiles.finders import find as find_static_file
from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from django.core.cache.backends.base import InvalidCacheBackendError


def get_static_path(path: str) -> Path:
    """
    Resolves a path commonly passed to `{% static %}` into a filesystem path
    """
    static_file_path = find_static_file(path)
    if static_file_path is None:
        raise FileNotFoundError(path)
    return Path(static_file_path)


def get_cache():
    try:
        return caches["sri"]
    except InvalidCacheBackendError:
        return caches[DEFAULT_CACHE_ALIAS]
