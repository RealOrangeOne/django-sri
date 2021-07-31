from enum import Enum, unique

@unique
class JsAttribute(Enum):
    DEFER = "defer"
    ASYNC = "async"
