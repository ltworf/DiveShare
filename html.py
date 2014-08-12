# -*- coding: utf-8 -*-

import urllib
import random


def photo(pics, dive):
    '''
    Creates a div with photos in it

    pics is an iterable of Photo
    '''
    r = '<div class="photo_list">'

    for i in pics:
        r += '<a href="%s" target="_blank">' % i.link

        r += '<img src="%s" />' % i.small_thumb

        r += '</a>'

    r += '<a href="%s/add_photo"><img alt="add photos" src="/stylesheets/add_photos.png"/></a>' % dive

    r += '</div>'

    return r


def wrap(code, title=None):
    '''
    Wraps some HTML code with some stuff
    '''

    r = u''

    r += '<!DOCTYPE html>'
    r += '<html><head>'

    r += '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'

    r += '<link href="//dive-share.appspot.com/stylesheets/base.css" rel="stylesheet" type="text/css">'
    if title:
        r += '<title>%s</title>' % title
        r += '<meta property="og:title" content="%s"/>' % title

    else:
        r += '<title>DiveShare</title>'

    r += '<meta property="og:site_name" content="DiveShare"/>'
    # r += '<meta property="og:picture"
    # content="http://dive-share.appspot.com/stylesheets/flag.png" />'

    r += '</head><body>'

    r += '<div class="header">'
    r += '<table class="header"><tr>'
    r += '<td width="100px">'

    # Flag
    # r += '<svg width="90" height="90">'
    # r += '    <rect width="90" height="90" fill="#FFFFFF"/>'
    # r += '    <rect x="1" y="1" width="88" height="88" fill="#FF0000"/>'
    # r += '<line x1="0" y1="0" x2="90" y2="90" style="stroke:white;stroke-width:20" />'
    # r += '</svg> &nbsp;'

    r += '<img alt="Diver flag" src="http://dive-share.appspot.com/stylesheets/flag.png" />'

    r += '</td><td class="header">'
    r += '<span class="header_title"><a class ="header_title" href="http://dive-share.appspot.com/">DiveShare</a></span>'

    r += '</td><td class="header_link">'
    r += '<a class="header_link" href=""></a>'
    r += '</td></tr></table>'
    r += '</div>'

    r += code

    r += '</body></html>'
    return r.encode('utf-8')


def share(url):

    url = urllib.quote(url)

    r = '<p>'

    r += '<a name="fb_share" href="http://www.facebook.com/sharer.php?u=%s" target="_blank" class="joinFB"><img  alt="Share on Facebook" src="/stylesheets/fb_share.png"/></a> ' % url

    r += '<script type="text/javascript" src="https://apis.google.com/js/plusone.js"></script><g:plusone></g:plusone> '

    r += '<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="https://platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script> '

    r += '</p>'
    return r


def make_table(data):
    '''
    Creates an HTML table containing the nicely
    impaginated divelog
    '''

    r = '<table class="divelog">'
    r += '<tr>'
    r += '<td>%s</td>' % data.get('number', '')
    r += '<td>%s</td>' % (
        data.get('rating', '') + '<br>' + data.get('visibility', ''))
    r += '<td align="right">%s</td>' % data.get('date', '')
    r += '</tr>'

    r += '<tr>'
    r += '<td colspan="2">%s</td>' % data.get('location', '')
    r += '<td align="right">%s</td>' % data.get('duration', '')
    r += '</tr>'

    r += '<tr>'
    r += '<td>%s</td>' % data.get('cylinder', '')
    r += '<td align="center">%s</td>' % data.get('suit', '')
    r += '<td align="right">%s</td>' % data.get('weightsystem', '')
    r += '</tr>'

    r += '<tr>'
    r += '<td colspan="2">%s</td>' % data.get('buddy', '')
    r += '<td>%s</td>' % data.get('divemaster', '')
    r += '</tr>'

    r += '<tr>'
    r += '<td colspan="2">%s</td>' % data.get('profile', '')
    r += '<td colspan="1">%s<br>%s<br>%s</td>' % (
        data.get('notes', ''), data.get('photo', ''), data.get('related', ''))
    r += '</tr>'

    r += '<tr>'
    r += '<td colspan="3" align="right">%s</td>' % data.get('tags', '')
    r += '</tr>'

    r += '</table>'
    return r


def upload_form(kind):
    d = {'subsurface': '<p>All data uploaded will be publicly available</p><form action="/subsurface" method="POST" enctype="multipart/form-data"><input type="file" name="log" accept="*/*"><input type="submit"></form>'
             }

    return d[kind]


def related_dives(iterator, title):
    '''
    Returns a div with nicely formatted
    dives.

    The iterator yields Dive objects
    '''

    related_div = '<div class="related_dives"><span class="related_dives">%s</span>' % title

    related_div += '<ul>'

    for d in iterator:
        related_div += '<li><a href="/dive/%s">#%d - %s</a></li>' % (
            str(d.key.id()), d.index, d.title)

    related_div += '</ul>'

    related_div += '</div>'

    return related_div


def random_image():
    img = (
        '005be695838257f20ba88722b8163d9a.jpg',
        '03656c08a9de88ec18c6f78311354c13.jpg',
        '0e2fec28393516736e0f32ca8a9cd384.jpg',
        '1c4dc2949f4ae9dbd86328660a6556ed.jpg',
        '2f8327539d711d1cd5de52a8cd5f0406.jpg',
        '31203c1790d06c667c5eec8d27490dc1.jpg',
        '3b77316c866fd2e6a2342d7c15e5a610.jpg',
        '42c9bfb961304ef1a2770a0782a202f2.jpg',
        '4a08b92873a59c9e70e790f72c31dfe2.jpg',
        '4b987571cfd4c48c7909a6ac4289d36b.jpg',
        '4e8c8392a719296b2de41bf4b5015f51.jpg',
        '50c47d6fbe95e3b7df26717997b010d6.jpg',
        '588cd868a9e52e7f268f20fa31117f72.jpg',
        '633ad17d252d50555b2b7cd4122a72c0.jpg',
        '711142bc130871581b160253735c567e.jpg',
        '7214c9cd301ece357768a82f2de16d06.jpg',
        '7788f6f2250d1d366e9882f819cc3a67.jpg',
        '977e85d6abed3c4c9d7f50b979e619cc.jpg',
        '9fca1256914237e7873f4d9d982bf242.jpg',
        'a16595b209d597de92f08873cf927674.jpg',
        'a2293780348646498d97ddf9d94cc592.jpg',
        'c0a8d1af7c8fa6fc2a8be3d018258213.jpg',
        'dfe85406d910e8fe9d5960e2cfa3f2c1.jpg'
    )

    img_name = random.choice(img)

    return '<img class="photo" alt="underwater picture" src="/pics/%s" />' % img_name
