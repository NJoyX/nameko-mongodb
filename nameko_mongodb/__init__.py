import eventlet

eventlet.monkey_patch()
# pymongo = eventlet.import_patched('pymongo')
# mongoengine = eventlet.import_patched('mongoengine')

from .mongo import MongoDB

__author__ = 'Fill Q'
__all__ = ['MongoDB']
