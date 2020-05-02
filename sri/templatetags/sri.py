from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def sri_js(url):
    return mark_safe("<script src='{src}'></script>".format(src=static(url)))


@register.simple_tag
def sri_css(url):
    return mark_safe("<link rel='stylesheet' href='{src}' />".format(src=static(url)))
