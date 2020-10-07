
from django.template import Library
from decimal import Decimal

register = Library()


@register.filter(name = 'times')
def times(number):
    return range(int(number))


