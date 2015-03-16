__all__ = ['long']


if 'long' in __builtins__:
    long = __builtins__['long']
else:
    class long(int):
        pass
