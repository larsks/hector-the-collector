import mock
import pytest
import sys
import unittest

import hector.exc

# We need to mock the collectd import, since the module
# is only available when running under collectd.
top_mock_collectd = mock.MagicMock()
sys.modules['collectd'] = top_mock_collectd
import hector.collectd  # NOQA


class FakeConfigNode(object):

    def __init__(self, name, value):
        self.key = name
        if isinstance(value, list):
            self.values = value
        else:
            self.values = [value]


class FakeConfig(object):

    def __init__(self, *settings):
        self.children = [FakeConfigNode(k, v)
                         for k, v in settings]


@mock.patch('hector.collectd.collectd')
@mock.patch('hector.collectd.Plugin.connect_to_bugzilla')
class TestCollectd(unittest.TestCase):

    def setUp(self):
        self.fake_config = FakeConfig(
            ('url', 'https://example.com'),
            ('username', 'testuser'),
            ('password', 'testpass'),
            ('name', 'testname'),
            ('query', 'https://example.com/query1'),
            ('query', 'https://example.com/query2'),
        )

    def test_import(self, mock_connect, mock_collectd):
        top_mock_collectd.register_config.assert_called_with(
            hector.collectd.plugin.cb_config)

    def test_plugin_manager(self, mock_connect, mock_collectd):
        mgr = hector.collectd.PluginManager()
        mgr.cb_config(self.fake_config)

        assert len(mgr.instances) == 1
        assert mgr.instances[0].iid == 0

    def test_configure(self, mock_connect, mock_collectd):
        plugin = hector.collectd.Plugin(0, self.fake_config)
        assert plugin.url == 'https://example.com'
        assert plugin.username == 'testuser'
        assert plugin.password == 'testpass'

    def test_init(self, mock_connect, mock_collectd):
        plugin = hector.collectd.Plugin(0, self.fake_config)
        plugin.bzapi = mock.MagicMock()
        plugin.bzapi.logged_in = True
        plugin.cb_init()

        mock_collectd.register_read.assert_called_with(
            plugin.cb_read,
            interval=plugin.interval,
            name='hector.%s' % plugin.instance)

    def test_init_failed_login(self, mock_connect, mock_collectd):
        plugin = hector.collectd.Plugin(0, self.fake_config)
        plugin.bzapi = mock.MagicMock()
        plugin.bzapi.logged_in = False

        with pytest.raises(hector.exc.AuthenticationError):
            plugin.cb_init()

    @mock.patch('hector.collectd.hector.collector.Collector')
    def test_cb_read(self, mock_collector, mock_connect, mock_collectd):
        plugin = hector.collectd.Plugin(0, self.fake_config)
        plugin.bzapi = mock.MagicMock()
        mock_collector_obj = mock.MagicMock()
        mock_collector.return_value = mock_collector_obj
        mock_collector_obj.stats = {'test': {'test': 100}}
        mock_values = mock.MagicMock()
        mock_collectd.Values.return_value = mock_values

        plugin.cb_read()

        mock_collector_obj.collect.assert_has_calls([
            mock.call('https://example.com/query1'),
            mock.call('https://example.com/query2'),
        ])
        mock_collectd.Values.assert_called_with(
            plugin='hector',
            type='gauge',
            interval=plugin.interval)
        assert mock_values.plugin_instance == 'testname'
        mock_values.dispatch.assert_called_once()
