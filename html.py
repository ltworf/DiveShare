# -*- coding: utf-8 -*-

def wrap(code):
    '''
    Wraps some HTML code with some stuff
    '''

    r = u''

    r+= '<HTML><HEAD><meta charset="UTF-8"><LINK href="stylesheets/base.css" rel="stylesheet" type="text/css">'
    r+='<title>DiveShare</title>'
    r+= '<meta property="og:site_name" content="DiveShare"/>'

    r+='</HEAD><BODY>'

    r+= '<div class="header">'
    r+= '<table class="header"><tr>'
    r+= '<td width="100px">'

    #Flag
    r+= '<svg width="90" height="90">'
    r+= '    <rect width="90" height="90" fill="#FFFFFF"/>'
    r+= '    <rect x="1" y="1" width="88" height="88" fill="#FF0000"/>'
    r+= '<line x1="0" y1="0" x2="90" y2="90" style="stroke:white;stroke-width:20" />'
    r+= '</svg> &nbsp;'


    r+= '</td><td class="header">'
    r+= '<span class="header_title"><a class ="header_title" href="http://dive-share.appspot.com/">DiveShare</a></span>'

    r+= '</td><td class="header_link">'
    r+= '<a alt="about" class="header_link" href="">?</a>'
    r+= '</td></tr></table>'
    r+= '</div>'

    r+=code

    r+='</body></html>'
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
    r += '<td colspan="1">%s</td>' % data.get('notes', '')
    r += '</tr>'

    r += '<tr>'
    r += '<td colspan="3" align="right">%s</td>' % data.get('tags', '')
    r += '</tr>'

    r += '</table>'
    return r
