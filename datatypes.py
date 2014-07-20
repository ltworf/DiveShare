# -*- coding: utf-8 -*-


class Location(object):

    def __init__(self, lat, lon, name):
        if lat is not None or lon is not None:
            self.lat = float(lat)
            self.lon = float(lon)
        else:
            self.lat = self.lon = None
        self.name = name

    def toHTML(self):
        if self.lat is not None:
            return '<span class="location"><a href="http://www.openstreetmap.org/?lat=%f&lon=%f&zoom=17&layers=M">%s</a></span>' % (self.lat, self.lon, self.name)
        else:
            return '<span class="location">%s</span>' % self.name


class DiveCount(object):

    def __init__(self, count):
        self.count = int(count)

    def toHTML(self):
        return '<span class="dive_count"># %s</span>' % self.count


class Date(object):

    def __init__(self, date, time=None):
        year, month, day = date.split('-')

        self.year = int(year)
        self.month = int(month)
        self.day = int(day)

        if time is None:
            self.hours = None
            self.minutes = None
            self.seconds = None
        else:
            values = time.split(':')

            self.hours = int(values[0])
            self.minutes = int(values[1])
            if len(values) == 3:
                self.seconds = int(values[2])
            else:
                self.seconds = 0

    def toHTML(self):

        r = '<span class="date">%d-%02d-%02d</span>' % (
            self.year, self.month, self.day)

        if self.hours is not None:
            r += ' <span class="time">%02d:%02d:%02d</span>' % (
                self.hours, self.minutes, self.seconds)

        return '<span class="date_time">%s</span>' % r


class Tags(object):

    def __init__(self, tags):
        self.tags = tags

    def toHTML(self):
        r = '<span class="tags_span">Tags: '

        count = 0
        for i in self.tags:
            r += '<span class="tag_span tag_span_%d">%s</span>&nbsp;' % (
                count % 3, i)
            count += 1

        r += '</span>'

        return r


class Weightsystem(object):

    def __init__(self, weight, description):
        self.weight = weight
        self.description = description

    def toHTML(self):
        r = '<span class="weightsystem %s">' % self.description
        r += '%s: %s' % (self.description, self.weight)
        r += '</span>'

        return r


class Cylinder(object):

    def __init__(self, size, workpressure, description, start, end):
        self.size = size
        self.workpressure = workpressure
        self.description = description
        self.start = start
        self.end = end

    def toHTML(self):
        r = '<span class="cylinder">Start: %s<br>End: %s</span><br>' % (
            self.start, self.end)

        # TODO something nice to show the rest of the info on click
        return r


class GenericField(object):

    '''
    Generic name=value datatype
    '''

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def toHTML(self):

        if self.value is None:
            return ''

        r = ''
        r += '<span class="%s_span">' % self.name
        r += '%s: %s' % (self.name, self.value)
        r += '</span>'
        return r


class Notes(object):

    def __init__(self, notes):
        self.notes = notes

    def toHTML(self):
        r = '<span class="notes_span">' + self.notes + '</span>'
        return r


class Rating(object):

    def __init__(self, rating, value):
        self.value = int(value)
        self.rating = rating

    def toHTML(self):

        r = u""
        for i in xrange(self.value):
            r += u"★"

        return '<span class="%s_span"><span class="rating_name">%s</span>&nbsp;<span class="rating">%s</span></span>' % (self.rating, self.rating, r)
