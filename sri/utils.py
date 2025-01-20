import logging
import os
from pathlib import Path

from django.contrib.staticfiles.finders import find as find_static_file
from django.contrib.staticfiles.storage import staticfiles_storage

logger = logging.getLogger(__name__)


def get_static_path(path: str) -> Path:
    """
    Resolves a path commonly passed to `{% static %}` into a filesystem path
    """

    if hasattr(staticfiles_storage, "stored_name"):
        path = staticfiles_storage.stored_name(path)

    collected_file_path = staticfiles_storage.path(path)
    if os.path.exists(collected_file_path):
        return Path(collected_file_path)

    logger.debug("File not found in staticfiles_storage - checking source files")
    source_static_file_path = find_static_file(path)
    if source_static_file_path is not None:
        return Path(source_static_file_path)

    raise FileNotFoundError(path)
