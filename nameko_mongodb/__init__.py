from __future__ import print_function
import weakref

import eventlet

eventlet.monkey_patch()
# pymongo = eventlet.import_patched('pymongo')
# mongoengine = eventlet.import_patched('mongoengine')

from pymongo.read_preferences import ReadPreference
from mongoengine.connection import register_connection, get_db, DEFAULT_CONNECTION_NAME, _connection_settings, disconnect
from nameko.extensions import DependencyProvider

__author__ = 'Fill Q'
__all__ = ['MongoDB']


class MongoDB(DependencyProvider):
    connections = weakref.WeakKeyDictionary()

    def __init__(self, db='default', collection='base', replica_set='grissli', db_alias=DEFAULT_CONNECTION_NAME):
        self.db_name = db
        self.collection_name = collection
        self.replica_set = replica_set
        self.alias = db_alias

    def setup(self):
        if self.alias in _connection_settings:
            return

        replSet = self.replica_set is None
        register_connection(
            alias=self.alias,
            name=self.db_name,
            host='mongodb',
            port=None,
            read_preference=ReadPreference.SECONDARY_PREFERRED if not replSet else None,
            tz_aware=True,
            replicaSet=self.replica_set if not replSet else None
        )

    def get_dependency(self, worker_ctx):
        _db = get_db(alias=self.alias)
        return _db[self.collection_name]

    def worker_teardown(self, worker_ctx):
        disconnect(self.alias)
        super(MongoDB, self).worker_teardown(worker_ctx=worker_ctx)

    def stop(self):
        del self.collection_name
        del self.connections

    def kill(self):
        try:
            self.stop()
        except Exception as e:
            print(e)