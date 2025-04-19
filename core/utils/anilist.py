import cv2
import requests
from io import BytesIO
import numpy as np

from steganography import embed_to_image
from steganography import extract_message
# API endpoint
url = 'https://graphql.anilist.co'

# GraphQL query to search for an anime by title
query = '''
query ($search: String) {
  Media(search: $search, type: ANIME) {
    title {
      romaji
      english
    }
    coverImage {
      large
      medium
    }
  }
}
'''

variables = {
    'search': 'Naruto'
}

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

# print(response.json())
if response.status_code == 200:
    data = response.json()
    title = data['data']['Media']['title']['romaji']
    cover = data['data']['Media']['coverImage']['large']

    # get image from anilist API
    response = requests.get(cover)
    imageStream = BytesIO(response.content)
    imageDecoded = cv2.imdecode(np.frombuffer(imageStream.read(), np.uint8), cv2.IMREAD_COLOR)
    cv2.imwrite("image/new3.png", imageDecoded)

    # read feteched image from anilist API
    # image = cv2.imread("image/new3.png") 

    # read image from local as sample
    # only this image work for steganography while other images are not working
    image = cv2.imread("image/capture.JPG") 

    
    embeddedMessage = embed_to_image(image, "hallo dari iqbal")

    # steganography image
    cv2.imwrite("image/hasil_stego.png", embeddedMessage)

    # extract message
    img = cv2.imread("image/hasil_stego.png")
    message = extract_message(img)
    print("Pesan disisipkan:", message)
else:
    print(f"Error: {response.status_code}")
