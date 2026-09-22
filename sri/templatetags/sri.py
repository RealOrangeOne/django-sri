from django import template
from django.conf import settings
from django.forms.utils import flatatt

from sri import get_sri_of_static

register = template.Library()


@register.simple_tag
def sri_integrity(path: str, algorithm: str | None = None) -> str:
    return get_sri_of_static(path, algorithm)


@register.simple_tag
def sri_attrs(path: str, algorithm: str | None = None) -> str:
    if not getattr(settings, "USE_SRI", not settings.DEBUG):
        return ""
    return flatatt(
        {
            "integrity": sri_integrity(path, algorithm),
            "crossorigin": "anonymous",
        }
    )
