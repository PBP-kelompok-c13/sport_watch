from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from .models import Scoreboard
from .forms import ScoreBoardForm
from django.http import JsonResponse

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
        status = 'recent'

    data = Scoreboard.objects.all()

    if status in {'live', 'recent', 'upcoming'}:
        data = data.filter(status=status)

    if sport:
        data = data.filter(sport__iexact=sport)

    results = [
        {
            'tim1': s.tim1,
            'tim2': s.tim2,
            'skor_tim1': s.skor_tim1,
            'skor_tim2': s.skor_tim2,
            'tanggal': s.tanggal.strftime('%Y-%m-%d %H:%M') if hasattr(s.tanggal, 'strftime') else str(s.tanggal),
            'sport': s.sport,
            'status': s.status,
            'sport_display': s.get_sport_display(), 
            'logo_tim1': getattr(s, 'logo_tim1', None),
            'logo_tim2': getattr(s, 'logo_tim2', None),
        }
        for s in data
    ]
    return JsonResponse({'scores': results})
