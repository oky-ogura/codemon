import os

from django import template

register = template.Library()


@register.filter
def basename(value: object) -> str:
    if value is None:
        return ""
    try:
        return os.path.basename(str(value))
    except Exception:
        return str(value)
