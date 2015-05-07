import httplib
from urlparse import urlparse


class Connection(httplib.HTTPConnection):

    '''
    Same thing as HTTPConnection but
    can be used in a with block
    '''

    def __exit__(self, type, value, traceback):
        self.close()

    def __enter__(self):
        return self


def is_imgur_good(url_string):
    '''
    Checks if an imgur link is good or bad
    '''
    url = urlparse(url_string)

    with Connection(url.netloc) as connection:
        connection.request("HEAD",
                           url.path
                           )

        response = connection.getresponse()

        if response.status != 200:
            return False

        # Some weird gifs have been added, they seem like an exploit of sorts
        if response.getheader('Content-Length', '0') == '41':
            return False
        return True
