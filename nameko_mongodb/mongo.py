from __future__ import unicode_literals, print_function, absolute_import, division

import os
from collections import defaultdict

import six
from kombu.utils import cached_property
from mongoengine.connection import (
    register_connection,
    get_db,
    DEFAULT_CONNECTION_NAME,
    disconnect
)
from nameko.extensions import DependencyProvider
from pymongo.read_preferences import ReadPreference

from .constants import (
    MONGODB_URI,
    MONGODB_CONF,
    MONGO_DB,
    MONGO_HOST,
    MONGO_PORT,
    MONGO_USER,
    MONGO_PASS,
    MONGO_OPTIONS,
    MONGO_REPLICA_SET,
    MONGO_REPLICA_SET_OPTIONS
)

__author__ = 'Fill Q'
__all__ = ['MongoDB']


class MongoDB(DependencyProvider):
    env_prefix = 'MONGODB_'

    def __init__(self,
                 db='default',
                 collection='base',
                 alias=DEFAULT_CONNECTION_NAME,
                 document_class=dict,
                 tz_aware=None):
        self.db_name = db
        self.collection_name = collection
        self.alias = alias
        self.document_class = document_class
        self.tz_aware = tz_aware

    @cached_property
    def config(self):
        config = self.container.config
        filtered_env = filter(
            lambda f: f[0].startswith(self.env_prefix) and len(f[0]) > len(self.env_prefix),
            os.environ.items()
        )
        env_config = dict(map(lambda e: (e[0].replace(self.env_prefix, '').lower(), e[1]), filtered_env))

        mongodb_uri = env_config.get('uri', config.get(MONGODB_URI))
        if mongodb_uri:
            return mongodb_uri

        new_config = config.get(MONGODB_CONF, {})
        new_config.update(dict(map(lambda e: (e[0].lower(), e[1]), env_config)))
        return new_config

    def setup(self):
        config = {}
        if isinstance(self.config, six.text_type):
            config = dict(host=self.config)
        elif isinstance(self.config, dict):
            config = self.register_dictionary_config()
        elif isinstance(self.config, (list, tuple)):
            config = self.register_list_config()

        if config:
            if self.tz_aware:
                config['tz_aware'] = self.tz_aware
            register_connection(alias=self.alias, document_class=self.document_class, **config)

    def register_dictionary_config(self):
        alias_config = self.config.get(self.alias)
        config = self.prepare_config(config=alias_config)
        if config:
            return config
        return {}

    def register_list_config(self):
        config = defaultdict(dict)
        host, username, password = [], None, None
        for host_conf in self.config:
            if not isinstance(host_conf, dict):
                continue

            if config.get(MONGO_DB) is None:
                config[MONGO_DB] = host_conf.get(MONGO_DB)
            host.append(':'.join(map(six.text_type, filter(None, map(host_conf.get, [MONGO_HOST, MONGO_PORT])))))
            if not all([username, password]):
                username = host_conf.get(MONGO_USER)
                password = host_conf.get(MONGO_PASS)
            if config.get(MONGO_REPLICA_SET) is None:
                config[MONGO_REPLICA_SET] = host_conf.get(MONGO_REPLICA_SET, None)
            config[MONGO_OPTIONS].update(host_conf.get(MONGO_OPTIONS, {}))
            config[MONGO_REPLICA_SET_OPTIONS].update(host_conf.get(MONGO_REPLICA_SET_OPTIONS, {}))

        if config.get(MONGO_DB) is None:
            config[MONGO_DB] = self.db_name
        config['host'] = list(set(host))
        return self.prepare_config(config=config)

    def prepare_config(self, config):
        if MONGO_HOST not in config:
            return

        config = config.get(MONGO_OPTIONS) or {}
        config.update(dict(
            name=config.get(MONGO_DB, self.db_name),
            host=config[MONGO_HOST],
            port=config.get(MONGO_PORT)
        ))

        username = config.get(MONGO_USER)
        password = config.get(MONGO_PASS)
        if all([username, password]):
            # username, password = map(lambda u: quote_plus(u), [username, password])
            config.update(dict(username=username, password=password))

        config['replicaSet'] = config.get(MONGO_REPLICA_SET, None)
        config.update(config.get(MONGO_REPLICA_SET_OPTIONS, {}))
        if 'readPreference' in config:
            config['read_preference'] = config['readPreference'] = {
                'primary': ReadPreference.PRIMARY,
                'primaryPreferred': ReadPreference.PRIMARY_PREFERRED,
                'secondary': ReadPreference.SECONDARY,
                'secondaryPreferred': ReadPreference.SECONDARY_PREFERRED,
                'nearest': ReadPreference.NEAREST
            }.get(config.get('readPreference'), ReadPreference.PRIMARY)
        return config

    def get_dependency(self, worker_ctx):
        _db = get_db(alias=self.alias)
        return _db[self.collection_name]

    def worker_teardown(self, worker_ctx):
        disconnect(self.alias)
        super(MongoDB, self).worker_teardown(worker_ctx=worker_ctx)

    def stop(self):
        del self.collection_name

    def kill(self):
        try:
            self.stop()
        except Exception as e:
            print(e)
