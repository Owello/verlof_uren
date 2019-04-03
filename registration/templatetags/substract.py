from django import template

register = template.Library()


@register.filter(name='substract')
def substract(value, arg):
    """Lowers the given value with the value of the argument"""
    substraction = value - arg
    return substraction
