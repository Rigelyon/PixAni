import json
import os
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import requests
from io import BytesIO
from PIL import Image

from core.forms import AnilistLinkForms, UserDataForm
from core.utils.anilist import get_anime_data
from core.utils.steganography import embed_data_in_image

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
    if request.method == 'POST':
        anime_data = request.session.get('anime_data')
        if not anime_data:
            messages.error(request, 'No anime data found in session.', status=400)
            return redirect('core:home')
        
        user_data_form = UserDataForm(request.POST)
        if user_data_form.is_valid():
            user_data = {
                'personal_rating': user_data_form.cleaned_data.get('personal_rating'),
                'review': user_data_form.cleaned_data.get('review'),
                'notes': user_data_form.cleaned_data.get('notes'),
                'download_link_1080p': user_data_form.cleaned_data.get('download_link_1080p'),
                'download_link_720p': user_data_form.cleaned_data.get('download_link_720p'),
                'download_link_480p': user_data_form.cleaned_data.get('download_link_480p'),
                'download_link_360p': user_data_form.cleaned_data.get('download_link_360p'),
            }

            data_to_embed = {
                'anime': {
                    'id': anime_data['id'],
                    'title': {
                        'english': anime_data['title']['english'],
                        'native': anime_data['title']['native'],
                        'romaji': anime_data['title']['romaji']
                    },
                    'synopsis': anime_data['synopsis'],
                    'type': anime_data['type'],
                    'episodes': anime_data['episodes'],
                    'year': anime_data['year'],
                    'genres': anime_data['genres'],
                    'studio': anime_data['studio'],
                    'rating': anime_data['rating'],
                    'source': anime_data['source'],
                },
                'user_data': user_data
            }

            try:
                response = requests.get(anime_data['cover'])
                cover = Image.open(BytesIO(response.content))

                filename = f"{anime_data['title']['english'].replace(' ', '_')}_cover.png"

                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'embedded_images'), exist_ok=True)

                temp_path = os.path.join(settings.MEDIA_ROOT, 'embedded_images', filename)
                download_path = os.path.join('media', 'embedded_images', filename)

                data_str = json.dumps(data_to_embed)
                embedded_images = embed_data_in_image(cover, data_str)

                embedded_images.save(temp_path, format='PNG')

                download_url = request.build_absolute_uri(f"/{download_path}")

                return JsonResponse({
                    'success': True,
                    'message': 'Data embedded successfully.',
                    'download_url': download_url,
                    'anime_data': anime_data,
                    'user_data': user_data
                })

            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid form data.',
                'errors': user_data_form.errors
            }, status=400)
        
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)