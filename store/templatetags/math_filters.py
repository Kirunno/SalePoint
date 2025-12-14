from django import template

register = template.Library()

@register.filter
def mul(a, b):
    try:
        return int(a) * int(b)
    except:
        return 0
