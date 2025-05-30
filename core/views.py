import json
import os
import re
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import requests
from io import BytesIO
from PIL import Image

from core.forms import AnilistLinkForms, UserDataForm
from core.utils.anilist import get_anime_data_by_id, get_anime_data_by_search, search_suggestions
from core.utils.steganography import embed_message, extract_message, test_extract_data
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.management import call_command

def home(request):
    form = AnilistLinkForms()
    return render(request, 'core/home.html', {'form': form})

def anime_detail(request):
    if request.method == 'POST':
        form = AnilistLinkForms(request.POST)
        if form.is_valid():
            anilist_search = form.cleaned_data['anilist_search']

            # Clear session data only for new searches
            request.session.pop('anime_data', None)
            request.session.pop('user_data', None)

            anime_data = get_anime_data_by_search(anilist_search)
            if not anime_data:
                messages.error(request, 'Failed to retrieve Anime data.')
                return redirect('core:home')
            
            request.session['anime_data'] = anime_data
            request.session['user_data'] = {
                'user_rating': None,
                'link_1': None,
                'notes': None,
                'link_2': None,
                'link_3': None
            }

            user_data = UserDataForm()
            return render(request, 'core/anime_detail.html', {
                'anime': anime_data,
                'user_data': user_data
            })
        
    # Retain session data for page refreshes
    anime_data = request.session.get('anime_data')
    user_data = request.session.get('user_data')
    if anime_data:
        if not user_data:
            user_data = {
                'user_rating': None,
                'link_1': None,
                'notes': None,
                'link_2': None,
                'link_3': None
            }
        user_data_form = UserDataForm(initial=user_data)
        return render(request, 'core/anime_detail.html', {
            'anime': anime_data,
            'user_data': user_data_form,
        })

    return redirect('core:home')

@csrf_exempt
def process_image(request):
    if request.method == 'POST':
        call_command('clear_embedded_images')

        anime_data = request.session.get('anime_data')
        if not anime_data:
            messages.error(request, 'No anime data found in session.', status=400)
            return redirect('core:home')
        
        user_data = UserDataForm(request.POST)
        if user_data.is_valid():
            user_data = {
                'user_rating': user_data.cleaned_data.get('user_rating') or None,
                'link_1':user_data.cleaned_data.get('link_1') or None,
                'notes':user_data.cleaned_data.get('notes') or None,
                'link_2':user_data.cleaned_data.get('link_2') or None,
                'link_3':user_data.cleaned_data.get('link_3') or None,
            }

            request.session['user_data'] = user_data

            data_to_embed = {
                'id': anime_data['id'],
                'user_data': user_data
            }

            try:
                response = requests.get(anime_data['cover'])
                cover = Image.open(BytesIO(response.content))

                safe_title = re.sub(r'[^\w\s-]', '', anime_data['title']['english']).strip().replace(' ', '_')
                filename = f"{safe_title}_cover.png"

                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'embedded_images'), exist_ok=True)

                temp_path = os.path.join(settings.MEDIA_ROOT, 'embedded_images', filename)
                download_path = f"media/embedded_images/{filename}"

                data_str = json.dumps(data_to_embed)
                embed_message(cover, data_str, filename=filename)

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
                'errors': user_data.errors
            }, status=400)
        
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)

@csrf_exempt
def decode_image(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES.get('image')
            if not isinstance(uploaded_file, InMemoryUploadedFile):
                return JsonResponse({'success': False, 'error': 'Invalid file upload'}, status=400)

            image = Image.open(uploaded_file)
            decoded_data_str = extract_message(image)
            
            try:
                decoded_data = json.loads(decoded_data_str)
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Decoded data is not valid JSON'}, status=500)

            anime_id = decoded_data['id']
            anime_data = get_anime_data_by_id(anime_id)
            if not anime_data:
                return JsonResponse({'success': False, 'error': 'Failed to refetch anime data from AniList'}, status=500)

            request.session['anime_data'] = anime_data
            request.session['user_data'] = decoded_data['user_data']

            return JsonResponse({
                'success': True,
                'message': 'Data decoded successfully.',
                'anime_data': anime_data,
                'user_data': decoded_data['user_data']
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)

def anime_search(request):
    query = request.GET.get('query', '')
    results = search_suggestions(query)
    if results:
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})