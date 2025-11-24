from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.core import serializers
import json
from datetime import datetime
from django.utils.timesince import timesince

from portal_berita.forms import BeritaForm, KategoriBeritaForm, CommentForm, CustomAuthenticationForm, CustomUserCreationForm
from portal_berita.models import Berita, KategoriBerita, Comment
from scoreboard.models import Scoreboard
from shop.models import Product

def is_admin(user):
    return user.is_staff


def main_view(request):
    context = {
        'Welcome': 'Welcome to Sport Watch!',
        'Who': 'Presented By Kelompok C 13',
    }
    return render(request, "portal_berita/main.html", context)

def detail_news(request, id):
    news = get_object_or_404(Berita, id=id)
    news.increment_views()

    comments = Comment.objects.filter(berita=news, parent=None).order_by('-created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.berita = news
            new_comment.user = request.user
            
            parent_id = request.POST.get('parent_id')
            if parent_id:
                new_comment.parent = Comment.objects.get(id=parent_id)
            
            new_comment.save()
            return redirect('portal_berita:detail_news', id=id)
    else:
        comment_form = CommentForm()

    context = {
        'news': news,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'portal_berita/detail_news.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('portal_berita:login')
        else:
            messages.error(request, 'Error creating account. Please check your input.')
    else:
        form = CustomUserCreationForm()
    return render(request, "portal_berita/register.html", {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome, {username}!')
                return redirect('portal_berita:main')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, "portal_berita/login.html", {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('portal_berita:login')

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def list_news(request):
    all_news = Berita.objects.filter(is_published=True).order_by('-tanggal_dibuat')
    featured_news = None
    other_news_list = []

    if all_news.exists():
        featured_news = all_news.first()
        other_news_list = all_news[1:]

    # Paginate other_news_list
    paginator = Paginator(other_news_list, 6)  # Show 6 news items per page
    page = request.GET.get('page', 1)
    try:
        other_news = paginator.page(page)
    except PageNotAnInteger:
        other_news = paginator.page(1)
    except EmptyPage:
        other_news = paginator.page(paginator.num_pages)

    most_popular_news = Berita.objects.filter(is_published=True).order_by('-views')[:5]
    live_scores = Scoreboard.objects.filter(status__in=['live', 'recent']).order_by('-tanggal')[:3]
    featured_products = Product.objects.filter(is_featured=True, status='active')[:3]

    context = {
        'featured_news': featured_news,
        'other_news': other_news,
        'most_popular_news': most_popular_news,
        'live_scores': live_scores,
        'featured_products': featured_products,
        'has_next_page': other_news.has_next(),
        'next_page_number': other_news.next_page_number() if other_news.has_next() else None,
    }
    return render(request, 'portal_berita/list_news.html', context)

def load_more_news(request):
    offset = int(request.GET.get('offset', 0))
    limit = 6  # Number of news items to load per request

    all_news = Berita.objects.filter(is_published=True).order_by('-tanggal_dibuat')
    # Exclude the featured news if it exists
    if all_news.exists():
        all_news = all_news[1:] # Skip the first one (featured)

    news_to_load = all_news[offset:offset + limit]
    
    data = []
    for news_item in news_to_load:
        data.append({
            'id': news_item.id,
            'thumbnail': news_item.thumbnail if news_item.thumbnail else '/static/images/default_news_thumbnail.jpg',
            'kategori_nama': news_item.kategori.nama if news_item.kategori else 'Default',
            'kategori_class': news_item.kategori.get_category_class() if news_item.kategori else 'default',
            'judul': news_item.judul,
            'konten_truncated': news_item.konten[:100] + '...' if len(news_item.konten) > 100 else news_item.konten,
            'tanggal_dibuat_timesince': timesince(news_item.tanggal_dibuat),
            'comment_count': news_item.comment_count,
            'detail_url': reverse('portal_berita:detail_news', args=[news_item.id]),
        })
    
    has_more = (offset + limit) < len(all_news)

    return JsonResponse({'news': data, 'has_more': has_more})

@csrf_exempt
@user_passes_test(is_admin)
@login_required
def create_news(request):
    if request.method == 'POST':
        form = BeritaForm(request.POST)
        if form.is_valid():
            berita = form.save(commit=False)
            berita.penulis = request.user
            berita.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'News created successfully.'})
            return HttpResponseRedirect(reverse('portal_berita:detail_news', args=[berita.id]))
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors})
            context = {'form': form}
            return render(request, 'portal_berita/form_berita.html', context)
    else:
        form = BeritaForm()
        context = {'form': form}
        return render(request, 'portal_berita/form_berita.html', context)

@csrf_exempt
@user_passes_test(is_admin)
@login_required
def edit_news(request, id):
    berita = get_object_or_404(Berita, id=id)

    if request.method == 'POST':
        form = BeritaForm(request.POST, instance=berita)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'News updated successfully.'})
            return HttpResponseRedirect(reverse('portal_berita:detail_news', args=[berita.id]))
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors})
            context = {'form': form}
            return render(request, 'portal_berita/form_berita.html', context)
    else:
        form = BeritaForm(instance=berita)
        context = {'form': form}
        return render(request, 'portal_berita/form_berita.html', context)

@csrf_exempt
@require_POST
@user_passes_test(is_admin)
@login_required
def delete_news(request, id):
    berita = get_object_or_404(Berita, id=id)
    
    berita.delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'News deleted successfully.'})
    
    return HttpResponseRedirect(reverse('portal_berita:list_news'))


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
    if request.method == 'POST':
        form = KategoriBeritaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('portal_berita:news_management')
        else:
            messages.error(request, 'Error adding category. Please check your input.')
    else:
        form = KategoriBeritaForm()
    return render(request, 'portal_berita/add_category.html', {'form': form})

@user_passes_test(is_admin)
@login_required
def news_management(request):
    news_list = Berita.objects.all()
    context = {'news_list': news_list}
    return render(request, 'portal_berita/news_management.html', context)
