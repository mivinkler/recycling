from django import template

register = template.Library()

@register.filter(name='getattr')
def getattr_filter(obj, attr):
    try:
        attr_value = getattr(obj, attr)
        if callable(attr_value):
            return attr_value()
        return attr_value
    except AttributeError:
        return None