# -*- coding: utf-8 -*-

import urllib


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
    r += '<td colspan="1">%s<br>%s</td>' % (
        data.get('notes', ''), data.get('related'))
    r += '</tr>'

    r += '<tr>'
    r += '<td colspan="3" align="right">%s</td>' % data.get('tags', '')
    r += '</tr>'

    r += '</table>'
    return r
