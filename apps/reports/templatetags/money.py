from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def tl(cents):
    value = Decimal(cents) / Decimal("100")
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".") + " ₺"
