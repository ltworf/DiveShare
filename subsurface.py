# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ElementTree
import re

from parser import *
from datatypes import *
from dive_profile import draw_profile


def getText(element):
    try:
        return element.text
    except:
        return None


def getFirst(element, tag, allowNone=False):
    """
    returns the first element found with the
    given tag
    """
    for i in element.getchildren():
        if i.tag == tag:
            return i

    if allowNone:
        return None
    raise ParseError("Node %s not found" % tag)


def parse(data):
    """
    Parses XML data in the subsurface format
    and returns a dictionary with various
    HTML elements, to be placed around.
    """

    e = ElementTree.XML(data)

    if e.tag != "divelog" or e.attrib.get('program') != 'subsurface':
        raise ParseError("Not a subsurface divelog")

    dives = getFirst(e, "dives")
    divelist = dives.getchildren()

    return _parseDive(divelist[0])

    # FIXME
    # return "".join(map(_parseDive, divelist))


def _parseDive(data):

    if data.tag != "dive":
        raise ParseError("dive expected")

    result = {}
    result['title'] = "Divelog"

    if 'rating' in data.attrib:
        r = Rating('rating', data.attrib['rating'])
        result['rating'] = r.toHTML()

    if 'visibility' in data.attrib:
        r = Rating('visibility', data.attrib['visibility'])
        result['visibility'] = r.toHTML()

    if 'number' in data.attrib:
        count = DiveCount(data.attrib['number'])
        result['index'] = int(data.attrib['number'])
        result['number'] = count.toHTML()

    if 'date' in data.attrib:
        d = Date(data.attrib['date'], data.attrib.get('time'))
        result['date'] = d.toHTML()

    if 'duration' in data.attrib:
        d = GenericField('Duration', data.attrib['duration'])
        result['duration'] = d.toHTML()

    if 'tags' in data.attrib:
        raw_tags = data.attrib['tags'].split(',')
        result['raw_tags'] = raw_tags
        d = Tags(map(lambda x: x.strip(), raw_tags))
        result['tags'] = d.toHTML()

    try:
        location = getFirst(data, "location")
        if 'gps' in location.attrib:
            lat, lon = location.attrib["gps"].split()
        else:
            lat, lon = (None, None)
        name = location.text
        result['position'] = (lat, lon)
        result['location_name'] = name
        result['title'] = "Dive in %s" % name
        result['location'] = Location(lat, lon, name).toHTML()
    except:
        pass

    result['cylinder'] = _parse_cylinder(data)
    result['weightsystem'] = _parse_weightsystem(data)

    result['suit'] = GenericField(
        'Suit',
        getText(getFirst(data, 'suit', True))
    ).toHTML()

    result['buddy'] = GenericField(
        'Buddy',
        getText(getFirst(data, 'buddy', True))
    ).toHTML()

    notes = getText(getFirst(data, 'notes', True))
    if notes:
        notes = notes.replace('\n', '<br>')
    result['notes'] = Notes(notes).toHTML()

    result['divemaster'] = GenericField(
        'Divemaster',
        getText(getFirst(data, 'divemaster', True))
    ).toHTML()

    result['profile'] = draw_profile(_get_samples(data), 600, 400)

    result['computer_id'] = _get_divecomputer_id(data)

    return result


def _get_divecomputer_id(data):
    computer = getFirst(data, "divecomputer", True)

    if computer is None:
        return ''

    return computer.attrib.get('model', 'Unknown') + computer.attrib.get('deviceid', 'Unknown')


def _parse_weightsystem(data):
    values = []

    for i in data.getchildren():
        if i.tag != 'weightsystem':
            continue

        weight = i.attrib.get('weight')
        description = i.attrib.get('description')

        weightsystem = Weightsystem(weight, description)
        values.append(weightsystem.toHTML())
    return '<div class="weightsystem"><span class="weightsystem_title">Weighting system</span><br>%s</div>' % '<hr>'.join(values)


def _parse_cylinder(data):

    values = []

    for i in data.getchildren():
        if i.tag != 'cylinder':
            continue

        size = i.attrib.get('size')
        workpressure = i.attrib.get('workpressure')
        description = i.attrib.get('description')
        start = i.attrib.get('start')
        end = i.attrib.get('end')

        cylinder = Cylinder(size, workpressure, description, start, end)
        values.append(cylinder.toHTML())

    return '<div class="cylinder"><span class="cylinder_title">Gas</span><br>%s</div>' % '<hr>'.join(values)


def _get_samples(data):
    computer = getFirst(data, "divecomputer", True)

    if computer is None:
        return []

    samples = []

    for i in computer.getchildren():
        if i.tag != 'sample':
            continue

        sample = {}

        time = re.match(
            r'([0-9]{1,2}):([0-9]{2}) min', i.attrib['time']).groups()

        sample['time'] = (int(time[0]) * 60) + int(time[1])

        depth = float(re.match(r'([0-9\.]+) m', i.attrib['depth']).groups()[0])

        sample['depth'] = depth

        if 'temp' in i.attrib:
            temp = float(
                re.match(r'([0-9\.]+) C', i.attrib['temp']).groups()[0])

            sample['temp'] = temp

        samples.append(sample)
    samples.sort(key=lambda x: x['time'])
    return samples
