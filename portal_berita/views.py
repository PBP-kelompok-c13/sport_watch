from django.shortcuts import render

"""
MODELS <-<>-> VIEWS <-<>-> TEMPLATES

models.py -> merupakan data & logika bisnis
template.py -> tampilan akhir yang dilihat oleh pengguna
views.pt -> yang menghubungi data (atau model) dan tampilan (template)


"""

def portalnews_info(request):
    context = {
        'Welcome' : 'Welcome to Sport Watch!',
        'Who': 'Presented By Kelompok C 13',
    }

    return render(request, "portal_berita.html", context)

# Create your views here.
