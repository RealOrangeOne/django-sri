from __future__ import annotations

import os.path

from django import template
from django.conf import settings
from django.forms.utils import flatatt
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from sri.algorithm import DEFAULT_ALGORITHM, Algorithm
from sri.integrity import calculate_integrity_of_static


USE_SRI = getattr(settings, "USE_SRI", not settings.DEBUG)

register = template.Library()


def format_attrs(*simple_attrs, **complex_attrs) -> str:
    """
    Flatten and format list and dict params.

    The returned value will be a string with a leading " " that is a
    combination of "name=value" and "name" params:

        ' src="/" defer'
        ' href="/" rel="stylesheet"'

    """
    complex = flatatt(complex_attrs)
    if simple_attrs:
        simple = " ".join(simple_attrs)
        return f"{complex} {simple}".rstrip()
    return complex.rstrip()


def sri_js(path: str, *simple_attrs: str, **complex_attrs: str) -> str:
    complex_attrs.setdefault("src", static(path))
    return mark_safe(f"<script{format_attrs(*simple_attrs, **complex_attrs)}></script>")


def sri_css(path: str, *simple_attrs: str, **complex_attrs: str) -> str:
    complex_attrs.setdefault("rel", "stylesheet")
    complex_attrs.setdefault("type", "text/css")
    complex_attrs.setdefault("href", static(path))
    return mark_safe(f"<link{format_attrs(*simple_attrs, **complex_attrs)}>")


EXTENSIONS = {"js": sri_js, "css": sri_css}


@register.simple_tag
def sri_static(
    path: str, *simple_attrs: str, algorithm: str | None = None, **complex_attrs: str
) -> str:
    extension = os.path.splitext(path)[1][1:]
    sri_method = EXTENSIONS[extension]
    if USE_SRI:
        complex_attrs.setdefault("crossorigin", "anonymous")
        complex_attrs["integrity"] = sri_integrity_static(path, algorithm)
    return sri_method(path, *simple_attrs, **complex_attrs)


@register.simple_tag
def sri_integrity_static(path: str, algorithm: str | None = None) -> str:
    algorithm_type = Algorithm(algorithm or DEFAULT_ALGORITHM)
    return calculate_integrity_of_static(path, algorithm_type)
