import os.path
from typing import Optional

from django import template
from django.conf import settings
from django.forms.utils import flatatt
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from sri.algorithm import DEFAULT_ALGORITHM, Algorithm
from sri.extra_attribute import ExtraAttribute
from sri.integrity import calculate_integrity_of_static

USE_SRI = getattr(settings, "USE_SRI", not settings.DEBUG)

register = template.Library()


def sri_js(attrs: dict, path: str, algorithm: Algorithm, **kwargs):
    if 'extra_attr' in kwargs:
        extra_attr = kwargs['extra_attr']
        if ExtraAttribute(extra_attr) in (ExtraAttribute.PRELOAD, ExtraAttribute.PREFETCH):
            attrs.update({"rel": extra_attr, "href": static(path), "as": "script"})
        elif ExtraAttribute(extra_attr) in (ExtraAttribute.DEFER, ExtraAttribute.ASYNC):
            attrs.update({extra_attr: True})
            attrs.update({"type": "text/javascript", "src": static(path)})
    else:
        attrs.update({"type": "text/javascript", "src": static(path)})
    return mark_safe(f"<script{flatatt(attrs)}></script>")


def sri_css(attrs: dict, path: str, algorithm: Algorithm, **kwargs):
    if 'extra_attr' in kwargs:
        extra_attr = kwargs['extra_attr']
        if ExtraAttribute(extra_attr) in (ExtraAttribute.PRELOAD, ExtraAttribute.PREFETCH):
            attrs.update({"rel": extra_attr, "href": static(path), "as": "style"})
    else:
        attrs.update({"rel": "stylesheet", "type": "text/css", "href": static(path)})
    return mark_safe(f"<link{flatatt(attrs)}/>")


EXTENSIONS = {"js": sri_js, "css": sri_css}


@register.simple_tag
def sri_static(path: str, algorithm: Optional[str] = None, **kwargs):
    algorithm_type = Algorithm(algorithm or DEFAULT_ALGORITHM)
    extension = os.path.splitext(path)[1][1:]
    sri_method = EXTENSIONS[extension]
    attrs = {}
    if USE_SRI:
        attrs.update(
            {
                "integrity": calculate_integrity_of_static(path, algorithm_type),
                "crossorigin": "anonymous",
            }
        )
    return sri_method(attrs, path, algorithm_type, **kwargs)


@register.simple_tag
def sri_integrity_static(path: str, algorithm: Optional[str] = None, **kwargs):
    return calculate_integrity_of_static(
        path, Algorithm(algorithm or DEFAULT_ALGORITHM)
    )
