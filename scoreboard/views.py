from django.shortcuts import render, redirect
from .models import scoreboard
from .forms import ScoreBoardForm
from datetime import date

def index(request):
    scores = scoreboard.objects.all().order_by('-tanggal')
    form = ScoreBoardForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('scoreboard:index')

    today = date.today()
    live = scoreboard.objects.filter(tanggal=today)
    finished = scoreboard.objects.filter(tanggal__lt=today)
    upcoming = scoreboard.objects.filter(tanggal__gt=today)

    context = {
        'judul': 'Scoreboard',
        'form': form,
        'live': live,
        'finished': finished,
        'upcoming': upcoming,
    }
    return render(request, 'scoreboard/index.html', context)
