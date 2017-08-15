from __future__ import print_function
from __future__ import absolute_import

import bugzilla
import collectd
import itertools
import threading
import time

import bzstats.collector

default_interval = 12 * 3600  # 12 hours

class BzstatsError(Exception):
    pass

class ConfigurationError(BzstatsError):
    pass

class AuthenticationError(BzstatsError):
    pass

class BzstatsPlugin(object):
    def __init__(self, iid, config):
        self.bzapi = None
        self.instance = 'unknown-%d' % iid
        self.interval = default_interval
        self.password = None
        self.query_urls = []
        self.url = None
        self.username = None

        self.configure(config)

    def configure(self, config):
        for node in config.children:
            key = node.key.lower()

            if key == 'url':
                self.url = node.values[0]
            elif key == 'username':
                self.username = node.values[0]
            elif key == 'password':
                self.password = node.values[0]
            elif key == 'name':
                self.instance = node.values[0]
            elif key == 'interval':
                self.interval = node.values[0]
            elif key == 'query':
                self.query_urls.append(node.values[0])

    def log_debug(self, msg):
        collectd.debug('bzstats.%s: %s' % (self.instance, msg))

    def log_info(self, msg):
        collectd.info('bzstats.%s: %s' % (self.instance, msg))

    def log_warning(self, msg):
        collectd.warning('bzstats.%s: %s' % (self.instance, msg))

    def log_error(self, msg):
        collectd.error('bzstats.%s: %s' % (self.instance, msg))

    def cb_init(self):
        self.log_info('start initialize bzstats@%s' % self.instance)

        if not self.url:
            raise ConfigurationError('you have not configure a bugzilla url')

        if len(self.query_urls) == 0:
            raise ConfigurationError('you have not configured any queries')

        if not self.username or not self.password:
            self.log_warning('you have not configured any credentials')

        self.log_info('connecting to url %s' % self.url)
        self.bzapi = bugzilla.Bugzilla(url=self.url,
                                       user=self.username,
                                       password=self.password)

        if not self.bzapi.logged_in:
            raise AuthenticationError(
                'failed to authenticate to %s' % self.url)

        res = collectd.register_read(self.cb_read,
                                     interval=self.interval,
                                     name='bzstats.%s' % self.instance)

        self.log_info('finish initialize bzstats@%s' % self.instance)

    def cb_read(self):
        self.log_info('start collection run for bzstats@%s' % (
            self.instance))

        collector = bzstats.collector.Collector(self.bzapi)
        for query in self.query_urls:
            self.log_info('processing query %s' % query)
            collector.collect(query)

        for klass, values in collector.stats.items():
            for name, value in values.items():
                val = collectd.Values(plugin='bzstats',
                                      type='gauge',
                                      interval=self.interval)
                val.plugin_instance = self.instance
                val.type_instance = '%s.%s' % (klass, name)
                val.values = [value]
                val.dispatch()

        self.log_info('finish collection run for bzstats@%s' % (
            self.instance))


class BzstatsPluginManager(object):
    '''This is a simple wrapper that handles instantiating a new BzStatsPlugin
    instance for each configuration block encountered by collectd.'''

    def __init__(self):
        self.iid = itertools.count()
        self.instances = []

    def cb_config(self, config):
        iid = next(self.iid)
        new = BzstatsPlugin(iid, config)
        self.instances.append(new)
        collectd.register_init(new.cb_init)


plugin = BzstatsPluginManager()
collectd.register_config(plugin.cb_config)
