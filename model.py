from google.appengine.ext import ndb

import os
import random


class Photo(object):

    def __init__(self):
        self.delete_link = ''
        self.small_thumb = ''
        self.large_thumb = ''
        self.link = ''


class Tag(ndb.Model):
    dives = ndb.PickleProperty(indexed=False, default={})

    @staticmethod
    def get_tags():
        return Tag.query().fetch(400)

    @staticmethod
    def add_dive(name, dive):
        t = Tag.get_or_insert(name.lower())
        t.dives[str(dive.key.id())] = dive.title
        t.put()

    @staticmethod
    def remove_dive(name, dive):
        dive = str(dive)
        k = ndb.Key(Tag, name)
        d = k.get()

        if d is None:
            raise Exception("Tag %s does not exist" % name)

        try:
            del d.dives[dive]
            d.put()
        except KeyError:
            pass

    @staticmethod
    def get_dives(name):
        k = ndb.Key(Tag, name)
        d = k.get()
        if d is None:
            return []
        return (i for i in d.dives.iteritems())


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
    index = ndb.IntegerProperty(indexed=True)
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

    @staticmethod
    def create_or_edit(index, uid):
        '''
        This is used to edit old dives.

        Only assigned dives can be edited.

        If index and user-id match, this returns an
        older dive, otherwise returns a newly created
        one.
        '''
        if uid is None:
            return Dive()

        query = ndb.AND(Dive.index == index, Dive.userid == uid)

        older = list(Dive.query(query).fetch(1))
        if len(older) != 0:
            return older[0]
        return Dive()

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
    def get_all():
        return Dive.query()

    @staticmethod
    def get_dives():
        yielded = 0
        for dive in Dive.query(Dive.private == False).fetch(200):
            if yielded >= 20:
                break
            if random.random() > 0.8:
                yielded += 1
                yield dive

    @staticmethod
    def get_multi(ids):
        return ndb.get_multi([ndb.Key(Dive, int(k)) for k in ids])
