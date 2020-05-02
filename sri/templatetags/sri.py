import os.path

from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from sri.utils import calculate_integrity, get_static_path

register = template.Library()


@register.simple_tag
def sri_js(path):
    return mark_safe(
        "<script src='{src}' integrity='{integrity}'></script>".format(
            src=static(path), integrity=calculate_integrity(get_static_path(path))
        )
    )


@register.simple_tag
def sri_css(path):
    return mark_safe(
        "<link rel='stylesheet' href='{src}' integrity='{integrity}'/>".format(
            src=static(path), integrity=calculate_integrity(get_static_path(path))
        )
    )


EXTENSIONS = {"js": sri_js, "css": sri_css}


@register.simple_tag
def sri(path):
    extension = os.path.splitext(path)[1][1:]
    return EXTENSIONS[extension](path)
