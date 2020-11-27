import base64
import hashlib
from functools import lru_cache

from django.conf import settings
from django.contrib.staticfiles.finders import find as find_static_file

HASHERS = {"sha256": hashlib.sha256, "sha384": hashlib.sha384, "sha512": hashlib.sha512}
DEFAULT_ALGORITHM = getattr(settings, "SRI_ALGORITHM", "sha256")

USE_SRI = getattr(settings, "USE_SRI", not settings.DEBUG)


@lru_cache()
def calculate_hash(path: str, algorithm: str) -> str:
    hasher = HASHERS[algorithm]
    with open(path, "r") as f:
        content = f.read()
    digest = hasher(content.encode()).digest()
    return base64.b64encode(digest).decode()


def get_static_path(path: str) -> str:
    """
    Resolves a path commonly passed to `{% static %}` into a filesystem path
    """
    static_file_path = find_static_file(path)
    if static_file_path is None:
        raise FileNotFoundError(path)
    return static_file_path


def calculate_integrity(path: str, algorithm: str = DEFAULT_ALGORITHM) -> str:
    return "-".join([algorithm, calculate_hash(path, algorithm)])


def attrs_to_str(attrs: dict):
    return " ".join(f'{k}="{v}"' for k, v in sorted(attrs.items()))
