from pathlib import Path

from sri.algorithm import DEFAULT_ALGORITHM, Algorithm
from sri.hashers import calculate_hash
from sri.utils import get_static_path


def calculate_integrity(path: Path, algorithm: Algorithm = DEFAULT_ALGORITHM) -> str:
    return f"{algorithm.value}-{calculate_hash(path, algorithm)}"


def calculate_integrity_of_static(
    static_path: str, algorithm: Algorithm = DEFAULT_ALGORITHM
) -> str:
    return calculate_integrity(get_static_path(static_path), algorithm)
