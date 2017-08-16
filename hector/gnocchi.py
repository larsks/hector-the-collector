from __future__ import print_function
from __future__ import absolute_import

import datetime
import logging
import uuid

from gnocchiclient import auth
from gnocchiclient.v1 import client
from gnocchiclient import exceptions

LOG = logging.getLogger(__name__)


def conflictok(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except exceptions.Conflict:
            pass

    return wrapper


class ResourceNotFound(Exception):
    pass


class DefaultPolicy(object):
    archive_policy_rule_name = 'bugzilla'
    archive_policy_name = 'bugzilla'
    resource_type_name = 'bugzilla'
    metric_prefix = 'bugzilla'

    def __init__(self,
                 archive_policy_rule_name=None,
                 archive_policy_name=None,
                 resource_type_name=None,
                 metric_prefix=None):

        if archive_policy_rule_name is not None:
            self.archive_policy_rule_name = archive_policy_rule_name
        if archive_policy_name is not None:
            self.archive_policy_name = archive_policy_name
        if resource_type_name is not None:
            self.resource_type_name = resource_type_name
        if metric_prefix is not None:
            self.metric_prefix = metric_prefix

    @property
    def archive_policy(self):
        return {
            "back_window": 0,
            "aggregation_methods": [
                "max",
                "min",
                "std",
                "sum",
                "mean",
                "count"
            ],
            "name": "%s" % (self.archive_policy_name),
            "definition": [
                {
                    "timespan": "365 days",
                    "granularity": "1:00:00"
                },
                {
                    "timespan": "3650 days",
                    "granularity": "12:00:00"
                }
            ]
        }

    @property
    def archive_policy_rule(self):
        return {
            "name": "%s" % (self.archive_policy_rule_name),
            "metric_pattern": "%s.*" % (self.metric_prefix),
            "archive_policy_name": "%s" % (self.archive_policy_name)
        }

    @property
    def resource_type(self):
        return {
            "name": "%s" % (self.resource_type_name),
            "attributes": {
                "name": {
                    "type": "string",
                    "required": True
                }
            }
        }


class GnocchiWriter(object):

    def __init__(self, name,
                 policy=None,
                 username='admin',
                 endpoint='http://localhost:8041'):

        if policy is None:
            policy = DefaultPolicy()

        self.name = name
        self.policy = policy
        self.username = username
        self.endpoint = endpoint

        self._rid = None

        self.init_gnocchi()

    @property
    def rid(self):
        if self._rid is None:
            query = {'=': {'name': self.name}}
            res = self.gnocchi.resource.search(
                self.policy.resource_type_name, query)

            if len(res) != 1:
                raise ResourceNotFound(self.name)

            self._rid = res[0]['id']

        return self._rid

    def init_gnocchi(self):
        auth_plugin = auth.GnocchiBasicPlugin(user=self.username,
                                              endpoint=self.endpoint)
        self.gnocchi = client.Client(session_options={'auth': auth_plugin})

    def apply_policy(self):
        self.create_archive_policy()
        self.create_archive_policy_rule()
        self.create_resource_type()
        self.create_resource()

    @conflictok
    def create_archive_policy(self):
        self.gnocchi.archive_policy.create(self.policy.archive_policy)
        LOG.info('created archive policy %s',
                 self.policy.archive_policy_name)

    @conflictok
    def create_archive_policy_rule(self):
        self.gnocchi.archive_policy_rule.create(self.policy.archive_policy_rule)
        LOG.info('created archive policy rule %s',
                 self.policy.archive_policy_rule_name)

    @conflictok
    def create_resource_type(self):
        self.gnocchi.resource_type.create(self.policy.resource_type)
        LOG.info('created resource type %s',
                 self.policy.resource_type_name)

    @conflictok
    def create_resource(self):
        query = {'=': {'name': self.name}}
        if not self.gnocchi.resource.search(self.policy.resource_type_name,
                                            query):
            rsrc = {'name': self.name, 'id': str(uuid.uuid4())}
            self.gnocchi.resource.create(self.policy.resource_type_name,
                                         rsrc)
            LOG.info('created resource %s', self.name)

    def write(self, stats, timestamp=None):
        LOG.info('writing statistics to gnocchi')
        if timestamp is None:
            timestamp = datetime.datetime.now()

        measures = {}
        for klass, values in stats.items():
            for name, value in values.items():
                qname = '{}.{}.{}'.format(self.policy.metric_prefix,
                                          klass,
                                          name)
                LOG.debug('writing %s=%s', qname, value)
                measures[qname] = [{
                    'timestamp': timestamp,
                    'value': value
                }]

        self.gnocchi.metric.batch_resources_metrics_measures(
            {self.rid: measures}, create_metrics=True)


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    g = GnocchiWriter('dev')
    g.apply_policy()
