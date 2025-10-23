from __future__ import annotations
from dataclasses import asdict, dataclass
from decimal import Decimal
import uuid

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from shop.models import Product


# ---------- cart helpers (session) ----------
CART_KEY = "cart_items"

@dataclass
class CartLine:
    id: str                 # uuid for the cart row
    product_id: int
    name_snapshot: str
    price_snapshot: str     # keep as string to avoid float issues when serializing
    qty: int
    thumb: str | None = None

def _get_cart(request):
    return request.session.get(CART_KEY, [])

def _save_cart(request, items):
    request.session[CART_KEY] = items
    request.session.modified = True

def _total(items):
    return sum(Decimal(i["price_snapshot"]) * i["qty"] for i in items)


# ---------- pages ----------
@login_required
@require_GET
def shopping(request):
    items = _get_cart(request)
    subtotal = _total(items)
    ctx = {
        "cart_items": items,
        "subtotal": subtotal,
        "total": subtotal,   # bisa tambah ongkir/tax nanti
    }
    return render(request, "fitur_belanja/shopping.html", ctx)

@login_required
@require_GET
def checkout(request):
    items = _get_cart(request)
    if not items:
        return redirect("fitur_belanja:shopping")
    ctx = {
        "total": _total(items),
    }
    return render(request, "fitur_belanja/checkout.html", ctx)

@login_required
@require_POST
def checkout_success(request):
    # di sini normalnya proses pembayaran. Untuk demo: kosongkan cart
    _save_cart(request, [])
    return render(request, "fitur_belanja/checkout_success.html")


# ---------- mutations ----------
@login_required
@require_POST
def add_to_cart(request):
    """
    Expect: product_id (form-data or JSON), qty (optional, default 1)
    Returns JSON {ok, count, subtotal}
    """
    pid = request.POST.get("product_id")
    qty = request.POST.get("qty") or "1"
    try:
        qty = max(1, int(qty))
    except Exception:
        return HttpResponseBadRequest("qty invalid")

    product = get_object_or_404(Product, pk=pid, status="active")

    # Larang owner menambahkan produknya sendiri (mirip di UI)
    if product.created_by_id and request.user.is_authenticated and product.created_by_id == request.user.id:
        return JsonResponse({"ok": False, "error": "Cannot add your own product."}, status=400)

    items = _get_cart(request)

    # Gabungkan baris jika product_id sama (sesederhana ini)
    merged = False
    for i in items:
        if i["product_id"] == product.id:
            i["qty"] += qty
            merged = True
            break

    if not merged:
        line = CartLine(
            id=str(uuid.uuid4()),
            product_id=product.id,
            name_snapshot=product.name,
            price_snapshot=str(product.final_price),
            qty=qty,
            thumb=product.thumbnail or None,
        )
        items.append(asdict(line))

    _save_cart(request, items)
    return JsonResponse({
        "ok": True,
        "count": sum(i["qty"] for i in items),
        "subtotal": float(_total(items)),
    }, status=201)


@login_required
@require_GET
def remove_from_cart(request, item_id):
    items = [i for i in _get_cart(request) if i["id"] != str(item_id)]
    _save_cart(request, items)
    return redirect("fitur_belanja:shopping")

@login_required
@require_POST
def clear_cart(request):
    _save_cart(request, [])
    return JsonResponse({"ok": True, "count": 0, "subtotal": 0})
