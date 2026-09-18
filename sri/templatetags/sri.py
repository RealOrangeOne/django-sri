from django import template
from django.conf import settings
from django.forms.utils import flatatt

from sri.algorithm import Algorithm
from sri.integrity import calculate_integrity_of_static

register = template.Library()


@register.simple_tag
def sri_integrity(path: str, algorithm: str | Algorithm | None = None) -> str:
    return calculate_integrity_of_static(
        path, Algorithm(algorithm) if algorithm is not None else Algorithm.get_default()
    )


@register.simple_tag
def sri_attrs(path: str, algorithm: str | Algorithm | None = None) -> str:
    if not getattr(settings, "USE_SRI", not settings.DEBUG):
        return ""
    return flatatt(
        {
            "integrity": sri_integrity(path, algorithm),
            "crossorigin": "anonymous",
        }
    )
