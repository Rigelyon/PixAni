from django.http import JsonResponse
import requests

api_url = 'https://graphql.anilist.co'

def get_anime_data(anime_title):
    query = '''
    query ($search: String) {
        Media(search: $search, type: ANIME) {
          id
          title {
            romaji
            english
            native
          }
          type
          episodes
          seasonYear
          genres
          description
          averageScore
          coverImage {
            extraLarge
            medium
          }
          studios {
            nodes {
              name
            }
        }
        source
      }
    }
    '''

    variables = {
        'search': anime_title
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    try:
      response = requests.post(api_url, json={'query': query, 'variables': variables}, headers=headers)
      data = response.json()
      media = data['data']['Media']

      studio_name = ''
      if media['studios']['nodes']:
          studio_name = media['studios']['nodes'][0]['name']

      formatted_data = {
          'id': media['id'],
          'title': {
              'romaji': media['title']['romaji'],
              'english': media['title']['english'],
              'native': media['title']['native']
          },
          'type': media['type'],
          'episodes': media['episodes'],
          'year': media['seasonYear'],
          'genres': media['genres'],
          'synopsis': media['description'],
          'studio': studio_name,
          'rating': media['averageScore'] / 10 if media['averageScore'] else None,
          'source': media['source'],
          'cover': {
              'extraLarge': media['coverImage']['extraLarge'],
          }
      }

      return formatted_data
        
    except Exception as e:
        print(f"Exception when fetching anime data: {e}")
        return None
    
def search_suggestions(query):
    try:
        response = requests.post(
            api_url,
            json={
                'query': '''
                    query ($search: String) {
                        Page(page: 1, perPage: 5) {
                            media(search: $search, type: ANIME) {
                                title {
                                    romaji
                                }
                                coverImage {
                                    medium
                                }
                            }
                        }
                    }
                ''',
                'variables': {'search': query},
            },
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()
        results = [
            {
                'title': anime['title']['romaji'],
                'cover': anime['coverImage']['medium']
            }
            for anime in data['data']['Page']['media']
        ]
        return results
    except Exception as e:
        print(f"Exception when fetching anime search query: {e}")
        return None