from google.appengine.ext import deferred

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


@application.route('^/subsurface$')
def upload(request, *args, **kwargs):

    page = ''

    if request.method == 'GET':

        page += html.upload_form('subsurface')

    elif request.method == 'POST':
        data = unicode(request.str_POST['log'].file.read(50000000), "utf-8")

        parsed_data = subsurface.parse(data.encode('utf-8'))

        dive = Dive()
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


@application.route("^/dive/(?P<dive_id>[0-9]+)/add_photo$")
def photo_uploader(request, *args, **kwargs):
    dive_id = kwargs["match"].group('dive_id')

    page = ''

    if request.method == 'GET':

        page += '<p>All data uploaded will be publicly available</p><form action="/dive/%s/add_photo" method="POST" enctype="multipart/form-data"><input type="file" name="photo" accept="*/*" multiple><input type="submit"></form><p>Do not reload the page, it will take a while.</p>' % dive_id

    elif request.method == 'POST':
        dive = Dive.get_by_id(int(dive_id))

        count = 0

        images = []

        for photo in request.str_POST.getall('photo'):
            blob = Blob()
            while True:
                chunk = photo.file.read(985145)
                if chunk == '': break
                blob.append(chunk)
            images.append(blob)

            count += 1
        deferred.defer(deferred_upload_photo,images,dive_id)


        page += '<h2>Upload complete!</h2>'
        if count > 1:
            page += '<p>%d photos were uploaded</p>' % count
        else:
            page += '<p>1 photo was uploaded</p>'
        page += '<p>Photos will soon appear in your divelog, do not upload again.</p>'
        page += '<p><a href="/dive/%s">Return to your dive</a></p>' % dive_id

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

    if dive.dive_format == 'subsurface':
        data = subsurface.parse(dive.dive_data.encode('utf-8'))
    else:
        return "Uh? Corrupt data in the database. Please report this"

    data['related'] = html.related_dives(dive.get_related(), "Related dives")

    data['photo'] = html.photo(dive.photos, dive_id)

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
