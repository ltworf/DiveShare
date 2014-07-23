import webapp2
import micro_webapp2
application = micro_webapp2.WSGIApplication()


import html
import subsurface
from model import Dive


@application.route('/')
def m(request, *args, **kwargs):

    page = '<h2>Share your dives!</h2>'

    page += '<p>Upload a log from <a href="/subsurface">subsurface</a></p>'

    return html.wrap(page)


@application.route('/subsurface')
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
        key = dive.put()

        page = '<h2>Upload complete</h2>'

        page += '<p>'
        page += '<a href="../dive/%s">Your divelog</a>' % str(key.id())
        page += '<br>'
        page += '<a href="../delete_dive/%s">Delete divelog</a>' % str(
            dive.delete_link)

    return html.wrap(page)


@application.route("/dive/<id>")
def echo(request, *args, **kwargs):

    # Can use cache
    cached = micro_webapp2.use_cache(request, 'dive/' + kwargs['id'])
    if cached:
        return cached

    dive = Dive.get_by_id(int(kwargs["id"]))

    if not dive:
        return html.wrap("<h1>Sorry, we couldn't find the page you were looking for</h1>" + kwargs['id'])

    if dive.dive_format == 'subsurface':
        data = subsurface.parse(dive.dive_data.encode('utf-8'))

    if 'location_name' in data:
        title = "Dive in %s" % data['location_name']
    else:
        title = "Divelog"

    result = html.wrap(
        html.make_table(data) + html.share(
            'http://dive-share.appspot.com/dive/%s' % kwargs['id']),
        title)

    micro_webapp2.cache('dive/' + kwargs['id'], result)
    return result


@application.route('delete_dive/<id>')
def delete(request, *args, **kwargs):
    dive_id = kwargs['id']

    return html.wrap('Not implemented yet')

    # TODO delete it
