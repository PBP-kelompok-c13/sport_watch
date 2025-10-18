from django.shortcuts import render

def index(request):
    context = {
        'judul': 'Scoreboard',
        'tim': [
            {'nama': 'Team A', 'skor': 78},
            {'nama': 'Team B', 'skor': 65},
            {'nama': 'Team C', 'skor': 90},
        ]
    }
    return render(request, 'scoreboard/index.html', context)