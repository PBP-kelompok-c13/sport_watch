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

from portal_berita.forms import BeritaForm
from portal_berita.models import Berita, KategoriBerita

def is_admin(user):
    return user.is_staff

@login_required
def main_view(request):
    context = {
        'Welcome': 'Welcome to Sport Watch!',
        'Who': 'Presented By Kelompok C 13',
    }
    return render(request, "portal_berita/main.html", context)

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('portal_berita:login')
        else:
            messages.error(request, 'Error creating account. Please check your input.')
    else:
        form = UserCreationForm()
    return render(request, "portal_berita/register.html", {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
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
        form = AuthenticationForm()
    return render(request, "portal_berita/login.html", {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('portal_berita:login')

def list_news(request):
    news_list = Berita.objects.filter(is_published=True)
    context = {'news_list': news_list}
    return render(request, 'portal_berita/list_news.html', context)

def detail_news(request, id):
    news = get_object_or_404(Berita, id=id)
    news.increment_views()
    context = {'news': news}
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
