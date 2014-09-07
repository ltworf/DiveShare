from google.appengine.api import memcache


def get(key, value_function=None, time=0, auto=True):
    '''
    Gets a value from memcache.

    This function is a wrapper and is used to avoid
    the ugliness of having

    c = memcache.get(key)
    if c is not None:
        return c
    content = generate_dynamic_content()
    memcache.add(key, content)

    This function is used in the following way:

    def generator():
        return 'dynamically generated content'
    return memcache.get(key, generator)

    Simplyifying the code.

    key: well, it's self explainatory
    value_function: callable
        It must return a string that get()
        will return if the item is not
        present in cache.

        If auto is true, this string will
        be added to the cache automatically.
    '''
    r = memcache.get(key)
    if r is None:

        if value_function is None:
            return None
        else:
            output = value_function()
            if auto:
                set(key, output, time=time)
            return output
    return r

add = memcache.add
set = memcache.set
delete = memcache.delete
