from __future__ import annotations

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.urls import reverse

from portal_berita.models import Berita
from shop.models import Product

from .forms import SearchForm, SearchPreferenceForm
from .models import SearchPreference, SearchLog


def _get_available_preferences(user):
    """Return presets that the current user is allowed to access."""

    base_q = Q(
        is_public=True, role_visibility=SearchPreference.RoleVisibility.ALL
    )
    if user.is_authenticated:
        base_q |= Q(user=user)
        if user.is_staff:
            base_q |= Q(is_public=True, role_visibility=SearchPreference.RoleVisibility.STAFF)
    return (
        SearchPreference.objects.filter(base_q)
        .select_related(
            "user",
            "default_news_category",
            "default_product_category",
            "default_brand",
        )
        .distinct()
        .order_by("label")
    )


def search_page(request):
    """Render the main search dashboard."""

    search_form = SearchForm()
    preference_form = SearchPreferenceForm(user=request.user)
    preferences = _get_available_preferences(request.user)

    trending_news = (
        Berita.objects.filter(is_published=True).order_by("-views")[:4]
    )
    featured_products = (
        Product.objects.filter(status="active", is_featured=True)[:6]
    )

    context = {
        "search_form": search_form,
        "preference_form": preference_form,
        "preferences": preferences,
        "recent_searches": request.session.get("recent_searches", []),
        "trending_news": trending_news,
        "featured_products": featured_products,
    }
    return render(request, "fitur_pencarian/search_page.html", context)


def _apply_preference_to_data(cleaned_data, preference):
    """Fill missing filters with values from the selected preference."""

    if not preference:
        return cleaned_data

    if cleaned_data.get("search_in") in (None, ""):
        cleaned_data["search_in"] = preference.default_scope
    if not cleaned_data.get("news_category") and preference.default_news_category:
        cleaned_data["news_category"] = preference.default_news_category
    if not cleaned_data.get("product_category") and preference.default_product_category:
        cleaned_data["product_category"] = preference.default_product_category
    if not cleaned_data.get("brand") and preference.default_brand:
        cleaned_data["brand"] = preference.default_brand
    if not cleaned_data.get("min_price") and preference.min_price is not None:
        cleaned_data["min_price"] = preference.min_price
    if not cleaned_data.get("max_price") and preference.max_price is not None:
        cleaned_data["max_price"] = preference.max_price
    return cleaned_data


def _serialize_news_item(news, is_staff=False):
    try:
        url = news.get_absolute_url()
    except AttributeError:
        url = reverse("portal_berita:detail_news", args=[news.id])
    return {
        "id": str(news.id),
        "title": news.judul,
        "category": news.kategori.nama if news.kategori else "Umum",
        "thumbnail": news.thumbnail,
        "url": url,
        "views": news.views if is_staff else None,
        "published_at": timezone.localtime(news.tanggal_dibuat).strftime("%d %b %Y"),
    }


def _serialize_product_item(product, is_staff=False):
    try:
        url = product.get_absolute_url()
    except AttributeError:
        url = reverse("shop:detail", args=[product.slug])
    return {
        "id": str(product.id),
        "name": product.name,
        "thumbnail": product.thumbnail,
        "price": float(product.final_price),
        "currency": product.currency,
        "discount": product.discount_percent,
        "url": url,
        "stock": product.stock if is_staff else None,
    }


def _update_recent_searches(request, payload):
    recent_searches = request.session.get("recent_searches", [])
    recent_searches = [
        item
        for item in recent_searches
        if not (
            item.get("query") == payload["query"]
            and item.get("scope") == payload["scope"]
        )
    ]
    recent_searches.insert(0, payload)
    request.session["recent_searches"] = recent_searches[:6]
    request.session.modified = True


@require_GET
def ajax_search_results(request):
    form = SearchForm(request.GET)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    cleaned_data = form.cleaned_data
    preference = None
    preference_id = request.GET.get("preference")
    if preference_id:
        preference = get_object_or_404(SearchPreference, pk=preference_id)
        if preference.is_staff_only and not request.user.is_staff:
            return JsonResponse(
                {"errors": {"preference": "Preset hanya untuk staf."}}, status=403
            )
        if not preference.is_public and preference.user != request.user:
            return JsonResponse(
                {"errors": {"preference": "Anda tidak diperbolehkan menggunakan preset ini."}},
                status=403,
            )
        cleaned_data = _apply_preference_to_data(cleaned_data, preference)

    query = cleaned_data.get("query", "")
    search_scope = cleaned_data.get("search_in") or SearchPreference.SearchScope.ALL

    news_results = Berita.objects.filter(is_published=True)
    if query:
        news_results = news_results.filter(
            Q(judul__icontains=query)
            | Q(konten__icontains=query)
            | Q(kategori__nama__icontains=query)
        )
    if cleaned_data.get("news_category"):
        news_results = news_results.filter(kategori=cleaned_data["news_category"])

    product_results = Product.objects.filter(status="active")
    if query:
        product_results = product_results.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(brand__name__icontains=query)
        )
    if cleaned_data.get("product_category"):
        product_results = product_results.filter(
            category=cleaned_data["product_category"]
        )
    if cleaned_data.get("brand"):
        product_results = product_results.filter(brand=cleaned_data["brand"])
    if cleaned_data.get("min_price") is not None:
        min_price = cleaned_data["min_price"]
        product_results = product_results.filter(
            Q(sale_price__gte=min_price)
            | (Q(sale_price__isnull=True) & Q(price__gte=min_price))
        )
    if cleaned_data.get("max_price") is not None:
        max_price = cleaned_data["max_price"]
        product_results = product_results.filter(
            Q(sale_price__lte=max_price)
            | (Q(sale_price__isnull=True) & Q(price__lte=max_price))
        )
    if cleaned_data.get("only_discount"):
        product_results = product_results.filter(sale_price__isnull=False)

    if search_scope == SearchPreference.SearchScope.NEWS:
        product_results = Product.objects.none()
    elif search_scope == SearchPreference.SearchScope.PRODUCTS:
        news_results = Berita.objects.none()

    news_data = [
        _serialize_news_item(berita, request.user.is_staff)
        for berita in news_results.select_related("kategori")[:8]
    ]
    product_data = [
        _serialize_product_item(product, request.user.is_staff)
        for product in product_results.select_related("category", "brand")[:8]
    ]

    total_results = len(news_data) + len(product_data)

    if not request.session.session_key:
        request.session.create()

    payload = {
        "query": query,
        "scope": search_scope,
        "news_count": len(news_data),
        "product_count": len(product_data),
        "timestamp": timezone.localtime().isoformat(),
    }
    _update_recent_searches(request, payload)

    SearchLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key,
        keyword=query,
        scope=search_scope,
        preference=preference,
        result_count=total_results,
    )

    return JsonResponse(
        {
            "summary": {
                "query": query,
                "scope": search_scope,
                "news_count": len(news_data),
                "product_count": len(product_data),
            },
            "news": news_data,
            "products": product_data,
            "recent": request.session.get("recent_searches", []),
            "role": "staff" if request.user.is_staff else "user",
        }
    )


@login_required
@require_GET
def ajax_preference_form(request, id=None):
    # id bisa dari path param (kwargs) atau dari querystring (?id=...)
    preference_id = id or request.GET.get("id")
    preference = None
    if preference_id:
        preference = get_object_or_404(SearchPreference, pk=preference_id, user=request.user)
    form = SearchPreferenceForm(instance=preference, user=request.user)
    html = render_to_string(
        "fitur_pencarian/_preference_form.html",
        {"form": form, "preference": preference},
        request=request,
    )
    return JsonResponse({"form": html})

@login_required
@require_POST
def ajax_preference_submit(request, id=None):
    # id bisa dari path param (kwargs) atau dari POST body (id=...)
    preference_id = id or request.POST.get("id")
    instance = None
    if preference_id:
        instance = get_object_or_404(SearchPreference, pk=preference_id, user=request.user)

    form = SearchPreferenceForm(request.POST, instance=instance, user=request.user)

    # **PENTING**: set user SEBELUM validasi agar validate_unique(user, label) jalan
    form.instance.user = request.user

    if form.is_valid():
        preference = form.save(commit=False)
        preference.user = request.user  # redundant tapi aman

        # jaga privasi dia sendiri (logika ini sebenarnya tidak perlu karena user sama)
        if not preference.is_public and preference.user != request.user:
            preference.is_public = False

        try:
            preference.save()
        except IntegrityError:
            # contoh: label sudah dipakai user yang sama → kembalikan error form (400)
            form.add_error("label", "Label sudah digunakan untuk preset lain di akun Anda.")
            html = render_to_string(
                "fitur_pencarian/_preference_form.html",
                {"form": form, "preference": instance},
                request=request,
            )
            return JsonResponse({"form": html, "errors": form.errors}, status=400)

        form.save_m2m()

        html = render_to_string(
            "fitur_pencarian/_preference_card.html",
            {"preference": preference, "request": request},
        )
        return JsonResponse(
            {
                "message": "Preset pencarian berhasil disimpan.",
                "preference": {
                    "id": str(preference.id),
                    "label": preference.label,
                    "scope": preference.default_scope,
                    "role_visibility": preference.role_visibility,
                },
                "card": html,
            }
        )

    html = render_to_string(
        "fitur_pencarian/_preference_form.html",
        {"form": form, "preference": instance},
        request=request,
    )
    return JsonResponse({"form": html, "errors": form.errors}, status=400)

@login_required
@require_POST
def ajax_preference_delete(request):
    preference_id = request.POST.get("id")
    if not preference_id:
        return JsonResponse({"error": "Preset tidak ditemukan."}, status=400)

    preference = get_object_or_404(
        SearchPreference, pk=preference_id, user=request.user
    )
    preference.delete()
    return JsonResponse({"message": "Preset pencarian berhasil dihapus."})

@require_GET
def ajax_recent_searches(request):
    return JsonResponse({"recent": request.session.get("recent_searches", [])})


@login_required
@user_passes_test(lambda user: user.is_staff)
@require_GET
def ajax_search_analytics(request):
    top_queries = list(
        SearchLog.objects.values("keyword")
        .annotate(total=Count("id"))
        .order_by("-total")[:8]
    )
    scope_breakdown = list(
        SearchLog.objects.values("scope").annotate(total=Count("id")).order_by("-total")
    )
    return JsonResponse(
        {
            "top_queries": top_queries,
            "scope_breakdown": scope_breakdown,
        }
    )