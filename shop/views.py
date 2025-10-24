from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib.auth.decorators import login_required,  permission_required
from django.core.paginator import Paginator
from django.db.models import Q, F
from .models import Product, Category, Review
from .forms import ReviewForm, ProductForm
from django.views.decorators.http import require_GET, require_POST
from django.utils.timezone import localtime
from django.contrib import messages
from django.urls import reverse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.db.models import Q, F, Avg, Count 
from django.core.exceptions import PermissionDenied
from django.db.models.functions import Coalesce
from django.db.models import DecimalField, F

def product_list(request):
    qs = Product.objects.filter(status="active").select_related("category","brand")
    cat = request.GET.get("category")
    sort = request.GET.get("sort")
    q   = request.GET.get("q")

    if cat: qs = qs.filter(category__slug=cat)
    if q:   qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

    
    qs = qs.annotate(effective_price=Coalesce("sale_price", "price", output_field=DecimalField()))

    if sort == "price_asc":
        qs = qs.order_by("effective_price", "-created_at")
    elif sort == "price_desc":
        qs = qs.order_by(F("effective_price").desc(), "-created_at")
    elif sort == "featured":
        # hanya feature
        qs = qs.filter(is_featured=True).order_by("-created_at")
    else:
        qs = qs.order_by("-created_at")

    paginator = Paginator(qs, 6)  # 6 cards first
    page_obj = paginator.get_page(request.GET.get("page"))

    ctx = {
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "categories": Category.objects.filter(parent__isnull=True),
        "active_cat": cat,
        "sort": sort or "featured",
        # contoh info filter member
        "show_member_price": request.user.is_authenticated,
    }
    return render(request, "shop/list.html", ctx)


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category","brand"), slug=slug, status="active")
    reviews = product.reviews.select_related("user")[:10]
    form = ReviewForm()
    return render(request, "shop/detail.html", {
        "product": product, "reviews": reviews, "form": form,
        "show_member_price": request.user.is_authenticated,
    })

#def product_featured

#JSON endpoints



@login_required
@require_POST
def create_review(request, product_id):
    # hanya menerima POST
    product = get_object_or_404(Product, pk=product_id, status="active")

    form = ReviewForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    review = form.save(commit=False)
    review.product = product
    review.user = request.user
    review.save()

    # hitung ulang agregat rating
    agg = product.reviews.aggregate(avg=Avg("rating"), cnt=Count("id"))
    product.rating_avg = agg["avg"] or 0
    product.rating_count = agg["cnt"] or 0
    product.save(update_fields=["rating_avg", "rating_count"])

    return JsonResponse({
        "ok": True,
        "review": {
            "user": request.user.username,
            "rating": review.rating,
            "title": review.title,
            "content": review.content,
        },
        "rating_avg": product.rating_avg,
        "rating_count": product.rating_count,
    }, status=201)

@require_GET
def product_detail_json(request, slug):
    p = get_object_or_404(Product.objects.select_related("category","brand"),
                          slug=slug, status="active")
    return JsonResponse({
        "id": str(p.id),
        "name": p.name,
        "slug": p.slug,
        "description": p.description,
        "thumbnail": p.thumbnail,
        "category": p.category.name if p.category else None,
        "brand": p.brand.name if p.brand else None,
        "price": float(p.price),
        "sale_price": float(p.sale_price) if p.sale_price is not None else None,
        "final_price": float(p.final_price),
        "discount_percent": p.discount_percent,
        "in_stock": p.in_stock,
        "rating_avg": p.rating_avg,
        "rating_count": p.rating_count,
        "stock": p.stock,
        "status": p.status,
    }, status=200)

@require_GET
def reviews_json(request, product_id):
    p = get_object_or_404(Product, pk=product_id, status="active")
    page_obj = Paginator(p.reviews.select_related("user").order_by("-created_at"), 10)\
                  .get_page(request.GET.get("page"))
    items = [{
        "user": r.user.username,
        "rating": r.rating,
        "title": r.title,
        "content": r.content,
        "created_at": localtime(r.created_at).isoformat(),
    } for r in page_obj.object_list]
    return JsonResponse({"results": items, "has_next": page_obj.has_next()}, status=200)


@require_GET
def product_mini_json(request, pk):
    p = get_object_or_404(Product.objects.select_related("category","brand"), pk=pk, status="active")
    return JsonResponse({
        "id": str(p.id),
        "name": p.name,
        "price": float(p.final_price),
        "currency": p.currency,
        "in_stock": p.in_stock,
        "stock": p.stock,
        "thumbnail": p.thumbnail,
    }, status=200)



@login_required
@require_http_methods(["GET", "POST"])
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # izinkan owner ATAU user yang punya perm change_product
    if not (request.user == product.created_by or request.user.has_perm("shop.change_product")):
        raise PermissionDenied("You are not allowed to edit this product.")

  
    FormCls = ProductForm

    if request.method == "GET":
        form = FormCls(instance=product)
   
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string(
                "shop/_product_form.html",
                {"form": form, "mode": "edit", "product": product},
                request=request,
            )
            return JsonResponse({"html": html})
        # fallback full page
        return render(request, "shop/product_form.html", {"form": form, "mode": "edit", "product": product})

    #simpan changes
    form = FormCls(request.POST, instance=product)
    if not form.is_valid():
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string(
                "shop/_product_form.html",
                {"form": form, "mode": "edit", "product": product},
                request=request,
            )
            return JsonResponse({"ok": False, "html": html}, status=400)
        return render(request, "shop/product_form.html", {"form": form, "mode": "edit", "product": product})

    p = form.save()

    # jika ajax balas payload minimal untuk update kartu di grid
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "ok": True,
            "product": {
                "id": str(p.id),
                "slug": p.slug,
                "name": p.name,
                "thumbnail": p.thumbnail or "",
                "category": p.category.name if p.category_id else None,
                "price": float(p.price),
                "sale_price": float(p.sale_price) if p.sale_price is not None else None,
                "in_stock": p.in_stock,
                "owner": p.created_by.username if p.created_by_id else None,
            }
        })

    messages.success(request, "Product updated.")
    return redirect("shop:detail", slug=p.slug)


@require_http_methods(["GET", "POST"])
@login_required
def product_create(request):
   # get post via ajax, atau gak pakai ajax
    # form publik 
    from .forms import ProductForm
    class PublicProductForm(ProductForm):
        class Meta(ProductForm.Meta):
            fields = [
                "name","category","brand","description",
                "price","sale_price","currency","stock","thumbnail",
                "is_featured",  
            ]

    FormCls = PublicProductForm if not request.user.is_staff else ProductForm

    if request.method == "GET":
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            form = FormCls()
            html = render_to_string("shop/_product_form.html", {"form": form, "mode": "create"}, request=request)
            return JsonResponse({"html": html})
        return redirect("shop:list")

    # POST
    form = FormCls(request.POST)
    if not form.is_valid():
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string("shop/_product_form.html", {"form": form, "mode": "create"}, request=request)
            return JsonResponse({"ok": False, "html": html}, status=400)
        return render(request, "shop/product_form.html", {"form": form, "mode": "create"})

    p = form.save(commit=False)
    #paksa nilai aman untuk user biasa
    if not request.user.is_staff:
        p.is_featured = False
        if hasattr(p, "status"):
            p.status = "active"
    if hasattr(p, "created_by"):
        p.created_by = request.user
    p.save()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "ok": True,
            "product": {
                "id": str(p.id),
                "slug": p.slug,
                "name": p.name,
                "thumbnail": p.thumbnail,
                "category": p.category.name if p.category_id else None,
                "price": float(p.price),
                "sale_price": float(p.sale_price) if p.sale_price is not None else None,
                "in_stock": p.in_stock,
                "owner": p.created_by.username if p.created_by_id else None,
            }
        }, status=201)

    messages.success(request, "Product created")
    return redirect("shop:detail", slug=p.slug)


def products_json(request):
    qs   = Product.objects.filter(status="active").select_related("category","created_by")
    cat  = request.GET.get("category")
    q    = request.GET.get("q")
    sort = request.GET.get("sort")
    page = int(request.GET.get("page", 1))

    if cat: qs = qs.filter(category__slug=cat)
    if q:   qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

    qs = qs.annotate(effective_price=Coalesce("sale_price", "price", output_field=DecimalField()))
    if sort == "price_asc":
        qs = qs.order_by("effective_price", "-created_at")
    elif sort == "price_desc":
        qs = qs.order_by(F("effective_price").desc(), "-created_at")
    elif sort == "featured":
        qs = qs.filter(is_featured=True).order_by("-created_at")
    else:
        qs = qs.order_by("-created_at")

    paginator = Paginator(qs, 6)
    page_obj = paginator.get_page(page)

    items = []
    uid = request.user.id if request.user.is_authenticated else None
    for p in page_obj.object_list.select_related("category","created_by"):
        items.append({
            "id": str(p.id),
            "name": p.name,
            "slug": p.slug,
            "thumbnail": p.thumbnail,
            "category": p.category.name if p.category else None,
            "price": float(p.price),
            "sale_price": float(p.sale_price) if p.sale_price is not None else None,
            "discount_percent": p.discount_percent,
            "in_stock": p.in_stock,
            "rating_avg": p.rating_avg,
            "rating_count": p.rating_count,
            "owner": (p.created_by.username if p.created_by_id else None),
            "is_owner": (uid is not None and p.created_by_id == uid),
        })
    return JsonResponse({"results": items, "has_next": page_obj.has_next()}, status=200)


def _is_ajax(request):
   
    return request.headers.get("x-requested-with") == "XMLHttpRequest"

@login_required
@require_http_methods(["GET", "POST"])
def create_product(request):
  # ajax, get, post atau non ajax
    if request.method == "GET":
        form = ProductForm()
        if _is_ajax(request):
            html = render_to_string("shop/_product_form.html", {"form": form}, request=request)
            return JsonResponse({"html": html})
        #fallback full page 
        return render(request, "shop/create.html", {"form": form})

    # POST
    form = ProductForm(request.POST)
    if form.is_valid():
        product = form.save(commit=False)
        product.created_by = request.user
        product.status = "active"
        product.save()
      
        payload = {
            "id": str(product.id),
            "name": product.name,
            "slug": product.slug,
            "thumbnail": product.thumbnail or "",
            "category": product.category.name if product.category_id else None,
            "price": float(product.price),
            "sale_price": float(product.sale_price) if product.sale_price is not None else None,
            "in_stock": product.in_stock,
            "owner": request.user.username,
            "is_owner": True,  # newly created by current user
        }
        return JsonResponse({"ok": True, "product": payload}, status=201)

    #Invalid maka return the form fragment with errors
    html = render_to_string("shop/_product_form.html", {"form": form}, request=request)
    return JsonResponse({"ok": False, "html": html}, status=400)


@login_required
@require_POST
def product_delete(request, pk):
   
    product = get_object_or_404(Product, pk=pk)
    if not (request.user.is_staff or product.created_by_id == request.user.id):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    product.delete()
    return JsonResponse({"ok": True}, status=200)