import os.path
from typing import Optional

from django import template
from django.conf import settings
from django.forms.utils import flatatt
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from sri.algorithm import Algorithm
from sri.integrity import calculate_integrity_of_static

USE_SRI = getattr(settings, "USE_SRI", not settings.DEBUG)

register = template.Library()


def format_attrs(*empty_tag_attrs, **extra_tag_attrs) -> str:
    """
    Flatten and format list and dict params.

    The returned value will be a string with a leading " " that is a
    combination of "name=value" and "name" params:

        ' src="/" defer'
        ' href="/" rel="stylesheet"'

    """
    extra_attrs = flatatt(extra_tag_attrs)
    if empty_tag_attrs:
        empty_attrs = " ".join(empty_tag_attrs)
        return f"{extra_attrs} {empty_attrs}".rstrip()
    return extra_attrs.rstrip()


def sri_js(path: str, *empty_tag_attrs: str, **extra_tag_attrs: str) -> str:
    return script_tag(path, *empty_tag_attrs, **extra_tag_attrs)


def sri_css(path: str, *empty_tag_attrs: str, **extra_tag_attrs: str) -> str:
    extra_tag_attrs.setdefault("rel", "stylesheet")
    extra_tag_attrs.setdefault("type", "text/css")
    return link_tag(path, *empty_tag_attrs, **extra_tag_attrs)


def script_tag(path: str, *empty_tag_attrs: str, **extra_tag_attrs: str) -> str:
    extra_tag_attrs.setdefault("src", static(path))
    return mark_safe(
        f"<script{format_attrs(*empty_tag_attrs, **extra_tag_attrs)}></script>"
    )


def link_tag(path: str, *empty_tag_attrs: str, **extra_tag_attrs: str) -> str:
    extra_tag_attrs.setdefault("href", static(path))
    return mark_safe(f"<link{format_attrs(*empty_tag_attrs, **extra_tag_attrs)}>")


EXTENSIONS = {"js": sri_js, "css": sri_css}


@register.simple_tag
def sri_static(
    path: str,
    *empty_tag_attrs: str,
    algorithm: Optional[str] = None,
    **extra_tag_attrs: str,
) -> str:
    extension = os.path.splitext(path)[1][1:]
    sri_method = EXTENSIONS.get(extension, link_tag)

    algorithm_type = (
        Algorithm(algorithm) if algorithm is not None else Algorithm.get_default()
    )

    if USE_SRI:
        extra_tag_attrs.setdefault("crossorigin", "anonymous")
        extra_tag_attrs["integrity"] = sri_integrity_static(path, algorithm_type)
    return sri_method(path, *empty_tag_attrs, **extra_tag_attrs)


@register.simple_tag
def sri_integrity_static(path: str, algorithm: Optional[str] = None) -> str:
    return calculate_integrity_of_static(
        path, Algorithm(algorithm) if algorithm is not None else Algorithm.get_default()
    )
