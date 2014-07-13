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
            return '<div id="location"><a href="http://www.openstreetmap.org/?lat=%f&lon=%f&zoom=17&layers=M">%s</a></div>' % (self.lat, self.lon, self.name)
        else:
            return '<div id="location">%s</div>' % self.name

class DiveCount(object):
    def __init__(self, count):
        self.count = int(count)

    def toHTML(self):
        return '<span id="dive_count"># %s</span>' % self.count

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
            if len(values)==3:
                self.seconds= int(values[2])
            else:
                self.seconds = 0


    def toHTML(self):

        r = '<span id="date">%d-%02d-%02d</span>' % (self.year, self.month, self.day)

        if self.hours is not None:
            r += ' <span id="time">%02d:%02d:%02d</span>' % (self.hours, self.minutes, self.seconds)

        return '<div id="date_time">%s</div>' % r


class Rating(object):
    def __init__(self, rating, value):
        self.value = int(value)
        self.rating = rating

    def toHTML(self):

        r=u""
        for i in xrange(self.value):
            r+= u"★"

        return '<span class="rating_name">%s</span><span class="rating">%s</span>' % (self.rating,r)
