"""
for functions that must be written differently between python2 and python3
"""


def is_int(number):
    return isinstance(number, (int, long))
