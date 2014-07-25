import re

from google.appengine.ext.webapp import Request, Response
from google.appengine.api import memcache


def _add_dicts(a, b):
    '''
    'Sums' two dictionaries
    '''
    r = {}

    for k, v in a.iteritems():
        r[k] = v
    for k, v in b.iteritems():
        r[k] = v
    return r


class App(object):

    def __init__(self):
        self.routes = {}
        self.default_route = None

    def __call__(self, *args, **kwargs):

        def call_endpoint(result, value, args, kwargs):
            # TODO implement E-Tag

            key = value.get('cache_key', lambda *x, **y: None)(*args, **kwargs)

            if key:
                cached = memcache.get(key)
                if cached:
                    cached

            kwargs['match'] = result
            kwargs = _add_dicts(dict(kwargs), args[0])
            request = Request(args[0])
            r = value['endpoint'](request, *args, **kwargs)

            if key:
                memcache.add(key, r)

            return r

        default = None

        for regexp, value in self.routes.iteritems():

            if regexp is None:
                default = value
                continue

            result = re.match(regexp, args[0].get('PATH_INFO', ''))
            if result:
                return call_endpoint(result, value, args, kwargs)

        if default:
            return call_endpoint(None, default, args, kwargs)
        return "NO ROUTE"

    def route(self, regexp, default=False, cache_key=None):
        '''
        Defines the function as an endpoint

        regexp: Python regular expression used to match the URL
                with the function.
                The function is then called with match=<Match_Object>

        default: Sets the function as the default endpoint, to
                use when no regexp matches.

        '''
        def wrapper(func):
            d = {
                'endpoint': func,
            }

            if cache_key:
                d['cache_key'] = cache_key

            if default:
                self.routes[None] = d
            else:
                self.routes[regexp] = d

            return func
        return wrapper
