try:
    from cStringIO import StringIO
except ImportError:
    from six import BytesIO as StringIO

from functools import reduce as _reduce


__all__ = ['BufferedReader', 'toposort', 'toposort_flatten', 'cached_property']


class BufferedReader(object):

    def __init__(self, input, buffer_size=65535):
        self.__input = input
        self.__buffer_size = buffer_size
        self.__buffer = StringIO()

        # initial fill
        chunk = input.read(buffer_size)
        self.__byte_count = len(chunk)
        self.__buffer.write(chunk)
        self.__buffer.seek(0)

    def read(self, byte_count):
        difference = byte_count - self.__byte_count

        if difference < 0:
            chunk = self.__buffer.read(byte_count)
            self.__byte_count -= byte_count
        else:
            chunk = self.__buffer.read() + self.__input.read(difference)

            # verify size
            if len(chunk) != byte_count:
                raise EOFError("Encountered unexpected end of stream")

            # reset internal buffer
            self.__buffer.seek(0)
            self.__buffer.truncate()

            # replenish
            fresh_chunk = self.__input.read(self.__buffer_size)
            self.__byte_count = len(fresh_chunk)
            self.__buffer.write(fresh_chunk)
            self.__buffer.seek(0)

        return chunk


#######################################################################
# Implements a topological sort algorithm.
#
# Copyright 2014 True Blade Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Notes:
#  Based on http://code.activestate.com/recipes/578272-topological-sort
#   with these major changes:
#    Added unittests.
#    Deleted doctests (maybe not the best idea in the world, but it cleans
#     up the docstring).
#    Moved functools import to the top of the file.
#    Changed assert to a ValueError.
#    Changed iter[items|keys] to [items|keys], for python 3
#     compatibility. I don't think it matters for python 2 these are
#     now lists instead of iterables.
#    Copy the input so as to leave it unmodified.
#    Renamed function from toposort2 to toposort.
#    Handle empty input.
#    Switch tests to use set literals.
#
########################################################################


def toposort(data):
    """
    Dependencies are expressed as a dictionary whose keys are items
    and whose values are a set of dependent items. Output is a list of
    sets in topological order. The first set consists of items with no
    dependences, each subsequent set consists of items that depend upon
    items in the preceeding sets.
    """

    # Special case empty input.
    if len(data) == 0:
        return

    # Copy the input so as to leave it unmodified.
    data = data.copy()

    # Ignore self dependencies.
    for k, v in data.items():
        v.discard(k)
    # Find all items that don't depend on anything.
    extra_items_in_deps = _reduce(set.union, data.values()) - set(data.keys())
    # Add empty dependences where needed.
    data.update(dict(([item, set()] for item in extra_items_in_deps)))
    while True:
        ordered = set(item for item, dep in data.items() if len(dep) == 0)
        if not ordered:
            break
        yield ordered
        data = dict(([item, (dep - ordered)]
                for item, dep in data.items()
                    if item not in ordered))
    if len(data) != 0:
        raise ValueError('Cyclic dependencies exist among these items: %s' %
            ', '.join(repr(x) for x in data.items()))


def toposort_flatten(data, sort=True):
    """
    Returns a single list of dependencies. For any set returned by
    toposort(), those items are sorted and appended to the result (just to
    make the results deterministic).
    """

    result = []
    for d in toposort(data):
        result.extend((sorted if sort else list)(d))
    return result


class cached_property(object):
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.

    Optional ``name`` argument allows you to make cached properties of other
    methods. (e.g.  url = cached_property(get_absolute_url, name='url') )
    """
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res
