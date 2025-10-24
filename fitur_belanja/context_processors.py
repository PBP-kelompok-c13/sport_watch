# fitur_belanja/context_processors.py
from .utils import cart_from_request

def cart_badge(request):
    cart = cart_from_request(request)
    return {"cart_count": cart.item_count if cart else 0}
