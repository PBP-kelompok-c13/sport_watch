# fitur_belanja/views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.db import transaction
from shop.models import Product
from .models import CartItem
from .utils import cart_from_request

def shopping(request):
    cart = cart_from_request(request)
    items = (
        CartItem.objects
        .select_related("product", "cart")
        .filter(cart=cart)
        .order_by("id")
    )
    subtotal = sum(i.subtotal for i in items)
    shipping = 0  # demo: gratis/flat
    total = subtotal + shipping
    return render(request, "fitur_belanja/cart.html", {
        "cart": cart,
        "items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
    })

@require_POST
def add_to_cart(request):
    import uuid
    pid = request.POST.get("product_id")
    qty = int(request.POST.get("qty", "1") or 1)

    try:
        pid = uuid.UUID(pid)
    except (ValueError, TypeError):
        return JsonResponse({"ok": False, "error": "Invalid product ID"}, status=400)

    product = get_object_or_404(Product, id=pid)

    if (request.user.is_authenticated and product.created_by_id == request.user.id) or not product.in_stock:
        return JsonResponse({"ok": False, "error": "Not allowed"}, status=400)

    cart = cart_from_request(request)
    
    with transaction.atomic():
        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=cart, 
            product=product,
            defaults={"qty": qty, "unit_price": product.final_price}  # ✅ qty: qty (bukan 0)
        )
        
        # ✅ Hanya tambah qty jika item SUDAH ADA
        if not created:
            item.qty += qty
            item.unit_price = product.final_price
            item.save()

    return JsonResponse({"ok": True, "cart_count": cart.item_count})

@require_POST
def update_qty(request):
    item_id = int(request.POST.get("item_id", "0"))
    qty = max(1, int(request.POST.get("qty", "1")))
    cart = cart_from_request(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.qty = qty
    item.save()
    return JsonResponse({"ok": True, "subtotal": float(item.subtotal)})

@require_POST
def remove_item(request):
    item_id = int(request.POST.get("item_id", "0"))
    cart = cart_from_request(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()

    #Hitung ulang subtotal dan total setelah item dihapus
    items = CartItem.objects.filter(cart=cart)
    subtotal = sum(i.subtotal for i in items)
    shipping = 0
    total = subtotal + shipping

    return JsonResponse({
        "ok": True,
        "cart_count": cart.item_count,
        "subtotal": subtotal,
        "total": total,
    })


@require_POST
def clear_cart(request):
    cart = cart_from_request(request)
    cart.items.all().delete()
    return JsonResponse({"ok": True, "cart_count": 0})
