from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, F
from .models import Product, Category, Review
from .forms import ReviewForm

def product_list(request):
    # filter dasar
    qs = Product.objects.filter(status="active").select_related("category","brand")
    cat = request.GET.get("category")
    sort = request.GET.get("sort")  # sorting atau featured
    q   = request.GET.get("q")      #MODULE SEARCH REFERENSI SINI

    if cat: qs = qs.filter(category__slug=cat)
    if q:   qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

    if sort == "price_asc":   qs = qs.order_by("sale_price","price")
    elif sort == "price_desc":qs = qs.order_by(F("sale_price").desc(nulls_last=True), F("price").desc())
    elif sort == "featured":  qs = qs.order_by("-is_featured","-created_at")

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


#JSON endpoints
def products_json(request):
    qs = Product.objects.filter(status="active")
    cat = request.GET.get("category")
    q   = request.GET.get("q")
    page = int(request.GET.get("page", 1))
    if cat: qs = qs.filter(category__slug=cat)
    if q:   qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

    paginator = Paginator(qs.order_by("-created_at"), 6)
    page_obj = paginator.get_page(page)

    items = []
    for p in page_obj.object_list:
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
        })
    return JsonResponse({"results": items, "has_next": page_obj.has_next()}, status=200)


@login_required
def create_review(request, product_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    product = get_object_or_404(Product, pk=product_id, status="active")
    form = ReviewForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    review = form.save(commit=False)
    review.product = product
    review.user = request.user
    review.save()

    #RATING
    agg = product.reviews.aggregate(avg=models.Avg("rating"), cnt=models.Count("id"))
    product.rating_avg = agg["avg"] or 0
    product.rating_count = agg["cnt"] or 0
    product.save(update_fields=["rating_avg","rating_count"])

    return JsonResponse({
        "ok": True,
        "review": {
            "user": request.user.username,
            "rating": review.rating,
            "title": review.title,
            "content": review.content,
        }
    }, status=201)
