import cv2
import requests
from io import BytesIO
import numpy as np

# from new_steganography import embed_to_image
# from new_steganography import extract_message

def get_anime_data(anime_title):
    url = 'https://graphql.anilist.co'

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
      response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
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
          'cover': media['coverImage']['extraLarge']
      }

      return formatted_data
        
    except Exception as e:
        print(f"Exception when fetching anime data: {e}")
        return None

        # # get image from anilist API
        # response = requests.get(cover)
        # imageStream = BytesIO(response.content)
        # imageDecoded = cv2.imdecode(np.frombuffer(imageStream.read(), np.uint8), cv2.IMREAD_COLOR)
        # cv2.imwrite("image/new3.png", imageDecoded)

        # # read feteched image from anilist API
        # # image = cv2.imread("image/new3.png") 

        # # read image from local as sample
        # # only this image work for steganography while other images are not working
        # image = cv2.imread("image/capture.JPG") 

        
        # embeddedMessage = embed_to_image(image, "hallo dari iqbal")

        # # steganography image
        # cv2.imwrite("image/hasil_stego.png", embeddedMessage)

        # # extract message
        # img = cv2.imread("image/hasil_stego.png")
        # message = extract_message(img)
        # print("Pesan disisipkan:", message)
