"""
StaticDict is an immutable dictionary.
Getter is an object that remembers how to retrieve a parameter for a certain class or classes.
"""


class StaticDict(object):
    def __init__(self, dictionary):
        self._dic = dictionary.copy()

    def keys(self):
        return self._dic.keys()

    def values(self):
        return self._dic.values()

    def items(self):
        return self._dic.items()

    def copy(self):
        return StaticDict(self._dic)

    def delete(self, key):
        new = self._dic.copy()
        del new[key]
        return StaticDict(new)

    def get(self, key, default=None):
        return self._dic.get(key, default)

    def set(self, key, value):
        new = self._dic.copy()
        new[key] = value
        return StaticDict(new)


class Getter(object):
    def __init__(self, method_name, default_value, is_property=False):
        self._method_name = method_name
        self._is_property = is_property
        try:
            self._default_value = default_value.copy()
            self._copyable = True
        except AttributeError:
            self._default_value = default_value
            self._copyable = False

    def get_default(self):
        if self._copyable:
            return self._default_value.copy()
        else:
            return self._default_value

    def get_from(self, obj):
        if self._is_property:
            return obj.__getattribute__(self._method_name)
        else:
            return obj.__getattribute__(self._method_name)()

    def get_bool(self):
        return self._is_property

    def get_name(self):
        return self._method_name

    def __str__(self):
        is_property = {True: 'property', False: 'method'}
        return '{}: "{}", default: {!r}'.format(is_property[self._is_property], self._method_name, self._default_value)

    def __eq__(self, other):
        try:
            return ((self.get_default(), self.get_bool(), self.get_name()) ==
                    (other.get_default(), other.get_bool(), other.get_name()))
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other
