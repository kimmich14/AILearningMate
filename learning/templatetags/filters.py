from django import template
register = template.Library()

@register.filter
def get(dict_obj, key):
    return dict_obj.get(key)

@register.filter
def split_choices(value):
    return [v.strip() for v in value.split('|')]