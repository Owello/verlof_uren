from django import template

register = template.Library()


@register.filter(name='subtract')
def substract(value, arg):
    """Lowers the given value with the value of the argument"""
    subtraction = value - arg
    return subtraction
