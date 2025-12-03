# fitur_belanja/views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.db import transaction
from shop.models import Product
from .models import CartItem
from .utils import cart_from_request
import json

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
    try:
        if request.content_type.startswith('application/json'):
            data = json.loads(request.body)
            pid = data.get("product_id")
            qty = data.get("qty", 1)
        else:
            pid = request.POST.get("product_id")
            qty = request.POST.get("qty", 1)

        qty = int(qty)

    except (ValueError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid data"}, status=400)

    if not pid:
        return JsonResponse({"ok": False, "error": "Missing product_id"}, status=400)

    # Product.id adalah UUID → langsung pakai tanpa cast
    product = get_object_or_404(Product, id=pid)


    # owner tidak boleh beli produknya sendiri
    if request.user.is_authenticated and product.created_by_id == request.user.id:
        return JsonResponse({"ok": False, "error": "Cannot buy your own product"}, status=400)

    # stock check
    if not product.in_stock:
        return JsonResponse({"ok": False, "error": "Product out of stock"}, status=400)

    cart = cart_from_request(request)

    # simpan item
    with transaction.atomic():
        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=cart,
            product=product,
            defaults={"qty": 0, "unit_price": product.final_price}
        )
        item.qty += qty
        item.unit_price = product.final_price
        item.save()

    return JsonResponse({
        "ok": True,
        "cart_count": cart.item_count,
        "message": "Success add to cart"
    })

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
    item_id = request.POST.get("item_id")

    cart = cart_from_request(request)
    item = CartItem.objects.filter(id=item_id, cart=cart).first()

    if item:
        item.delete()

    # setelah delete, total dihitung ulang otomatis dari property
    return JsonResponse({"success": True})


@require_POST
def clear_cart(request):
    cart = cart_from_request(request)
    cart.items.all().delete()
    return JsonResponse({"ok": True, "cart_count": 0})