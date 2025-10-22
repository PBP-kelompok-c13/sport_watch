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

from portal_berita.forms import BeritaForm, KategoriBeritaForm, CommentForm
from portal_berita.models import Berita, KategoriBerita, Comment

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

    comments = news.comments.filter(parent__isnull=True)
    comment_form = CommentForm()

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

    context = {
        'news': news,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'portal_berita/detail_news.html', context)

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


@csrf_exempt
@require_POST
def berita_json_view(request):
    all_berita = Berita.objects.all()
    data = serializers.serialize('json', all_berita)
    return JsonResponse(data, safe=False)

@user_passes_test(is_admin)
@login_required
def add_category(request):
    if request.method == 'POST':
        form = KategoriBeritaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('portal_berita:create_news')
    else:
        form = KategoriBeritaForm()
    return render(request, 'portal_berita/add_category.html', {'form': form})

@user_passes_test(is_admin)
@login_required
def news_management(request):
    news_list = Berita.objects.all()
    context = {'news_list': news_list}
    return render(request, 'portal_berita/news_management.html', context)
