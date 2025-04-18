from django.shortcuts import redirect, render

def home(request):
    return render(request, 'core/home.html')

def anime_detail(request):
    return redirect('core:home')

def process_image(request):
    return redirect('core:home')