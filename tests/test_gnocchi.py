import mock
import unittest
import datetime

import gnocchiclient.exceptions

import hector.common
import hector.gnocchi
import hector.defaults


@mock.patch('hector.gnocchi.gnocchiclient',
            exceptions=gnocchiclient.exceptions)
@mock.patch('hector.gnocchi.gnocchiclient.v1')
class TestGnocchi(unittest.TestCase):

    def setUp(self):
        self.policy = hector.gnocchi.DefaultPolicy(
            archive_policy_rule_name='testrule',
            archive_policy_name='testpolicy',
            resource_type_name='testtype',
            metric_prefix='testprefix')

    def test_init(self, mock_client_v1, mock_client):
        g = hector.gnocchi.GnocchiWriter('test')
        g.apply_policy()

        mock_client.auth.GnocchiBasicPlugin.assert_called_with(
            user=hector.defaults.gnocchi_username,
            endpoint=hector.defaults.gnocchi_url)

    def test_init_custom_policy(self, mock_client_v1, mock_client):
        g = hector.gnocchi.GnocchiWriter('test', policy=self.policy)
        g.apply_policy()

        assert g.policy == self.policy
        assert (g.gnocchi.archive_policy.create.call_args[0][0]['name']
                == self.policy.archive_policy_name)
        assert (g.gnocchi.archive_policy_rule.create.call_args[0][0]['name']
                == self.policy.archive_policy_rule_name)
        assert (g.gnocchi.resource_type.create.call_args[0][0]['name']
                == self.policy.resource_type_name)

    def test_rid(self, mock_client_v1, mock_client):
        g = hector.gnocchi.GnocchiWriter('test')
        g.gnocchi.resource.search.return_value = [{'id': 1}]

        assert g.rid == 1

    def test_create_archive_policy(self, mock_client_v1, mock_client):
        g = hector.gnocchi.GnocchiWriter('test')
        g.create_archive_policy()

        assert g.gnocchi.archive_policy.create.called_once()
        assert (
            g.gnocchi.archive_policy.create.call_args[0][0]['name']
            == g.policy.archive_policy_name)

    def test_create_archive_policy_rule(self, mock_client_v1, mock_client):
        g = hector.gnocchi.GnocchiWriter('test')
        g.create_archive_policy_rule()

        assert g.gnocchi.archive_policy_rule.create.called_once()
        assert (
            g.gnocchi.archive_policy_rule.create.call_args[0][0]['name']
            == g.policy.archive_policy_rule_name)

    def test_create_resource_type(self, mock_client_v1, mock_client):
        g = hector.gnocchi.GnocchiWriter('test')
        g.create_resource_type()

        assert g.gnocchi.resource_type.create.called_once()
        assert (
            g.gnocchi.resource_type.create.call_args[0][0]['name']
            == g.policy.resource_type_name)

    def test_create_resource_type_conflict(self, mock_client_v1, mock_client):
        g = hector.gnocchi.GnocchiWriter('test')

        g.gnocchi.resource_type.create.side_effect = (
            gnocchiclient.exceptions.ResourceTypeAlreadyExists())

        g.create_resource_type()
        assert g.gnocchi.resource_type.create.called_once()

    def test_create_resource_missing(self, mock_client_v1, mock_client):
        g = hector.gnocchi.GnocchiWriter('test')

        g.gnocchi.resource.search.return_value = []
        g.create_resource()
        assert g.gnocchi.resource.create.called_once()

    def test_create_resource_exists(self, mock_client_v1, mock_client):
        g = hector.gnocchi.GnocchiWriter('test')

        g.gnocchi.resource.search.return_value = [{'id': 1}]
        g.create_resource()
        assert not g.gnocchi.resource.create.called

    def test_write(self, mock_client_v1, mock_client):
        g = hector.gnocchi.GnocchiWriter('test')
        timestamp = datetime.datetime.now()

        g.gnocchi.resource.search.return_value = [{'id': 1}]
        g.write({'test': {'test': 100}}, timestamp=timestamp)

        assert (
            g.gnocchi.metric.batch_resources_metrics_measures.called_with(
                {1: {'bugzilla.test.test':
                     [{'value': 100, 'timestamp': timestamp}]}},
                create_metrics=True
            ))
