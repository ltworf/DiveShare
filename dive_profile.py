# -*- coding: utf-8 -*-


def draw_profile(samples, width, height):
    initial = {'time': 0, 'depth': 0}
    samples.insert(0, initial)

    r = '<svg width="%d" height="%d">' % (width, height)

    top = (44, 18)
    bottom = (width - 30, height - 44)
    size = (bottom[0] - top[0], bottom[1] - top[1])

    r += '<rect rect x="%d" y="%d" width="%d" height="%d" style="fill:#F3F3E6;stroke-width:1;stroke:#FFFFFF" />' % (
        top[0],
        top[1],
        size[0],
        size[1]
    )

    max_time = float(((max((i['time'] for i in samples)) / 600) + 1) * 600)
    max_depth = float(((max((i['depth'] for i in samples)) / 10) + 1) * 10)

    # Horizontal lines
    for i in xrange(0, int(max_depth), 10):
        x1 = 0 + top[0]
        x2 = size[0] + top[0]

        y2 = y1 = ((i * size[1]) / max_depth) + top[1]

        r += '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:#FFFFFF;stroke-width:2" />' % (
            x1, y1, x2, y2)

        r += '<text x="%f" y="%f" fill="blue">%dm</text>' % (
            x1 - 30,
            y1 + 5,
            i
        )

    # Vertical lines
    for i in xrange(0, int(max_time), 600):
        x1 = x2 = ((i * size[0]) / max_time) + top[0]
        y1 = 0 + top[1]
        y2 = size[1] + top[1]

        r += '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:#FFFFFF;stroke-width:2" />' % (
            x1, y1, x2, y2)

        r += '<text x="%f" y="%f" fill="black">%dmin</text>' % (
            x1 - 5,
            y2 + 15,
            i / 60
        )

    # Depth profile
    for i in xrange(len(samples) - 1):
        x1 = ((samples[i]['time'] * size[0]) / max_time) + top[0]
        x2 = ((samples[i + 1]['time'] * size[0]) / max_time) + top[0]

        y1 = ((samples[i]['depth'] * size[1]) / max_depth) + top[1]
        y2 = ((samples[i + 1]['depth'] * size[1]) / max_depth) + top[1]

        r += '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(255,0,0);stroke-width:2" />' % (
            x1, y1, x2, y2)

    # Mark temperatures
    temp_count = 0
    for i in samples:
        temp_count -= 1
        if 'temp' not in i or temp_count > 0:
            continue

        x = ((i['time'] * size[0]) / max_time) + top[0] - 15
        y = bottom[1] - 50

        r += u'<text x="%f" y="%f" fill="red">%d°C</text>' % (
            x,
            y,
            i['temp']
        )
        temp_count = 30

    r += '</svg>'
    return r
