from google.appengine.ext import ndb

import os

import html
import subsurface

class Photo(object):

    def __init__(self):
        self.delete_link = ''
        self.small_thumb = ''
        self.large_thumb = ''
        self.link = ''


class Blob(object):

    '''
    A binary blob
    '''

    def __init__(self):
        self.ids = []

    def append(self, value):
        b = _Blob()
        b.blob = value
        key = b.put().id()
        self.ids.append(key)

    def get_all(self):
        blobs = [_Blob.get_by_id(i) for i in self.ids]
        return ''.join((i.blob for i in blobs))

    def delete(self):
        [_Blob.get_by_id(i).key.delete() for i in self.ids]


class _Blob(ndb.Model):
    blob = ndb.PickleProperty()


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
    photos = ndb.PickleProperty(default=[])
    userid = ndb.StringProperty(indexed=True)
    cached_parsed = ndb.PickleProperty()

    def __init__(self, *args, **kwargs):
        super(Dive, self).__init__(*args, **kwargs)

        self.delete_link = os.urandom(64).encode('hex')

    def get_html_elements(self):
        '''
        Returns a dictionary with the various components
        in html format, ready to be fed to make_table
        '''

        dive_id = str(self.key.id())

        # Create cached version of said dictionary
        if self.cached_parsed is None:
            if self.dive_format == 'subsurface':
                self.cached_parsed = subsurface.parse(self.dive_data.encode('utf-8'))
                self.put()
            else:
                raise Exception("Corrupt data in dive %d" % self.key.id())

        data = {k:v for k,v in self.cached_parsed.iteritems()}

        data['related'] = html.related_dives(self.get_related(), "Related dives")

        if self.userid is None:
            data[
                'assign'] = '<a href="/dive/%s/assign_confirm">I did this dive!</a>&nbsp;' % dive_id

        data['photo'] = html.photo(self.photos, dive_id)

        return data




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
                Dive.computer_id == self.computer_id, Dive.userid == self.userid)
        else:
            query = Dive.computer_id == self.computer_id

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
