from google.appengine.ext import ndb

import os


class Dive(ndb.Model):
    computer_id = ndb.StringProperty(indexed=True)
    dive_data = ndb.StringProperty(indexed=False)
    dive_format = ndb.StringProperty(indexed=False)
    delete_link = ndb.StringProperty(indexed=True)

    def __init__(self, *args, **kwargs):
        super(Dive, self).__init__(*args, **kwargs)

        self.delete_link = os.urandom(64).encode('hex')
