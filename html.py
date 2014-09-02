# -*- coding: utf-8 -*-

import urllib
import random


def random_image():
    '''
    Returns a random photo from the ones in /pics
    '''
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

    return random.choice(img)
