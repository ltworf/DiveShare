import os
import urllib
import json
import datetime
import md5
import base64
import time

import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
import jinja2

import html
import http
from model import Dive, Tag
from dive_profile import draw_profile
import tasks
import memcache
import uid_secret


def error(response, code, message=''):
    template_values = {'h1': 'Error %d' % code,
                       'p': message}
    template = templater.get_template('templates/generic.html')
    response.write(template.render(template_values))
    response.status = code


def login(uri, response):
    response.set_cookie('has_session', 'true', max_age=86400)
    response.status = 302
    response.headers['Location'] = users.create_login_url(uri)

templater = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):

    def get(self):

        self.response.headers['Content-Type'] = 'text/html'
        self.response.headers['Cache-Control'] = 'max-age=14400'

        # Cache stuff
        request_etag = float(self.request.headers.get('If-None-Match', '"0"')[1:-1])
        if time.time() - request_etag < 14400:
            self.response.status = 304
            return
        key = str(time.time())
        self.response.etag = key

        def response():
            template_values = {
                'photo_name': html.random_image(),
                'dives': Dive.get_dives(),
            }
            template = templater.get_template('templates/index.html')
            return template.render(template_values)

        self.response.write(
            memcache.get('main_page', response, time=600))


class ManualUpload(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.headers['Cache-Control'] = 'max-age=259200'

        def response():
            template = templater.get_template('templates/manual_upload.html')
            return template.render({})

        self.response.write(
            memcache.get('manual_upload', response))


class Help(webapp2.RequestHandler):

    def get(self):

        self.response.headers['Content-Type'] = 'text/html'
        self.response.headers['Cache-Control'] = 'max-age=14400'

        def response():
            template_values = {
                'photo_name': html.random_image(),
            }
            template = templater.get_template('templates/help.html')
            return template.render(template_values)
        self.response.write(memcache.get('help_page', response))


class UploadDive(webapp2.RequestHandler):

    def post(self):

        # TODO put a checkbox to make them private in the form
        try:
            data = self.request.str_POST['log'].file.read(
                50000000
            )[6:]
        except:
            error(self.response, 400, 'Missing upload')
            return

        dives = self.create_dives(data, False, None)
        template_values = {'dives': dives,
                           'associate': ','.join(i[0] for i in dives)}

        template = templater.get_template('templates/upload.html')
        self.response.write(template.render(template_values))

    def put(self):

        private = bool(self.request.str_GET.get('private', False))

        client_uid = self.request.headers.get('X-UID', None)
        if client_uid:
            uid = ShowUID.validate_uid(client_uid)
        else:
            uid = None

        dives = self.create_dives(self.request.body[6:], private, uid)

        for i in dives:
            self.response.out.write(','.join(i) + '\n')

    def create_dives(self, json_string, private, uid):
        '''
        Creates all the dives contained in a subsurface json.

        json_string: the string containing the json
        private: boolena, whether or not mark them as private.
        uid: None or string, the user id of the owner of the dive

        Returns [("dive_id","dive_delete_id")]
        '''
        r = []
        trips = json.loads(json_string)

        for trip in trips:
            f = lambda x: self.create_dive(trip['name'], x, private, uid)
            r += map(f, trip['dives'])
        return r

    def create_dive(self, name, dive, private, uid):
        '''
        name: trip name
        dive: subsurface json for a single dive
        private: boolean, is the dive private?
        uid: None or string, the user id of the owner of the dive

        Returns ("dive_id","dive_delete_id","dive_title")
        '''

        dive_object = Dive.create_or_edit(
            dive.get('subsurface_number', 0), uid)

        # Escape notes, keeping new lines.
        dive['notes'] = html.escape_notes(dive.get('notes', ''))

        dive_object.dive_data = dive
        dive_object.dive_format = "json_subsurface"
        dive_object.trip = name
        if uid:
            dive_object.userid = uid

        try:
            dive_object.computer_id = dive['divecomputers']['deviceid']
        except:
            pass

        dive_object.title = dive.get('location', 'untitled')
        dive_object.index = dive.get('subsurface_number', 0)
        coordinates = dive.get('coordinates')
        if coordinates:
            dive_object.lat = float(coordinates['lat'])
            dive_object.lon = float(coordinates['lon'])
        dive_object.date = datetime.date(
            *[int(i) for i in dive['date'].split('-')])

        dive_object.private = private
        dive_object.put()
        if not private:
            tasks.tag_dive(dive_object)

        return (
            str(dive_object.key.id()),
            dive_object.delete_link,
            dive_object.title
        )


class ShowDive(webapp2.RequestHandler):

    def get(self, dive_id):
        dive = Dive.get_by_id(int(dive_id))
        if dive is None:
            error(self.response, 404)
            return

        # Cache stuff
        key = '%s-%d-%s' % (dive_id, len(dive.photos), dive.userid)
        self.response.etag = key
        request_etag = self.request.headers.get('If-None-Match', '""')[1:-1]
        if request_etag == key:
            self.response.status = 304
            return

        def response():
            related = dive.get_related()

            #TODO maybe other perks for different gasses?
            nitrox = len(filter(lambda x: x.get('O2','Air') != 'Air', dive.dive_data['Cylinders'])) != 0
            template_values = {
                'nitrox': nitrox,
                'dive': dive,
                'related': related,
                'description': dive.dive_data['notes'].split('<br>')[0],
                'fake_thumb': html.random_image(),
                'profile': draw_profile(dive.dive_data.get('samples', []), 600, 400),
            }
            template = templater.get_template('templates/dive.html')
            return template.render(template_values)

        self.response.write(memcache.get(key, response))


class ShowProfile(webapp2.RequestHandler):

    def get(self, dive_id):
        width = int(self.request.get('width', default_value=600))
        height = int(self.request.get('height', default_value=400))
        dive = Dive.get_by_id(int(dive_id))
        if dive is None:
            error(self.response, 404)
            return
        key = 'profile-%s-%d-%d' % (dive_id, width, height)
        self.response.etag = key
        request_etag = self.request.headers.get('If-None-Match', '""')[1:-1]
        if request_etag == key:
            self.response.status = 304
            return

        def response():
            return draw_profile(dive.dive_data.get('samples', []), width, height)

        self.response.write(memcache.get(key, response))


class ShowUser(webapp2.RequestHandler):

    def get(self, userid):
        user = users.get_current_user()
        authuserid = user.user_id() if user is not None else ''

        self.response.headers['Cache-Control'] = 'max-age=600'
        dives = Dive.get_same_user(userid)

        key = userid + str(authuserid == userid) + str(len(dives))
        self.response.etag = key
        request_etag = self.request.headers.get('If-None-Match', '""')[1:-1]
        if request_etag == key:
            self.response.status = 304
            return

        def response():
            template_values = {'dives': dives,
                               'authenticated': authuserid == userid,
                               'userid': userid
                               }
            template = templater.get_template('templates/my.html')
            return template.render(template_values)
        self.response.write(memcache.get(key, response))


class MyDives(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()

        if not user:
            return login('/my', self.response)
        self.redirect('/user/%s' % user.user_id())


class AssociateDive(webapp2.RequestHandler):

    def get(self):
        ids = self.request.str_GET.get('dives', '')
        uri = '/associate?dives=' + ids
        user = users.get_current_user()
        if not user:
            return login(uri, self.response)

        self.response.headers['Cache-Control'] = 'max-age=14400'

        template_values = {'uri': uri}

        template = templater.get_template('templates/associate_form.html')
        self.response.write(template.render(template_values))

    def post(self):
        user = users.get_current_user()
        if not user:
            error(self.response, 412)
            return
        ids = self.request.str_GET.get('dives', '').split(',')

        error = False
        for dive in Dive.get_multi(ids):
            if dive.userid is not None:
                error = True
                continue
            dive.userid = user.user_id()
            dive.put()

        template_values = {}
        template_values['h2'] = 'Associate dive to account'

        if error:
            error(self.response, 400)
            return
        else:
            template_values['p'] = 'All dives were associated to your account.'

        template = templater.get_template('templates/generic.html')
        self.response.write(template.render(template_values))


class PhotoSubmit(webapp2.RequestHandler):

    def get(self, dive_id):
        upload_url = blobstore.create_upload_url('/post_photo/' + dive_id)

        self.response.headers['Cache-Control'] = 'max-age=60'
        self.response.headers.add_header("X-Post-Url", upload_url)

        template_values = {'h2': 'Select image files',
                           'p': '<form action="%s" method="POST" enctype="multipart/form-data">Upload File: <input type="file" name="file" multiple><br> <input type="submit" name="submit" value="Submit"></form>' % upload_url
                           }

        template = templater.get_template('templates/generic.html')
        self.response.write(template.render(template_values))


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):

    def post(self, dive_id):
        upload_files = self.get_uploads(
            'file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]

        tasks.upload_photo(
            [i.key() for i in upload_files],
            dive_id
        )

        template_values = {'h2': 'Upload complete',
                           'p': 'Your photos have been uploaded and will be processed shortly. Please don\'t upload them again.<br><a href="/dive/%s">Go back to your dive</a>' % dive_id
                           }

        template = templater.get_template('templates/generic.html')
        self.response.write(template.render(template_values))


class TaggedDives(webapp2.RequestHandler):

    def get(self, tag):
        self.response.headers['Cache-Control'] = 'max-age=14400'
        if tag is None:
            #No tag selected
            tags = Tag.get_tags()
            template = templater.get_template('templates/tags.html')
            self.response.write(templater.render({'tags':tags}))
            return

        dives = Tag.get_dives(tag.lower())
        data = {'dives': dives,
                'tag': tag}

        # TODO use Etag and/or memcache

        template = templater.get_template('templates/tag.html')
        self.response.write(template.render(data))


class DeleteDive(webapp2.RequestHandler):

    def get(self, delete_id):
        ids = self.request.str_GET.get('dives', '')
        uri = '/delete/dive/' + delete_id
        self.response.headers['Cache-Control'] = 'max-age=14400'

        template_values = {'uri': uri}
        template = templater.get_template('templates/delete_form.html')
        self.response.write(template.render(template_values))

    def delete(self, delete_id):
        r = Dive.delete(delete_id)
        if r is None:
            self.response.status = 404
        else:
            tasks.untag_dive(r)

    def post(self, delete_id):
        r = Dive.delete(delete_id)
        if r is None:
            error(self.response, 404)
            return
        else:
            tasks.untag_dive(r)
            template_values = {'h1': 'Dive deleted',
                               'p': 'Your dive was deleted'}

        template = templater.get_template('templates/generic.html')
        self.response.write(template.render(template_values))


class ShowUID(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if not user:
            return login('/secret', self.response)

        secret = ShowUID.generate_uid(
            user.user_id(),
            user.email(),
            ''  # TODO
        )

        self.response.write(secret)

    @staticmethod
    def generate_uid(uid, email, changed=''):
        data = ','.join((uid, email, changed))
        hashed = md5.md5(data + uid_secret.SECRET).hexdigest()

        data = base64.b64encode(data + ',' + hashed)

        return data

    @staticmethod
    def validate_uid(data):
        uid, email, changed, hashed = base64.b64decode(data).split(',')
        data = ','.join((uid, email, changed))
        if hashed != md5.md5(data + uid_secret.SECRET).hexdigest():
            raise Exception('Invalid')

        # TODO check changed
        return uid


class Logout(webapp2.RequestHandler):

    def get(self):
        self.response.set_cookie('has_session', '')
        self.response.set_cookie('ACSID', '')
        self.response.set_cookie('dev_appserver_login', '')

        self.response.status = 302
        self.response.headers['Location'] = '/'


class TaskPhotoCleanup(webapp2.RequestHandler):

    def get(self):
        if self.request.headers.get('X-Appengine-Cron', None) is None:
            raise Exception('Invalid header')
        tasks.cleanup_photos()


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/manual_upload', ManualUpload),
    ('/dive/(\d+)', ShowDive),
    ('/profile/(\d+)', ShowProfile),
    ('/associate', AssociateDive),
    ('/help', Help),
    ('/upload', UploadDive),
    ('/secret', ShowUID),
    ('/my', MyDives),
    ('/user/(\d+)', ShowUser),
    ('/add_photo/(\d+)', PhotoSubmit),
    ('/post_photo/(\d+)', UploadHandler),
    ('/tag/([^/]+)?', TaggedDives),
    ('/delete/dive/([0-9a-f]+)', DeleteDive),
    ('/logout', Logout),

    ('/tasks/imgur_cleanup', TaskPhotoCleanup),
], debug=False)
