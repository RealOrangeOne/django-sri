from pathlib import Path

from django.contrib.staticfiles.finders import find as find_static_file


def get_static_path(path: str) -> Path:
    """
    Resolves a path commonly passed to `{% static %}` into a filesystem path
    """
    static_file_path = find_static_file(path)
    if static_file_path is None:
        raise FileNotFoundError(path)
    return Path(static_file_path)


def attrs_to_str(attrs: dict):
    return " ".join(f'{k}="{v}"' for k, v in sorted(attrs.items()))
