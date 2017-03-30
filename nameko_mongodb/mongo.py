from __future__ import unicode_literals, print_function, absolute_import, division

import os
import weakref
from collections import defaultdict

from mongoengine.connection import (
    register_connection,
    get_db,
    DEFAULT_CONNECTION_NAME,
    _connection_settings,
    disconnect
)
from nameko.extensions import DependencyProvider
from pymongo.read_preferences import ReadPreference

__author__ = 'Fill Q'
__all__ = ['MongoDB']

MONGO_HOST = 'MONGO_HOST'
MONGO_PORT = 'MONGO_PORT'
MONGO_DB = 'MONGO_DB'
REPLICA_SET = 'REPLICA_SET'


class MongoDB(DependencyProvider):
    connections = weakref.WeakKeyDictionary()

    def __init__(self, host='localhost', port=27017,
                 db='default', collection='base', replica_set=None,
                 alias=DEFAULT_CONNECTION_NAME):
        self.db_name = db
        self.host = host
        self.port = port
        self.collection_name = collection
        self.replica_set = replica_set
        self.alias = alias

    def setup(self):
        if self.alias in _connection_settings:
            return

        mongo_conf_object = self.container.config.get('MONGO') or defaultdict(dict)
        replica_set = os.environ.get(REPLICA_SET, mongo_conf_object.get(REPLICA_SET.lower(), self.replica_set))
        host = os.environ.get(MONGO_HOST, mongo_conf_object.get('host', self.host))
        port = os.environ.get(MONGO_PORT, mongo_conf_object.get('port', self.port))
        db = os.environ.get(MONGO_DB, mongo_conf_object.get('db', self.db_name))

        # @TODO login/pass auth with MongoDB

        is_replica_set = replica_set is None
        register_connection(
            alias=self.alias,
            name=db,
            host=host,
            port=port,
            read_preference=ReadPreference.SECONDARY_PREFERRED if not is_replica_set else None,
            tz_aware=True,
            replicaSet=replica_set if not is_replica_set else None
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
