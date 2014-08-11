import diver_framework
import html
import subsurface
from model import Dive


application = diver_framework.App()


@application.route('^/$', default=True)
def m(request, *args, **kwargs):

    page = '<h2>Share your dives!</h2>'

    page += '<p>Upload a log from <a href="/subsurface">subsurface</a></p>'

    return html.wrap(page)


@application.route('^/subsurface$')
def upload(request, *args, **kwargs):

    page = ''

    if request.method == 'GET':

        page += '<p>All data uploaded will be publicly available</p>'

        page += '<form action="/subsurface" method="POST" enctype="multipart/form-data">'
        page += '<input type="file" name="log" accept="*/*">'
        page += '<input type="submit">'
        page += '</form>'

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

    related_div = '<div class="related_dives"><span class="related_dives">Related dives</span>'
    for d in dive.get_related():
        related_div += '<br /><a href="%s">#%d - %s</a>' % (
            str(d.key.id()), d.index, d.title)

    related_div += '</div>'
    data['related'] = related_div

    title = data['title']

    result = html.wrap(
        html.make_table(data) + html.share(
            'http://dive-share.appspot.com/dive/%s' % dive_id),
        title)

    return result


@application.route('^/delete_dive/(?P<dive_id>[0-9a-f]+)$')
def delete(request, *args, **kwargs):
    dive_id = kwargs["match"].group('dive_id')

    return html.wrap('Not implemented yet')

    # TODO delete it
