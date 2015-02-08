__author__ = 'dowling'
import klein

routing_cache = dict()

def route(*args, **kwargs):
    """
    This acts just like klein.route, but let's you route to bound object methods.

    Since we can only register one resource per url, you shouldn't use this on classes with multiple instances. In that
    case, we will route to the bound method of the last Application instance that is passed to your apps Holist object.
    """
    def route_decorator(method):
        routing_cache[method] = (args, kwargs)
        return method
    return route_decorator