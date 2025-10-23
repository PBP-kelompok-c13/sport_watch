# from django.shortcuts import render
# from django.http import HttpResponse


# def shopping_view(request):
#     return render(request, 'fitur_belanja/shopping.html')
from django.shortcuts import render, redirect
from .models import Cart, CartItem, Order, Payment
from django.contrib.auth.decorators import login_required

def get_cart(request):
    """Ambil cart untuk user login atau session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key or request.session.save()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart

def shopping_view(request):
    cart = get_cart(request)
    cart_items = cart.items.all()
    subtotal = sum(item.price_snapshot * item.qty for item in cart_items)

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': subtotal,  # nanti bisa tambahkan tax/diskon
    }
    return render(request, 'fitur_belanja/shopping.html', context)

def add_to_cart(request, product_id):
    cart = get_cart(request)
    # Simulasi produk (nanti bisa ambil dari model Product)
    name = "Produk Dummy"
    price = 100000

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_id=product_id,
        defaults={'name_snapshot': name, 'price_snapshot': price, 'qty': 1},
    )
    if not created:
        item.qty += 1
        item.save()
    return redirect('fitur_belanja:shopping')

def remove_from_cart(request, item_id):
    CartItem.objects.filter(id=item_id).delete()
    return redirect('fitur_belanja:shopping')

@login_required
def checkout_view(request):
    cart = get_cart(request)
    cart_items = cart.items.all()
    total = sum(item.price_snapshot * item.qty for item in cart_items)

    if request.method == 'POST':
        # Simulasi pembayaran dummy
        order = Order.objects.create(
            user=request.user,
            subtotal=total,
            total=total,
            status='PAID',
        )
        Payment.objects.create(order=order, status='SUCCESS', amount=total)
        cart.items.all().delete()
        return render(request, 'fitur_belanja/checkout_success.html', {'order': order})

    return render(request, 'fitur_belanja/checkout.html', {'cart_items': cart_items, 'total': total})


