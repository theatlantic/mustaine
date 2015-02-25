__all__ = ['long']


if hasattr(__builtins__, 'long'):
    long = long
else:
    class long(int):
        pass
