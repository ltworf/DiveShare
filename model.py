from google.appengine.ext import ndb

import os


class Photo(object):

    def __init__(self):
        self.delete_link = ''
        self.small_thumb = ''
        self.large_thumb = ''
        self.link = ''


class Tag(ndb.Model):
    dives = ndb.PickleProperty(indexed=False, default=[])

    @staticmethod
    def add_dive(name, dive):
        t = Tag.get_or_insert(name.lower())
        t.dives.append((str(dive.key.id()), dive.title))
        t.put()

    @staticmethod
    def remove_dive(name, dive):
        k = ndb.Key(Tag, name)
        d = k.get()

        if d is None:
            raise Exception("Tag %s does not exist" % name)

        for index, tl in enumerate(d.dives):
            if tl[0] == str(dive):
                d.dives.pop(index)
                break
        d.put()

    @staticmethod
    def get_dives(name):
        k = ndb.Key(Tag, name)
        d = k.get()
        if d is None:
            return []
        return d.dives


class Dive(ndb.Model):
    # String representing a divecomputer
    computer_id = ndb.StringProperty(indexed=True)
    trip = ndb.StringProperty(indexed=True)

    # objects representing the divelog
    dive_data = ndb.PickleProperty(indexed=False)

    # String telling in which format dive_data is
    dive_format = ndb.StringProperty(indexed=False)

    # Secret code to delete this dive
    delete_link = ndb.StringProperty(indexed=True)

    # Title of the dive
    title = ndb.StringProperty(indexed=True)

    # Index (per sub, not total index in the db)
    index = ndb.IntegerProperty(indexed=False)
    lat = ndb.FloatProperty()
    lon = ndb.FloatProperty()
    date = ndb.DateProperty()

    # Photos
    photos = ndb.PickleProperty(default=[])

    # User who did this dive (None by default)
    userid = ndb.StringProperty(indexed=True)

    # If private, do not show in related
    private = ndb.BooleanProperty(default=False)

    def __init__(self, *args, **kwargs):
        super(Dive, self).__init__(*args, **kwargs)

        self.delete_link = os.urandom(64).encode('hex')

    def add_photo(self, links):
        '''
        Adds a photo. Doesn't call put()
        '''
        p = Photo()
        p.link = links['link']
        p.large_thumb = links['large_thumb']
        p.small_thumb = links['small_thumb']
        p.delete_link = links['delete_link']
        self.photos.append(p)

    def get_related(self):
        '''
        Returns an iterable of "Dive"s, which are related
        to this one.
        '''

        if self.userid is not None:
            query = ndb.OR(
                ndb.AND(Dive.computer_id == self.computer_id, Dive.userid == self.userid), Dive.private == False)
        else:
            query = ndb.AND(
                Dive.computer_id == self.computer_id, Dive.private == False)

        related = Dive.query(query).filter(Dive.key != self.key).fetch(20)

        return related

    @staticmethod
    def get_same_user(userid):
        '''
        Returns all the dives from the same user
        '''
        query = Dive.userid == userid
        result = list(Dive.query(query))

        '''this is terrible but .order from the query returns
        no results'''

        result.sort(key=lambda x: x.index)
        return result

    @staticmethod
    def delete(del_key):
        '''
        Deletes the dive with the given
        del_key.

        Returns the dive on success or None on failure
        '''
        to_del = Dive.query(Dive.delete_link == del_key)
        for i in to_del:
            i.key.delete()
            return i
        return None

    @staticmethod
    def get_dives():
        return Dive.query(Dive.private == False).fetch(20)

    @staticmethod
    def get_multi(ids):
        return ndb.get_multi([ndb.Key(Dive, int(k)) for k in ids])
