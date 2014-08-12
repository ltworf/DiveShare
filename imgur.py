import json
import base64
import urllib
import httplib

from imgur_key import api_key  # To keep it a secret on git


class UploadException(Exception):
    pass


class Connection(httplib.HTTPConnection):

    '''
    Same thing as HTTPConnection but
    can be used in a with block
    '''

    def __exit__(self, type, value, traceback):
        self.close()

    def __enter__(self):
        return self


def upload_image(f, title="Diveshare"):
    '''
    Uploads an image.

    f must be something that supports read
    and it won't be closed here.

    Returns a dictionary containing:

    delete_link
    small_thumb
    large_thumb
    link
    '''

    binary_data = f.read(2854790)
    b64image = base64.b64encode(binary_data)

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
