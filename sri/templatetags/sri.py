from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from sri.utils import calculate_integrity, get_static_path

register = template.Library()


@register.simple_tag
def sri_js(url):
    return mark_safe(
        "<script src='{src}' integrity='{integrity}'></script>".format(
            src=static(url), integrity=calculate_integrity(get_static_path(url))
        )
    )


@register.simple_tag
def sri_css(url):
    return mark_safe(
        "<link rel='stylesheet' href='{src}' integrity='{integrity}'/>".format(
            src=static(url), integrity=calculate_integrity(get_static_path(url))
        )
    )
