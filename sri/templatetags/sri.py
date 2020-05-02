import os.path
from collections import OrderedDict

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


@register.simple_tag
def sri_js(path, algorithm=DEFAULT_ALGORITHM):
    attrs = OrderedDict([("type", "text/javascript"), ("src", static(path))])
    if USE_SRI:
        attrs["integrity"] = calculate_integrity(get_static_path(path), algorithm)
        attrs["crossorigin"] = "anonymous"
    return mark_safe(f"<script {attrs_to_str(attrs)}></script>")


@register.simple_tag
def sri_css(path, algorithm=DEFAULT_ALGORITHM):
    attrs = OrderedDict(
        [("rel", "stylesheet"), ("type", "text/css"), ("href", static(path))]
    )
    if USE_SRI:
        attrs["integrity"] = calculate_integrity(get_static_path(path), algorithm)
        attrs["crossorigin"] = "anonymous"
    return mark_safe(f"<link {attrs_to_str(attrs)} />")


EXTENSIONS = {"js": sri_js, "css": sri_css}


@register.simple_tag
def sri(path, algorithm=DEFAULT_ALGORITHM):
    extension = os.path.splitext(path)[1][1:]
    return EXTENSIONS[extension](path, algorithm)
