# -*- coding: utf-8 -*-


def velocity(speed):
    '''
    Speed is in mm/s

    This code is copied from subsurface
    '''
    STABLE = '#008000'
    SLOW = '#789300'
    MODERATE = '#C2A200'
    FAST = '#FF8000'
    CRAZY = '#FF0000'

    if (speed < -304):
        return CRAZY
    elif (speed < -152):
        return FAST
    elif (speed < -76):
        return MODERATE
    elif (speed < -25):
        return SLOW
    elif (speed < 25):
        return STABLE
    elif (speed < 152):
        return SLOW
    elif (speed < 304):
        return MODERATE
    elif (speed < 507):
        return FAST

    # more than that is just crazy - you'll blow your ears out
    return CRAZY


def draw_profile(samples, width, height):
    samples.insert(0, [0, 0, 0, 0])

    r = '<svg width="%d" height="%d" class="dive_profile">' % (width, height)

    top = (44, 18)
    bottom = (width - 30, height - 44)
    size = (bottom[0] - top[0], bottom[1] - top[1])

    r += '<rect x="%d" y="%d" width="%d" height="%d" style="fill:#F3F3E6;stroke-width:1;stroke:#FFFFFF" />' % (
        top[0],
        top[1],
        size[0],
        size[1]
    )

    max_time = float(((samples[-1][0] / 600) + 1) * 600)
    max_depth = float(((max((i[1] for i in samples)) / 10000) + 1) * 10000)

    # Horizontal lines
    for i in xrange(0, int(max_depth), 5000):
        x1 = 0 + top[0]
        x2 = size[0] + top[0]

        y2 = y1 = ((i * size[1]) / max_depth) + top[1]

        r += '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:#FFFFFF;stroke-width:2" />' % (
            x1, y1, x2, y2)

        r += '<text x="%f" y="%f" fill="blue">%dm</text>' % (
            x1 - 30,
            y1 + 5,
            i / 1000
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
    avg_depth = 0
    for i in xrange(len(samples) - 1):
        avg_depth += samples[i][1]

        x1 = ((samples[i][0] * size[0]) / max_time) + top[0]
        x2 = ((samples[i + 1][0] * size[0]) / max_time) + top[0]

        y1 = ((samples[i][1] * size[1]) / max_depth) + top[1]
        y2 = ((samples[i + 1][1] * size[1]) / max_depth) + top[1]

        try:
            speed = (float(samples[i][1] - samples[i + 1][1]) / (
                float(samples[i][0] - samples[i + 1][0])))
        except ZeroDivisionError:
            speed = 0

        r += '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:%s;stroke-width:2" />' % (
            x1, y1, x2, y2, velocity(speed))

    # Draw average line
    avg_depth /= float(len(samples))
    x1 = top[0]
    x2 = size[0] + top[0]
    y1 = y2 = ((avg_depth * size[1]) / max_depth) + top[1]

    r += '<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(100,100,100);stroke-width:1" />' % (
        x1, y1, x2, y2)
    r += u'<text x="%f" y="%f" fill="rgb(100,100,100)">%.2fm</text>' % (
        x1 + 2,
            y1 - 4,
            avg_depth / 1000.0
    )

    # Mark temperatures
    temp_count = 0
    for i in samples:
        temp_count -= 1
        if i[3] == 0 or temp_count > 0:
            continue

        x = ((i[0] * size[0]) / max_time) + top[0] - 15
        y = bottom[1] - 50

        r += u'<text x="%f" y="%f" fill="red">%d°C</text>' % (
            x,
            y,
            i[3] / 1000.0 - 273.15
        )
        temp_count = 30

    r += '</svg>'
    return r
