import os
import urllib
import json
import datetime

import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
import jinja2

import html
from model import Dive
from dive_profile import draw_profile
import tasks
import memcache


def error(response, code, message=''):
    template_values = {'h1': 'Error %d' % code,
                       'p': message}
    template = templater.get_template('templates/generic.html')
    response.write(template.render(template_values))
    response.status = code


templater = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):

    def get(self):

        self.response.headers['Content-Type'] = 'text/html'
        self.response.headers['Cache-Control'] = 'max-age=14400'

        def response():
            template_values = {
                'photo_name': html.random_image(),
                'dives': Dive.get_dives(),
            }
            template = templater.get_template('templates/index.html')
            return template.render(template_values)

        self.response.write(
            memcache.get('main_page', response, time=600))


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

        dives = self.create_dives(data, False)
        template_values = {'dives': dives}

        template = templater.get_template('templates/upload.html')
        self.response.write(template.render(template_values))

    def put(self):

        private = bool(self.request.str_GET.get('private', False))

        dives = self.create_dives(self.request.body[6:], private)

        for i in dives:
            self.response.out.write(','.join(i) + '\n')

    def create_dives(self, json_string, private):
        '''
        Creates all the dives contained in a subsurface json.

        json_string: the string containing the json
        private: boolena, whether or not mark them as private.

        Returns [("dive_id","dive_delete_id")]
        '''
        r = []
        trips = json.loads(json_string)

        for trip in trips:
            f = lambda x: self.create_dive(trip['name'], x, private)
            r += map(f, trip['dives'])
        return r

    def create_dive(self, name, dive, private):
        '''
        name: trip name
        dive: subsurface json for a single dive
        private: boolean, is the dive private?

        Returns ("dive_id","dive_delete_id","dive_title")
        '''

        dive_object = Dive()

        # Escape notes, keeping new lines.
        dive['notes'] = dive.get('notes', '').replace(
            '<br>', '\n').replace('<', '&lt;').replace('\n', '<br>')

        dive_object.dive_data = dive
        dive_object.dive_format = "json_subsurface"
        dive_object.trip = name
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
        dive_object.tags = ','.join(dive.get('tags', []))

        dive_object.private = private
        dive_object.put()

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
            template_values = {
                'dive': dive,
                'related': related,
                'profile': draw_profile(dive.dive_data.get('samples', []), 600, 400),
            }
            template = templater.get_template('templates/dive.html')
            return template.render(template_values)

        self.response.write(memcache.get(key, response))


class MyDives(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()

        if not user:
            login_uri = users.create_login_url('/my')
            self.redirect(login_uri)
            return
        self.response.headers['Cache-Control'] = 'max-age=600'
        template_values = {'dives': Dive.get_same_user(user.user_id())}

        template = templater.get_template('templates/my.html')
        self.response.write(template.render(template_values))


class AssociateDive(webapp2.RequestHandler):

    def get(self):
        ids = self.request.str_GET.get('dives', '')
        uri = '/associate?dives=' + ids
        user = users.get_current_user()
        if not user:
            login_uri = users.create_login_url(uri)
            self.redirect(login_uri)
            return

        self.response.headers['Cache-Control'] = 'max-age=14400'

        template_values = {'uri': uri}
        # TODO make this form nicer and clearer

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
        if not r:
            self.response.status = 404
            return

    def post(self, delete_id):
        r = Dive.delete(delete_id)
        if not r:
            error(self.response, 404)
        else:
            template_values = {'h1': 'Dive deleted',
                               'p': 'Your dive was deleted'}

        template = templater.get_template('templates/generic.html')
        self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/dive/(\d+)', ShowDive),
    ('/associate', AssociateDive),
    ('/help', Help),
    ('/upload', UploadDive),
    ('/my', MyDives),
    ('/add_photo/(\d+)', PhotoSubmit),
    ('/post_photo/(\d+)', UploadHandler),
    #('/serve/([^/]+)?', ServeHandler)
    ('/delete/dive/([0-9a-f]+)', DeleteDive),
    # TODO delete endpoint
], debug=True)
