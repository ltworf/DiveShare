import json
import base64
import urllib

from http import Connection
from imgur_key import api_key  # To keep it a secret on git


class UploadException(Exception):
    pass


def upload_image(image, title="Diveshare"):
    '''
    Uploads an image.

    image is the image in a string

    Returns a dictionary containing:

    delete_link
    small_thumb
    large_thumb
    link
    '''

    b64image = base64.b64encode(image)

    payload = {
        'key': api_key,
        'image': b64image,
        'title': title
    }

    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"
    }

    with Connection('api.imgur.com') as connection:

        connection.request("POST",
                           "/2/upload.json",
                           urllib.urlencode(payload),
                           headers
                           )

        response = connection.getresponse()

        if response.status != 200:
            raise UploadException(response)

        data = json.loads(response.read())
        links = data['upload']['links']

        r = {'delete_link': links['delete_page'],
             'small_thumb': links['small_square'],
             'large_thumb': links['large_thumbnail'],
             'link': links['original'],
             }
        return r
