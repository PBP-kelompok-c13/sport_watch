from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Scoreboard
from .forms import ScoreBoardForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def index(request):
    # ambil langsung berdasarkan status
    live = Scoreboard.objects.filter(status='live').order_by('-tanggal')
    finished = Scoreboard.objects.filter(status='recent').order_by('-tanggal')
    upcoming = Scoreboard.objects.filter(status='upcoming').order_by('-tanggal')

    context = {
        'judul': 'Scoreboard',
        'live': live,
        'finished': finished,
        'upcoming': upcoming,
    }
    return render(request, 'scoreboard/index.html', context)

@user_passes_test(is_admin, login_url='/accounts/login/')
def scoreboard_management(request):
    scores = Scoreboard.objects.all().order_by('-tanggal')
    return render(request, 'scoreboard/scoreboard_management.html', {'scores': scores})

@user_passes_test(is_admin, login_url='/accounts/login/')
def create_score(request):
    form = ScoreBoardForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('scoreboard:scoreboard_management')
    return render(request, 'scoreboard/score_form.html', {'form': form, 'title': 'Add New Score'})

@user_passes_test(is_admin, login_url='/accounts/login/')
def edit_score(request, pk):
    item = get_object_or_404(Scoreboard, pk=pk)
    form = ScoreBoardForm(request.POST or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('scoreboard:scoreboard_management')
    return render(request, 'scoreboard/score_form.html', {'form': form, 'title': 'Edit Score'})

@user_passes_test(is_admin, login_url='/accounts/login/')
def delete_score(request, pk):
    item = get_object_or_404(Scoreboard, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('scoreboard:scoreboard_management')
    return render(request, 'scoreboard/confirm_delete.html', {'score': item})

def filter_scores(request):
    status = request.GET.get('status')  
    sport = request.GET.get('sport')
    
    if status == 'finished':
        status_filter = 'recent'
    else:
        status_filter = status

    data = Scoreboard.objects.all().order_by('-tanggal')

    if status_filter in {'live', 'recent', 'upcoming'}:
        data = data.filter(status=status_filter)

    if sport:
        data = data.filter(sport__iexact=sport)

    results = []
    for s in data:
        status_for_frontend = 'finished' if s.status == 'recent' else s.status

        results.append({
            'id': s.id,
            'tim1': s.tim1,
            'tim2': s.tim2,
            'skor_tim1': s.skor_tim1,
            'skor_tim2': s.skor_tim2,
            'tanggal': s.tanggal.isoformat(),
            'sport': s.sport,                
            'sport_display': s.get_sport_display(),
            'status': status_for_frontend,   
            'logo_tim1': s.logo_tim1,
            'logo_tim2': s.logo_tim2,
        })

    return JsonResponse({'scores': results})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_score_flutter(request):
    if not request.user.is_staff:
         return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    data = request.data

    tim1 = strip_tags(data.get('tim1', ''))
    tim2 = strip_tags(data.get('tim2', ''))
    skor_tim1 = data.get('skor_tim1')
    skor_tim2 = data.get('skor_tim2')
    sport = data.get('sport', 'NBA')
    status = data.get('status', 'upcoming')
    logo_tim1 = data.get('logo_tim1', '')
    logo_tim2 = data.get('logo_tim2', '')
    
    if not tim1 or not tim2:
         return JsonResponse({'status': 'error', 'message': 'Team names are required'}, status=400)

    score = Scoreboard.objects.create(
        tim1=tim1,
        tim2=tim2,
        skor_tim1=int(skor_tim1) if skor_tim1 is not None else 0,
        skor_tim2=int(skor_tim2) if skor_tim2 is not None else 0,
        sport=sport,
        status=status,
        logo_tim1=logo_tim1,
        logo_tim2=logo_tim2,
        tanggal=timezone.now()
    )

    return JsonResponse({'status': 'success', 'id': score.id}, status=201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_score_flutter(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
    score = get_object_or_404(Scoreboard, pk=pk)
    
    data = request.data

    score.tim1 = strip_tags(data.get('tim1', score.tim1))
    score.tim2 = strip_tags(data.get('tim2', score.tim2))
    score.skor_tim1 = int(data.get('skor_tim1', score.skor_tim1))
    score.skor_tim2 = int(data.get('skor_tim2', score.skor_tim2))
    score.sport = data.get('sport', score.sport)
    score.status = data.get('status', score.status)
    score.logo_tim1 = data.get('logo_tim1', score.logo_tim1)
    score.logo_tim2 = data.get('logo_tim2', score.logo_tim2)
    
    score.save()
    
    return JsonResponse({'status': 'success', 'id': score.id})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_score_flutter(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
    score = get_object_or_404(Scoreboard, pk=pk)
    score.delete()
    
    return JsonResponse({'status': 'success', 'id': pk})
