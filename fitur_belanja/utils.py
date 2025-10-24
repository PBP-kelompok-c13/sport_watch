# fitur_belanja/utils.py
from .models import Cart

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # merge guest cart by session if ada
        sk = request.session.session_key
        if sk:
            try:
                g = Cart.objects.get(session_key=sk, user__isnull=True)
                for it in g.items.all():
                    tgt, _ = cart.items.get_or_create(product=it.product, defaults={"qty":0,"unit_price":it.unit_price})
                    tgt.qty += it.qty
                    tgt.save(update_fields=["qty"])
                g.delete()
            except Cart.DoesNotExist:
                pass
        return cart
    # guest
    if not request.session.session_key:
        request.session.create()
    return Cart.objects.get_or_create(session_key=request.session.session_key)[0]

from .models import Cart
from django.utils.crypto import get_random_string

def cart_from_request(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    # guest cart by session_key
    if not request.session.session_key:
        request.session.save()
    sk = request.session.session_key or get_random_string(32)
    request.session["cart_sk"] = sk
    cart, _ = Cart.objects.get_or_create(session_key=sk, user=None)
    return cart
