import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.timesince import timesince
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from scoreboard.models import Scoreboard
from shop.models import Product

from portal_berita.forms import (
    BeritaForm,
    CommentForm,
    CustomAuthenticationForm,
    CustomUserCreationForm,
    KategoriBeritaForm,
)
from portal_berita.models import (
    REACTION_CHOICES,
    Berita,
    Comment,
    KategoriBerita,
    NewsReaction,
)


def is_admin(user):
    return user.is_staff


def main_view(request):
    context = {
        "Welcome": "Welcome to Sport Watch!",
        "Who": "Presented By Kelompok C 13",
    }
    return render(request, "portal_berita/main.html", context)


from django.views.decorators.cache import never_cache


@never_cache
def detail_news(request, id):
    news = get_object_or_404(Berita, id=id)
    news.increment_views()

    comments = Comment.objects.filter(berita=news, parent=None).order_by("-created_at")

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.berita = news
            new_comment.user = request.user

            parent_id = request.POST.get("parent_id")
            if parent_id:
                new_comment.parent = Comment.objects.get(id=parent_id)

            new_comment.save()
            return redirect("portal_berita:detail_news", id=id)
    else:
        comment_form = CommentForm()

    user_reaction = news.get_user_reaction(request.user)

    context = {
        "news": news,
        "comments": comments,
        "comment_form": comment_form,
        "reaction_summary": news.reaction_summary,
        "user_reaction": user_reaction,
        "user_reactions_json": json.dumps(
            {str(news.id): user_reaction} if user_reaction else {}
        ),
        "reaction_login_url": reverse("portal_berita:login"),
    }
    return render(request, "portal_berita/detail_news.html", context)


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("portal_berita:login")
        else:
            messages.error(request, "Error creating account. Please check your input.")
    else:
        form = CustomUserCreationForm()
    return render(request, "portal_berita/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {username}!")
                return redirect("portal_berita:list_news")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, "portal_berita/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("portal_berita:login")


from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def list_news(request):
    news_queryset = (
        Berita.objects.filter(is_published=True)
        .select_related("kategori", "penulis")
        .prefetch_related("reactions")
        .order_by("-tanggal_dibuat")
    )
    all_news = list(news_queryset)
    featured_news = all_news[0] if all_news else None
    other_news_list = all_news[1:] if len(all_news) > 1 else []

    # Paginate other_news_list
    paginator = Paginator(other_news_list, 6)  # Show 6 news items per page
    page = request.GET.get("page", 1)
    try:
        other_news = paginator.page(page)
    except PageNotAnInteger:
        other_news = paginator.page(1)
    except EmptyPage:
        other_news = paginator.page(paginator.num_pages)

    most_popular_news = Berita.objects.filter(is_published=True).order_by("-views")[:5]
    try:
        live_scores = Scoreboard.objects.filter(status__in=["live", "recent"]).order_by(
            "-tanggal"
        )[:3]
    except Exception:
        live_scores = []

    try:
        featured_products = Product.objects.filter(is_featured=True, status="active")[
            :3
        ]
    except Exception:
        featured_products = []

    news_ids = [news.id for news in all_news]
    user_reactions = {}
    if request.user.is_authenticated and news_ids:
        user_reactions = {
            str(reaction.berita_id): reaction.reaction_type
            for reaction in NewsReaction.objects.filter(
                user=request.user,
                berita_id__in=news_ids,
            )
        }

    context = {
        "featured_news": featured_news,
        "other_news": other_news,
        "most_popular_news": most_popular_news,
        "live_scores": live_scores,
        "featured_products": featured_products,
        "has_next_page": other_news.has_next(),
        "next_page_number": other_news.next_page_number()
        if other_news.has_next()
        else None,
        "user_reactions_json": json.dumps(user_reactions),
        "reaction_login_url": reverse("portal_berita:login"),
    }
    return render(request, "portal_berita/list_news.html", context)


def load_more_news(request):
    offset = int(request.GET.get("offset", 0))
    limit = 6  # Number of news items to load per request

    all_news = (
        Berita.objects.filter(is_published=True)
        .prefetch_related("reactions")
        .order_by("-tanggal_dibuat")
    )
    # Exclude the featured news if it exists
    if all_news.exists():
        all_news = all_news[1:]  # Skip the first one (featured)

    news_to_load = list(all_news[offset : offset + limit])

    user_reaction_map = {}
    if request.user.is_authenticated and news_to_load:
        ids = [news.id for news in news_to_load]
        user_reaction_map = {
            str(reaction.berita_id): reaction.reaction_type
            for reaction in NewsReaction.objects.filter(
                user=request.user,
                berita_id__in=ids,
            )
        }

    data = []
    for news_item in news_to_load:
        data.append(
            {
                "id": news_item.id,
                "thumbnail": news_item.thumbnail
                if news_item.thumbnail
                else "/static/images/default_news_thumbnail.jpg",
                "kategori_nama": news_item.kategori.nama
                if news_item.kategori
                else "Default",
                "kategori_class": news_item.kategori.get_category_class()
                if news_item.kategori
                else "default",
                "judul": news_item.judul,
                "konten_truncated": news_item.konten[:100] + "..."
                if len(news_item.konten) > 100
                else news_item.konten,
                "tanggal_dibuat_timesince": timesince(news_item.tanggal_dibuat),
                "comment_count": news_item.comment_count,
                "detail_url": reverse("portal_berita:detail_news", args=[news_item.id]),
                "reactions": news_item.reaction_summary,
                "user_reaction": user_reaction_map.get(str(news_item.id)),
                "reaction_post_url": reverse(
                    "portal_berita:react_to_news", args=[news_item.id]
                ),
            }
        )

    has_more = (offset + limit) < len(all_news)

    return JsonResponse({"news": data, "has_more": has_more})


@csrf_exempt
@require_POST
def react_to_news(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)

    valid_reactions = {key for key, _ in REACTION_CHOICES}
    reaction_type = None
    if request.body:
        try:
            payload = json.loads(request.body)
            if isinstance(payload, dict):
                reaction_type = payload.get("reaction")
        except json.JSONDecodeError:
            reaction_type = None
    if not reaction_type:
        reaction_type = request.POST.get("reaction")

    if reaction_type not in valid_reactions:
        return JsonResponse({"error": "Invalid reaction choice."}, status=400)

    berita = get_object_or_404(Berita, id=id)

    reaction, created = NewsReaction.objects.get_or_create(
        berita=berita,
        user=request.user,
        defaults={"reaction_type": reaction_type},
    )

    if not created:
        if reaction.reaction_type == reaction_type:
            reaction.delete()
            user_reaction = None
            state = "removed"
        else:
            reaction.reaction_type = reaction_type
            reaction.save(update_fields=["reaction_type"])
            user_reaction = reaction_type
            state = "updated"
    else:
        user_reaction = reaction_type
        state = "created"

    return JsonResponse(
        {
            "status": "ok",
            "state": state,
            "news_id": str(berita.id),
            "user_reaction": user_reaction,
            "reactions": berita.reaction_summary,
        }
    )


@require_GET
def news_list_json(request):
    per_page = max(1, min(int(request.GET.get("per_page", 6)), 30))
    page_number = request.GET.get("page", 1)
    news_queryset = (
        Berita.objects.filter(is_published=True)
        .order_by("-tanggal_dibuat")
        .prefetch_related("reactions")
    )
    paginator = Paginator(news_queryset, per_page)
    page_obj = paginator.get_page(page_number)

    user_reaction_map = {}
    if request.user.is_authenticated and page_obj.object_list:
        news_ids = [news.id for news in page_obj.object_list]
        user_reaction_map = {
            str(reaction.berita_id): reaction.reaction_type
            for reaction in NewsReaction.objects.filter(
                user=request.user,
                berita_id__in=news_ids,
            )
        }

    items = []
    for news_item in page_obj.object_list:
        items.append(
            {
                "id": str(news_item.id),
                "judul": news_item.judul,
                "konten": news_item.konten,
                "kategori": news_item.kategori.nama
                if news_item.kategori
                else "General",
                "thumbnail": news_item.thumbnail or "",
                "views": news_item.views,
                "penulis": news_item.penulis.username if news_item.penulis else None,
                "sumber": news_item.sumber,
                "is_published": news_item.is_published,
                "tanggal_dibuat": news_item.tanggal_dibuat.isoformat(),
                "tanggal_diperbarui": news_item.tanggal_diperbarui.isoformat(),
                "reaction_summary": news_item.reaction_summary,
                "user_reaction": user_reaction_map.get(str(news_item.id)),
                "detail_url": request.build_absolute_uri(
                    reverse("portal_berita:detail_news", args=[news_item.id])
                ),
            }
        )

    return JsonResponse(
        {
            "results": items,
            "has_next": page_obj.has_next(),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
            "total_pages": paginator.num_pages,
            "total_count": paginator.count,
            "page": page_obj.number,
            "per_page": per_page,
        }
    )


@csrf_exempt
@user_passes_test(is_admin)
@login_required
def create_news(request):
    if request.method == "POST":
        form = BeritaForm(request.POST)
        if form.is_valid():
            berita = form.save(commit=False)
            berita.penulis = request.user
            berita.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {"status": "success", "message": "News created successfully."}
                )
            return HttpResponseRedirect(
                reverse("portal_berita:detail_news", args=[berita.id])
            )
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "errors": form.errors})
            context = {"form": form}
            return render(request, "portal_berita/form_berita.html", context)
    else:
        form = BeritaForm()
        context = {"form": form}
        return render(request, "portal_berita/form_berita.html", context)


@csrf_exempt
@user_passes_test(is_admin)
@login_required
def edit_news(request, id):
    berita = get_object_or_404(Berita, id=id)

    if request.method == "POST":
        form = BeritaForm(request.POST, instance=berita)
        if form.is_valid():
            form.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {"status": "success", "message": "News updated successfully."}
                )
            return HttpResponseRedirect(
                reverse("portal_berita:detail_news", args=[berita.id])
            )
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "errors": form.errors})
            context = {"form": form}
            return render(request, "portal_berita/form_berita.html", context)
    else:
        form = BeritaForm(instance=berita)
        context = {"form": form}
        return render(request, "portal_berita/form_berita.html", context)


@csrf_exempt
@require_POST
@user_passes_test(is_admin)
@login_required
def delete_news(request, id):
    berita = get_object_or_404(Berita, id=id)

    berita.delete()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {"status": "success", "message": "News deleted successfully."}
        )

    return HttpResponseRedirect(reverse("portal_berita:list_news"))


def berita_json_view(request, id):
    berita = get_object_or_404(Berita, id=id)
    data = {
        "id": berita.id,
        "judul": berita.judul,
        "konten": berita.konten,
        "kategori": berita.kategori.nama if berita.kategori else None,
        "thumbnail": berita.thumbnail,
        "views": berita.views,
        "penulis": berita.penulis.username if berita.penulis else None,
        "sumber": berita.sumber,
        "is_published": berita.is_published,
        "tanggal_dibuat": berita.tanggal_dibuat,
        "tanggal_diperbarui": berita.tanggal_diperbarui,
    }
    return JsonResponse(data)


@user_passes_test(is_admin)
@login_required
def add_category(request):
    if request.method == "POST":
        form = KategoriBeritaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect("portal_berita:news_management")
        else:
            messages.error(request, "Error adding category. Please check your input.")
    else:
        form = KategoriBeritaForm()
    return render(request, "portal_berita/add_category.html", {"form": form})


@user_passes_test(is_admin)
@login_required
def news_management(request):
    news_list = Berita.objects.all()
    context = {"news_list": news_list}
    return render(request, "portal_berita/news_management.html", context)


@csrf_exempt
@login_required
@require_POST
def create_news_flutter(request):
    if not request.user.is_staff:
        return JsonResponse(
            {"status": "error", "message": "Permission denied"}, status=403
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    judul = strip_tags(data.get("judul", ""))
    konten = strip_tags(data.get("konten", ""))
    thumbnail = data.get("thumbnail", "")
    sumber = strip_tags(data.get("sumber", ""))
    is_published = data.get("is_published", False)
    kategori_name = data.get("kategori", None)

    if not judul or not konten:
        return JsonResponse(
            {"status": "error", "message": "Title and Content are required"}, status=400
        )

    kategori = None
    if kategori_name:
        kategori, _ = KategoriBerita.objects.get_or_create(nama=kategori_name)

    berita = Berita.objects.create(
        judul=judul,
        konten=konten,
        thumbnail=thumbnail,
        sumber=sumber,
        is_published=is_published,
        kategori=kategori,
        penulis=request.user,
    )

    return JsonResponse({"status": "success", "id": str(berita.id)}, status=201)


@csrf_exempt
@login_required
@require_POST
def edit_news_flutter(request, id):
    if not request.user.is_staff:
        return JsonResponse(
            {"status": "error", "message": "Permission denied"}, status=403
        )

    berita = get_object_or_404(Berita, id=id)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    berita.judul = strip_tags(data.get("judul", berita.judul))
    berita.konten = strip_tags(data.get("konten", berita.konten))
    berita.thumbnail = data.get("thumbnail", berita.thumbnail)
    berita.sumber = strip_tags(data.get("sumber", berita.sumber))
    berita.is_published = data.get("is_published", berita.is_published)

    kategori_name = data.get("kategori", None)
    if kategori_name:
        kategori, _ = KategoriBerita.objects.get_or_create(nama=kategori_name)
        berita.kategori = kategori

    berita.save()

    return JsonResponse({"status": "success", "id": str(berita.id)})


@csrf_exempt
@login_required
@require_POST
def delete_news_flutter(request, id):
    if not request.user.is_staff:
        return JsonResponse(
            {"status": "error", "message": "Permission denied"}, status=403
        )

    berita = get_object_or_404(Berita, id=id)
    berita.delete()

    return JsonResponse({"status": "success", "id": str(id)})


@require_GET
def news_comments_json(request, id):
    news = get_object_or_404(Berita, id=id)
    comments = Comment.objects.filter(berita=news, parent=None).order_by("-created_at")

    comments_data = []
    for comment in comments:
        comments_data.append(
            {
                "id": comment.id,
                "user": comment.user.username,
                "content": comment.content,
                "created_at": timesince(comment.created_at),
            }
        )

    return JsonResponse({"comments": comments_data})


@csrf_exempt
@login_required
@require_POST
def create_comment_flutter(request, id):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    content = strip_tags(data.get("content", ""))
    if not content:
        return JsonResponse(
            {"status": "error", "message": "Content is required"}, status=400
        )

    news = get_object_or_404(Berita, id=id)

    comment = Comment.objects.create(berita=news, user=request.user, content=content)

    return JsonResponse(
        {
            "status": "success",
            "comment": {
                "id": comment.id,
                "user": comment.user.username,
                "content": comment.content,
                "created_at": timesince(comment.created_at),
            },
        },
        status=201,
    )
