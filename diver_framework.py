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

            kwargs['match'] = result
            r = None

            # TODO implement E-Tag
            key = value.get('cache_key', lambda *x, **y: None)(*args, **kwargs)

            # Try to get page from cache
            if key:
                cached = memcache.get(key)
                if cached:
                    r = cached

            # Generate the page if that failed
            if r is None:
                kwargs = _add_dicts(dict(kwargs), args[0])
                request = Request(args[0])
                r = value['endpoint'](request, *args, **kwargs)

                if key:
                    memcache.add(key, r)

            # Generate Response object
            # if isinstance(r, basestring):
                # r = Response(r)
            # elif isinstance(r, tuple):
                # r = Response(*r)

            # Add additional headers
            # map(r.headerlist.append, value['static_headers'])

            # r.wsgi_write(lambda *a,**b:None)
            # return
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

    def route(self, regexp, default=False, cache_key=None, static_headers=[]):
        '''
        Defines the function as an endpoint

        regexp: Python regular expression used to match the URL
                with the function.
                The function is then called with match=<Match_Object>

        default: Sets the function as the default endpoint, to
                use when no regexp matches.

        static_headers: List of tuples, containing any extra headers
                to add to the response

        '''
        def wrapper(func):
            d = {
                'endpoint': func,
            }

            if cache_key:
                d['cache_key'] = cache_key
            d['static_headers'] = static_headers

            if default:
                self.routes[None] = d
            else:
                self.routes[regexp] = d

            return func
        return wrapper
