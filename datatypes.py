# -*- coding: utf-8 -*-

class Location(object):
    def __init__(self, lat, lon, name):
        self.lat = float(lat)
        self.lon = float(lon)
        self.name = name

    def toHTML(self):
        return '<div class="location"><a href="http://www.openstreetmap.org/?lat=%f&lon=%f&zoom=17&layers=M">asd</a><br><span class="location_name">%s</span></div>' % (self.lat, self.lon, self.name)


class Rating(object):
    def __init__(self, rating, value):
        self.value = int(value)
        self.rating = rating

    def toHTML(self):

        r=u""
        for i in xrange(self.value):
            r+= u"★"

        return '<span class="rating_name>%s></span><span class="rating">%s</span>' % (self.rating,r)
