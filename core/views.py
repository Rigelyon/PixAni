from django.shortcuts import redirect, render
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from core.forms import AnilistLinkForms, UserDataForm
from core.utils.anilist import get_anime_data

def home(request):
    form = AnilistLinkForms()
    return render(request, 'core/home.html', {'form': form})

def anime_detail(request):
    if request.method == 'POST':
        form = AnilistLinkForms(request.POST)
        if form.is_valid():
            anilist_search = form.cleaned_data['anilist_search']

            anime_data = get_anime_data(anilist_search)
            if not anime_data:
                messages.error(request, 'Failed to retrieve Anime data.')
                return redirect('core:home')
            
            request.session['anime_data'] = anime_data

            user_data_form = UserDataForm()
            return render(request, 'core/anime_detail.html', {
                'anime': anime_data,
                'user_data_form': user_data_form
            })
        
    anime_data = request.session.get('anime_data')
    if anime_data:
        user_data_form = UserDataForm()
        return render(request, 'core/anime_detail.html', {
            'anime': anime_data,
            'user_data_form': user_data_form
        })

    return redirect('core:home')

@csrf_exempt
def process_image(request):
    return redirect('core:home')