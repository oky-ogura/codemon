from django import template

register = template.Library()

@register.filter
def css_class_to_html(value):
    """CSSクラス名のドットをスペースに変換
    例: 'flower.neko' -> 'flower neko'
    """
    if value:
        return value.replace('.', ' ')
    return value
