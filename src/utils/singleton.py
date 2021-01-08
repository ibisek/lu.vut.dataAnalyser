"""
Created on Jun 12, 2015

@author: ibisek
"""

"""
@see http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

alternatively
@see http://python-3-patterns-idioms-test.readthedocs.org/en/latest/Singleton.html
"""


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(_Singleton('SingletonMeta', (object,), {})):
    pass
