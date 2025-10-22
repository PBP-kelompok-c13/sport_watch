from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from .models import scoreboard  
from .forms import ScoreBoardForm
from django.http import JsonResponse

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def index(request):
    today = timezone.localdate()

    live = scoreboard.objects.filter(tanggal=today).order_by('-tanggal')
    finished = scoreboard.objects.filter(tanggal__lt=today).order_by('-tanggal')
    upcoming = scoreboard.objects.filter(tanggal__gt=today).order_by('-tanggal')

    context = {
        'judul': 'Scoreboard',
        'live': live,
        'finished': finished,
        'upcoming': upcoming,
    }
    return render(request, 'scoreboard/index.html', context)


@user_passes_test(is_admin)
def scoreboard_management(request):
    scores = scoreboard.objects.all().order_by('-tanggal')
    return render(request, 'scoreboard/scoreboard_management.html', {'scores': scores})


@user_passes_test(is_admin)
def create_score(request):
    form = ScoreBoardForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('scoreboard:scoreboard_management')
    return render(request, 'scoreboard/score_form.html', {'form': form, 'title': 'Add New Score'})


@user_passes_test(is_admin)
def edit_score(request, pk):
    item = get_object_or_404(scoreboard, pk=pk)
    form = ScoreBoardForm(request.POST or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('scoreboard:scoreboard_management')
    return render(request, 'scoreboard/score_form.html', {'form': form, 'title': 'Edit Score'})


@user_passes_test(is_admin)
def delete_score(request, pk):
    item = get_object_or_404(scoreboard, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('scoreboard:scoreboard_management')
    return render(request, 'scoreboard/confirm_delete.html', {'score': item})

def filter_scores(request):
    status = request.GET.get('status')
    today = timezone.localdate()
    
    if status ==  "live":
        data = scoreboard.objects.filter(tanggal=today)
    elif status == "finished":
        data = scoreboard.objects.filter(tanggal__lt=today)
    elif status == "upcoming":
        data = scoreboard,objects.filter(tanggal__gt=today)
    else:
        data = scoreboard.objects.all()
        
    results = [
        {
            'tim1': s.tim1,
            'tim2': s.tim2,
            'skor_tim1': s.skor_tim1,
            'skor_tim2': s.skor_tim2,
            'tanggal': s.tanggal.strftime('%Y-%m-%d'),
        }
        for s in data
     ]
    return jsonResponse({'scores': results})
