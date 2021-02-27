import base64
import hashlib
from enum import Enum, unique
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles.finders import find as find_static_file

USE_SRI = getattr(settings, "USE_SRI", not settings.DEBUG)


@unique
class Algorithm(Enum):
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"


HASHERS = {
    Algorithm.SHA256: hashlib.sha256,
    Algorithm.SHA384: hashlib.sha384,
    Algorithm.SHA512: hashlib.sha512,
}
DEFAULT_ALGORITHM = Algorithm(getattr(settings, "SRI_ALGORITHM", Algorithm.SHA256))


@lru_cache()
def calculate_hash(path: Path, algorithm: Algorithm) -> str:
    hasher = HASHERS[algorithm]
    content = path.read_bytes()
    digest = hasher(content).digest()
    return base64.b64encode(digest).decode()


def get_static_path(path: str) -> Path:
    """
    Resolves a path commonly passed to `{% static %}` into a filesystem path
    """
    static_file_path = find_static_file(path)
    if static_file_path is None:
        raise FileNotFoundError(path)
    return Path(static_file_path)


def calculate_integrity(path: Path, algorithm: Algorithm = DEFAULT_ALGORITHM) -> str:
    return "-".join([algorithm.value, calculate_hash(path, algorithm)])


def calculate_integrity_of_static(
    static_path: str, algorithm: Algorithm = DEFAULT_ALGORITHM
) -> str:
    return calculate_integrity(get_static_path(static_path), algorithm)


def attrs_to_str(attrs: dict):
    return " ".join(f'{k}="{v}"' for k, v in sorted(attrs.items()))
