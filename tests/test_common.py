import argparse
import unittest
import mock

import hector.common


class TestCommon(unittest.TestCase):

    def test_add_bugzilla_options(self):
        p = argparse.ArgumentParser()
        hector.common.add_bugzilla_options(p)
        args = p.parse_args([])

        assert hasattr(args, 'bugzilla_url')

    def test_add_logging_options(self):
        p = argparse.ArgumentParser()
        hector.common.add_logging_options(p)
        args = p.parse_args([])

        assert hasattr(args, 'loglevel')
        assert args.loglevel == 'WARNING'

    def test_add_config_options(self):
        p = argparse.ArgumentParser()
        hector.common.add_config_options(p)
        args = p.parse_args([])

        assert hasattr(args, 'config')

    @mock.patch('hector.common.bugzilla')
    def test_connect_to_bugzilla_default(self, mock_bugzilla):
        p = argparse.ArgumentParser()
        hector.common.add_bugzilla_options(p)
        args = p.parse_args([])
        config = {}
        hector.common.connect_to_bugzilla(args, config)

        mock_bugzilla.Bugzilla.assert_called_with(
            url=hector.defaults.bugzilla_url,
            user=None,
            password=None)

    @mock.patch('hector.common.bugzilla')
    def test_connect_to_bugzilla_explicit(self, mock_bugzilla):
        p = argparse.ArgumentParser()
        hector.common.add_bugzilla_options(p)
        args = p.parse_args(['--bugzilla-username', 'testuser'])
        config = {}
        hector.common.connect_to_bugzilla(args, config)

        mock_bugzilla.Bugzilla.assert_called_with(
            url=hector.defaults.bugzilla_url,
            user='testuser',
            password=None)
