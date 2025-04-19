from django.shortcuts import redirect, render

from core.forms import AnilistLinkForms

def home(request):
    form = AnilistLinkForms()
    return render(request, 'core/home.html', {'form': form})

def anime_detail(request):
    return redirect('core:home')

def process_image(request):
    return redirect('core:home')