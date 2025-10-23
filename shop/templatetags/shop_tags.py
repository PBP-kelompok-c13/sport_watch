
from django import template
from math import floor

register = template.Library()

@register.filter
def price_idr(value):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return value
    return f"Rp {n:,.0f}".replace(",", ".")

@register.simple_tag
def star_rating(avg, size=5):
    """Render bintang dari angka 05 """
    try:
        avg = float(avg or 0)
    except (TypeError, ValueError):
        avg = 0
    full = int(floor(avg))
    half = 1 if (avg - full) >= 0.5 and full < size else 0
    empty = size - full - half
    return "★" * full + ("☆" if half else "") + "☆" * empty
