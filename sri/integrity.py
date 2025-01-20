from pathlib import Path
from typing import Optional

from sri.algorithm import Algorithm
from sri.hashers import calculate_hash
from sri.utils import get_static_path


def calculate_integrity(path: Path, algorithm: Optional[Algorithm] = None) -> str:
    if algorithm is None:
        algorithm = Algorithm.get_default()

    return f"{algorithm.value}-{calculate_hash(path, algorithm)}"


def calculate_integrity_of_static(
    static_path: str, algorithm: Optional[Algorithm] = None
) -> str:
    return calculate_integrity(get_static_path(static_path), algorithm)
