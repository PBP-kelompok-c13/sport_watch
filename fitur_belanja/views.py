# fitur_belanja/views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.db import transaction
from shop.models import Product
from .models import CartItem
from django.contrib import messages
from django.shortcuts import redirect, render
from django.db import transaction
from .utils import cart_from_request
import json
import uuid

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
    # Baca input: dukung form-encoded & JSON
    if request.headers.get("Content-Type", "").startswith("application/json"):
        try:
            payload = json.loads(request.body.decode() or "{}")
        except json.JSONDecodeError:
            payload = {}
        raw_pid = payload.get("product_id")
        qty = int(payload.get("qty", 1) or 1)
    else:
        raw_pid = request.POST.get("product_id")
        qty = int(request.POST.get("qty", "1") or 1)

    # Validasi UUID
    try:
        pid = uuid.UUID(str(raw_pid))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Invalid product ID"}, status=400)

    product = get_object_or_404(Product, id=pid)

    
    if (request.user.is_authenticated and product.created_by_id == request.user.id) or not product.in_stock:
        return JsonResponse({"ok": False, "error": "Not allowed"}, status=400)

    cart = cart_from_request(request)
    with transaction.atomic():
        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=cart, product=product,
            defaults={"qty": qty, "unit_price": product.final_price},
        )
        if not created:
            item.qty += qty
            item.unit_price = product.final_price
            item.save(update_fields=["qty", "unit_price"])

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
    return JsonResponse({"ok": True, "cart_count": cart.item_count})

@require_POST
def clear_cart(request):
    cart = cart_from_request(request)
    cart.items.all().delete()
    return JsonResponse({"ok": True, "cart_count": 0})



def _cart_totals(cart):
    items = (CartItem.objects
             .select_related("product", "cart")
             .filter(cart=cart)
             .order_by("id"))
    subtotal = sum(i.subtotal for i in items)
    shipping = 0
    total = subtotal + shipping
    return items, subtotal, shipping, total

def checkout(request):
    cart = cart_from_request(request)
    items, subtotal, shipping, total = _cart_totals(cart)

    
    if not items.exists():
        messages.info(request, "Keranjang masih kosong.")
        return redirect("fitur_belanja:shopping")

    if request.method == "POST":
     
        try:
            with transaction.atomic():
               
                for it in items.select_related("product"):
                    p = it.product

                  
                    if request.user.is_authenticated and p.created_by_id == request.user.id:
                        raise ValueError(f"Tidak boleh membeli produk sendiri: {p.name}")

                    if p.status != "active" or it.qty > p.stock:
                        raise ValueError(f"Stok tidak cukup untuk {p.name} (tersisa {p.stock})")

                   
                    p.stock -= it.qty
                    p.total_sold += it.qty
                    p.save(update_fields=["stock", "total_sold", "updated_at"])

                cart.items.all().delete()

            messages.success(request, "Pembayaran berhasil. Terima kasih! 🎉")
            
            return redirect("shop:list")

        except ValueError as e:
            messages.error(request, str(e))
          
            return render(request, "fitur_belanja/checkout.html", {
                "items": items,
                "subtotal": subtotal,
                "shipping": shipping,
                "total": total,
            })

  
    return render(request, "fitur_belanja/checkout.html", {
        "items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
    })