import base64
import hashlib

from django.conf import settings
from django.utils._os import safe_join

HASHERS = {"sha256": hashlib.sha256, "sha384": hashlib.sha384, "sha512": hashlib.sha512}
DEFAULT_ALGORITHM = getattr(settings, "SRI_ALGORITHM", "sha256")


def calculate_hash(path: str, algorithm: str) -> str:
    hasher = HASHERS[algorithm]
    with open(path, "r") as f:
        content = f.read()
    digest = hasher(content.encode()).digest()
    return base64.b64encode(digest).decode()


def get_static_path(path) -> str:
    """
    Resolves a path commonly passed to `{% static %}` into a filesystem path
    """
    return safe_join(settings.STATIC_ROOT, path)


def calculate_integrity(path: str, algorithm: str = DEFAULT_ALGORITHM) -> str:
    return "-".join([algorithm, calculate_hash(path, algorithm)])
