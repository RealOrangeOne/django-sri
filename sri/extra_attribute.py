from enum import Enum, unique

@unique
class ExtraAttribute(Enum):
    DEFER = "defer"
    ASYNC = "async"
    PRELOAD = "preload"
    PREFETCH = "prefetch"
