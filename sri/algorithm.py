from enum import Enum, unique

from django.conf import settings


@unique
class Algorithm(Enum):
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"


DEFAULT_ALGORITHM = Algorithm(getattr(settings, "SRI_ALGORITHM", Algorithm.SHA256))
