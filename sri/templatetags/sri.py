import os.path

from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from sri.utils import (
    DEFAULT_ALGORITHM,
    USE_SRI,
    attrs_to_str,
    calculate_integrity,
    get_static_path,
)

register = template.Library()


def sri_js(attrs: dict, path: str, algorithm: str):
    attrs.update({"type": "text/javascript", "src": static(path)})
    return mark_safe(f"<script {attrs_to_str(attrs)}></script>")


def sri_css(attrs: dict, path: str, algorithm: str):
    attrs.update({"rel": "stylesheet", "type": "text/css", "href": static(path)})
    return mark_safe(f"<link {attrs_to_str(attrs)}/>")


EXTENSIONS = {"js": sri_js, "css": sri_css}


@register.simple_tag
def sri_static(path, algorithm=DEFAULT_ALGORITHM):
    extension = os.path.splitext(path)[1][1:]
    sri_method = EXTENSIONS[extension]
    attrs = {}
    if USE_SRI:
        attrs.update(
            {
                "integrity": calculate_integrity(get_static_path(path), algorithm),
                "crossorigin": "anonymous",
            }
        )
    return sri_method(attrs, path, algorithm)


@register.simple_tag
def sri_integrity_static(path, algorithm=DEFAULT_ALGORITHM):
    return calculate_integrity(get_static_path(path), algorithm)
