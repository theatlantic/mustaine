"""
transparent types used for hessian serialization
objects of this type can appear on the wire but have no native python type
"""
import copy
import six


class Call(object):

    def __init__(self, method=None, args=None, headers=None, overload=None, version=1):
        self.method = method or ''
        self.args = args or list()
        self.headers = headers or dict()
        self.overload = overload or False
        self.version = version

    def _get_method(self):
        return self._method

    def _set_method(self, value):
        if isinstance(value, six.binary_type):
            self._method = value
        elif isinstance(value, six.text_type):
            self._method = value.encode('utf-8')
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
            if not isinstance(key, six.string_types):
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

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


class Reply(object):

    def __init__(self, value=None, headers=None, version=None):
        self.value = value  # unmanaged property
        self._headers = headers or {}
        self.version = version

    def _get_headers(self):
        return self._headers

    def _set_headers(self, value):
        if not isinstance(value, dict):
            raise TypeError("Call.headers must be a dict of strings to objects")

        for key in value.keys():
            if not isinstance(key, six.string_types):
                raise TypeError("Call.headers must be a dict of strings to objects")

        self._headers = value

    headers = property(_get_headers, _set_headers)


class Fault(Exception):

    def __init__(self, code, message, detail):
        self.code = code
        self.message = message
        self.detail = detail

    # 'message' property implemented to mask DeprecationWarning
    def _get_message(self):
        return self.__message

    def _set_message(self, message):
        self.__message = message

    message = property(_get_message, _set_message)

    def __repr__(self):
        return "<pyhessian.protocol.Fault: \"%s: %s\">" % (self.code, self.message,)

    def __str__(self):
        return self.__repr__()


class Binary(object):

    def __init__(self, value):
        self.value = value

    def __add__(self, value):
        if self.value is None:
            return Binary(value)
        else:
            return Binary(self.value + value.value)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)


class Remote(object):

    def __init__(self, type_name=None, url=None):
        self.type_name = type_name
        self.url = url


class ObjectMeta(type):

    def __instancecheck__(cls, other):
        if Object not in other.__class__.__mro__:
            return False
        cls_type_name = '.'.join([cls.__module__, cls.__name__])
        if cls_type_name == 'pyhessian.protocol.Object':
            return True
        other_type_name = '.'.join([type(other).__module__, type(other).__name__])
        return cls_type_name == other_type_name


@six.add_metaclass(ObjectMeta)
class Object(object):

    def __init__(self, *args, **kwargs):
        for f, arg in zip(self._hessian_field_names, args):
            setattr(self, f, arg)
        for f, arg in six.iteritems(kwargs):
            setattr(self, f, arg)

    def __repr__(self):
        return (u"<%s.%s object at 0x%x>"
            % (type(self).__module__, type(self).__name__, id(self)))

    def __str__(self):
        return self.__repr__().encode('ascii', 'ignore')

    def __unicode__(self):
        return self.__repr__()

    def __getstate__(self):
        obj_dict = self.__dict__.copy()
        obj_dict.pop('_hessian_factory_args', None)
        obj_dict.pop('_hessian_field_names', None)
        return obj_dict

    def __setstate__(self, obj_dict):
        self.__dict__.update(obj_dict)

    def __reduce__(self):
        return (object_factory, self._hessian_factory_args, self.__dict__)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        from pyhessian.encoder import encode_object
        return encode_object(self) == encode_object(other)

    def __ne__(self, other):
        return not self.__eq__(other)


def cls_factory(name, fields=None, bases=None, attrs=None):
    cls_attrs = copy.deepcopy(attrs) if attrs else {}
    fields = fields or []

    for i, f in enumerate(fields):
        if six.PY2 and isinstance(f, unicode):
            fields[i] = f.encode('utf-8')
        elif six.PY3 and isinstance(f, six.binary_type):
            fields[i] = f.decode('utf-8')

    if six.PY2 and isinstance(name, unicode):
        name = name.encode('utf-8')
    elif six.PY3 and isinstance(name, six.binary_type):
        name = name.decode('utf-8')

    module_name, _, cls_name = name.rpartition('.')

    bases = bases or tuple()
    cls_attrs.update({
        '_hessian_field_names': fields,
        '_hessian_factory_args': (name, fields, bases, attrs),
    })

    if module_name:
        cls_attrs['__module__'] = module_name

    bases += (Object, )

    return type(cls_name, bases, cls_attrs)


def object_factory(name, fields=None, bases=None, attrs=None, **kwargs):
    if fields is None and kwargs:
        fields = kwargs.keys()
    cls = cls_factory(name, fields, bases, attrs)
    obj = cls.__new__(cls)
    obj.__setstate__(kwargs)
    return obj
