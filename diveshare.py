from google.appengine.ext import deferred
from google.appengine.api import users

import diver_framework
import html
import subsurface
from model import Dive, Photo, Blob
import imgur


application = diver_framework.App()


@application.route('^/$', default=True)
def index(request, *args, **kwargs):

    page = ''

    page += '<table class="header" style="width: 98%; margin: 5px;">'

    page += '<tr>'
    page += '<td colspan="1">'

    page += '<h2>Share your dives!</h2><hr />'

    page += '<p>Upload a log from <a href="/subsurface">subsurface</a></p>%s</td>' % html.upload_form(
        'subsurface')

    page += '<td align="right" rowspan="2">%s<br />Photo by Carmelo Menza</td>' % html.random_image(
    )

    page += '</tr>'

    page += '<tr>'
    page += '<td>%s</td>' % html.related_dives(
        Dive.get_dives(), "Some divelogs")

    page += '</tr>'

    page += '</table>'

    return html.wrap(page)


@application.route('^/help$', cache_key=lambda *a, **k: '/help')
def showhelp(request, *args, **kwargs):

    page = ''

    page += '<table class="header" style="width: 98%; margin: 5px;">'

    page += '<tr>'
    page += '<td>'

    page += '<h2>Purpose</h2>'
    page += '<p>This website lets you upload and share your divelogs, and add' \
            + 'photos to them</p>'

    page += '<h2>How to use it?</h2>'
    page += '<p>For now, you will need your logs to be in the' \
            + ' <a href="http://subsurface.hohndel.org/">subsurface</a> format.' \
            + 'You need to write your log within subsurface, then export it and' \
            + ' then upload it here.</p>'
    page += '<p>Probably in the future, other formats will be supported.</p>'

    page += '<h2>About</h2>'
    page += '<p>This was written by Salvo \'LtWorf\' Tomaselli.</p>'
    page += '<p>Source code is available '\
        + '<a href="https://github.com/ltworf/DiveShare">here</a>.</p>'

    page += '</td>'

    page += '<td align="right">%s<br />Photo by Carmelo Menza</td>' % html.random_image(
    )

    page += '</tr>'

    page += '</table>'

    return html.wrap(page)


@application.route('^/subsurface$')
def upload(request, *args, **kwargs):

    page = ''

    if request.method == 'GET':

        page += html.upload_form('subsurface')

    elif request.method == 'POST':
        data = unicode(request.str_POST['log'].file.read(50000000), "utf-8")

        parsed_data = subsurface.parse(data.encode('utf-8'))

        dive = Dive()
        dive.cached_parsed = parsed_data
        dive.dive_data = data
        dive.dive_format = 'subsurface'
        dive.computer_id = parsed_data['computer_id']
        dive.title = parsed_data['title']
        dive.index = parsed_data.get('index', 0)
        dive.lat = float(parsed_data.get('position', (0, 0))[0])
        dive.lon = float(parsed_data.get('position', (0, 0))[1])
        dive.tags = str(parsed_data.get('raw_tags', []))
        key = dive.put()

        page = '<h2>Upload complete</h2>'

        page += '<p>'
        page += '<a href="../dive/%s">Your divelog</a>' % str(key.id())
        page += '<br>'
        page += '<a href="../delete_dive/%s">Delete divelog</a>' % str(
            dive.delete_link)

    return html.wrap(page)


def deferred_upload_photo(blobs, dive_id):
    dive = Dive.get_by_id(int(dive_id))
    for blob in blobs:
        img = blob.get_all()
        if img is None:
            raise Exception("Invalid blob")
        links = imgur.upload_image(img)
        dive.add_photo(links)
        blob.delete()
    dive.put()
    application.uncache('dive/%s' % dive_id)


@application.route("^/dive/(?P<dive_id>[0-9]+)/post_photo$")
def photo_uploader_post(request, *args, **kwargs):
    dive_id = kwargs["match"].group('dive_id')

    page = ''
    if request.method == 'POST':
        dive = Dive.get_by_id(int(dive_id))

        count = 0

        images = []

        for photo in request.str_POST.getall('photo'):
            blob = Blob()
            while True:
                chunk = photo.file.read(985145)
                if chunk == '':
                    break
                blob.append(chunk)
            images.append(blob)

            count += 1
        deferred.defer(deferred_upload_photo, images, dive_id)

        page += '<h2>Upload complete!</h2>'
        if count > 1:
            page += '<p>%d photos were uploaded</p>' % count
        else:
            page += '<p>1 photo was uploaded</p>'
        page += '<p>Photos will soon appear in your divelog, do not upload again.</p>'
        page += '<p><a href="/dive/%s">Return to your dive</a></p>' % dive_id

    return html.wrap(page)


@application.route("^/dive/(?P<dive_id>[0-9]+)/add_photo$",
                   cache_key=lambda *a, **k: '/add_photo')
def photo_uploader(request, *args, **kwargs):
    dive_id = kwargs["match"].group('dive_id')

    page = '<p>All data uploaded will be publicly available</p><form action="/dive/%s/post_photo" method="POST" enctype="multipart/form-data"><input type="file" name="photo" accept="*/*" multiple><input type="submit"></form><p>Do not reload the page, it will take a while.</p>' % dive_id

    return html.wrap(page)


@application.route("^/dive/(?P<dive_id>[0-9]+)$",
                   cache_key=lambda *a, **k: 'dive/' +
                   k["match"].group('dive_id')
                   )
def echo(request, *args, **kwargs):
    dive_id = kwargs["match"].group('dive_id')

    dive = Dive.get_by_id(int(dive_id))

    if not dive:
        return html.wrap("<h1>Sorry, we couldn't find the page you were looking for</h1>" + dive_id)

    data = dive.get_html_elements()

    title = data['title']

    result = html.wrap(
        html.make_table(data) + html.share(
            'http://dive-share.appspot.com/dive/%s' % dive_id),
        title)

    return result


@application.route('^/delete_dive/(?P<del_key>[0-9a-f]+)$')
def delete(request, *args, **kwargs):
    del_key = kwargs["match"].group('del_key')

    result = Dive.delete(del_key)

    if result:
        return html.wrap('Dive deleted')
    else:
        return html.wrap('Error. Invalid link')


@application.route("^/dive/(?P<dive_id>[0-9]+)/assign_confirm$",
                   cache_key=lambda *a, **k: 'assign_confirm/' +
                   k["match"].group('dive_id'))
def assign(request, *args, **kwargs):
    dive_id = kwargs["match"].group('dive_id')

    page = '<h2>Did you do this dive?</h2>'
    page += '<p>'
    page += 'If you proceed, this divelog will be associated with your google account'
    page += ' and this dive will be added to your own dives.'
    page += '</p>'

    page += '<p>'
    page += '<a href="/dive/%s/assign">Yes, this is my divelog</a>' % dive_id
    page += ' '
    page += '<a href="/dive/%s">No, this is not my divelog</a>' % dive_id
    page += '</p>'

    return html.wrap(page)


@application.route("^/dive/(?P<dive_id>[0-9]+)/assign$")
def assign(request, *args, **kwargs):
    dive_id = kwargs["match"].group('dive_id')
    user = users.get_current_user()
    page = ''

    if user:
        dive = Dive.get_by_id(int(dive_id))
        if dive.userid is not None:
            raise Exception('Dive already assigned %s' % dive_id)
        dive.userid = user.user_id()
        dive.put()
        application.uncache('dive/%s' % dive_id)

        page += '<p>This dive was assigned to you.</p>'

        page += '<script type="text/JavaScript">' \
                + ('setTimeout("location.href = \'/dive/%s\';", 1000);' % dive_id) \
                + '</script>'

    else:
        login_uri = users.create_login_url('/dive/%s/assign' % dive_id)

        page += '<script type="text/JavaScript">' \
                + ('setTimeout("location.href = \'%s\';", 1000);' % login_uri) \
                + '</script>'
        page += '<p>'
        page += 'You will be redirected to the '
        page += '<a href="%s">login page</a>' % login_uri
        page += '.'
        page += '</p>'

    return html.wrap(page)


@application.route("^/my$")
def my(request, *args, **kwargs):
    user = users.get_current_user()
    page = ''

    if user:
        page += '<h2>Your dives</h2>'

        page += '<table class="mydives">'

        page += '<thead class="mydives">'

        page += '<tr>'
        page += '<td>#</td>'
        page += '<td>Dive</td>'
        page += '<td>Delete dive</td>'
        page += '</tr>'

        page += '</thead>'

        page += '<tbody>'

        for i, d in enumerate(Dive.get_same_user(user.user_id())):
            page += '<tr class="%s">' % ('dark_row' if i % 2 else 'light_row')

            page += '<td>'
            page += '%d' % d.index
            page += '</td>'

            page += '<td>'
            page += '<a href="/dive/%d">%s</a>' % (d.key.id(), d.title)
            page += '</td>'

            page += '<td>'
            page += '<a href="/delete_dive/%s">Delete this dive</a>' % d.delete_link
            page += '</td>'

            page += '</tr>'

        page += '</thead>'

        page += '</table>'

    else:
        login_uri = users.create_login_url('/my')

        page += '<script type="text/JavaScript">' \
                + ('setTimeout("location.href = \'%s\';", 1000);' % login_uri) \
                + '</script>'
        page += '<p>'
        page += 'You will be redirected to the '
        page += '<a href="%s">login page</a>' % login_uri
        page += '.'
        page += '</p>'

    return html.wrap(page)
