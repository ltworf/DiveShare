from google.appengine.ext import ndb

import os


class Dive(ndb.Model):
    computer_id = ndb.StringProperty(indexed=True)
    dive_data = ndb.StringProperty(indexed=False)
    dive_format = ndb.StringProperty(indexed=False)
    delete_link = ndb.StringProperty(indexed=True)
    title = ndb.StringProperty(indexed=True)
    index = ndb.IntegerProperty(indexed=False)
    lat = ndb.FloatProperty()
    lon = ndb.FloatProperty()
    date = ndb.DateProperty()
    tags = ndb.StringProperty(indexed=True)

    def __init__(self, *args, **kwargs):
        super(Dive, self).__init__(*args, **kwargs)

        self.delete_link = os.urandom(64).encode('hex')

    def get_related(self):
        '''
        Returns an iterable of "Dive"s, which are related
        to this one.
        '''

        related = Dive.query(Dive.computer_id == self.computer_id).filter(
            Dive.key != self.key).fetch(20)

        return related

    @staticmethod
    def delete(del_key):
        '''
        Deletes the dive with the given
        del_key.

        Returns true on success.
        '''
        to_del = Dive.query(Dive.delete_link == del_key)
        for i in to_del:
            i.key.delete()
            return True
        return False

    @staticmethod
    def get_dives():
        return Dive.query().fetch(20)
