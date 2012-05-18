# transparent types used for hessian serialization
# objects of this type can appear on the wire but have no native python type

class Call(object):
    def __init__(self, method=None, args=None, headers=None, overload=None):
        self._method   = method or ''
        self._args     = args or list()
        self._headers  = headers or dict()
        self._overload = overload or False

    def _get_method(self):
        return self._method

    def _set_method(self, value):
        if isinstance(value, str):
            self._method = value
        else:
            raise TypeError("Call.method must be a string")

    method = property(_get_method, _set_method)

    def _get_args(self):
        return self._args

    def _set_args(self, value):
        if hasattr(value, '__iter__'):
            self._args = value
        else:
            raise TypeError("Call.args must be an iterable value")

    args = property(_get_args, _set_args)

    def _get_headers(self):
        return self._headers

    def _set_headers(self, value):
        if not isinstance(value, dict):
            raise TypeError("Call.headers must be a dict of strings to objects")

        for key in value.keys():
            if not isinstance(key, basestring):
                raise TypeError("Call.headers must be a dict of strings to objects")

        self._headers = value

    headers = property(_get_headers, _set_headers)

    def _get_overload(self):
        return self._overload

    def _set_overload(self, value):
        if isinstance(value, bool):
            self._overload = value
        else:
            raise TypeError("Call.overload must be True or False")

    overload = property(_get_overload, _set_overload)


class Reply(object):
    def __init__(self, value=None, headers=None):
        self.value    = value # unmanaged property
        self._headers = headers or dict()

    def _get_headers(self):
        return self._headers

    def _set_headers(self, value):
        if not isinstance(value, dict):
            raise TypeError("Call.headers must be a dict of strings to objects")

        for key in value.keys():
            if not isinstance(key, basestring):
                raise TypeError("Call.headers must be a dict of strings to objects")

        self._headers = value

    headers = property(_get_headers, _set_headers)


class Fault(Exception):
    def __init__(self, code, message, detail):
        self.code    = code
        self.message = message 
        self.detail  = detail

    # 'message' property implemented to mask DeprecationWarning
    def _get_message(self):
        return self.__message

    def _set_message(self, message):
        self.__message = message

    message = property(_get_message, _set_message)

    def __repr__(self):
        return u"<mustaine.protocol.Fault: \"%s: %s\">" % (self.code, self.message,)

    def __str__(self):
        return self.__repr__().encode('ascii', 'ignore')

    def __unicode__(self):
        return self.__repr__()

class Binary(object):
    def __init__(self, value):
        self.value = value
    def __add__(self, value):
        if self.value == None:
            return Binary(value)
        else:
            return Binary(self.value + value.value)


class Remote(object):
    def __init__(self, type_name=None, url=None):
        self.type_name = type_name
        self.url       = url


class Object(object):
    def __init__(self, meta_type, **kwargs):
        self.__meta_type = meta_type

        if kwargs:
            for key in kwargs:
                self.__dict__[key] = kwargs[key]

    @property
    def _meta_type(self):
        return self.__meta_type

    def __repr__(self):
        return "<%s object at %s>" % (self.__meta_type, hex(id(self)),)

    def __getstate__(self):
        # clear metadata for clean pickling
        t = self.__meta_type
        del self.__meta_type

        d = self.__dict__.copy()
        d['__meta_type'] = t

        # restore metadata
        self.__meta_type = t

        return d

    def __setstate__(self, d):
        self.__meta_type = d['__meta_type']
        del d['__meta_type']

        self.__dict__.update(d)

