from django.conf import settings

from .utils import get_sri_for_file, get_static_path

__all__ = ["get_sri", "get_sri_of_static"]


def get_default_algorithm() -> str:
    return getattr(settings, "SRI_ALGORITHM", "sha256")


def get_sri(path: str, algorithm: str | None = None) -> str:
    if algorithm is None:
        algorithm = get_default_algorithm()

    algorithm = algorithm.lower()

    return f"{algorithm}-{get_sri_for_file(path, algorithm)}"


def get_sri_of_static(static_path: str, algorithm: str | None = None) -> str:
    return get_sri(get_static_path(static_path), algorithm)
