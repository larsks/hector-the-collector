import mock
import unittest

import hector.collector


class FakeBug(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestCollector(unittest.TestCase):

    def test_init(self):
        bzapi = mock.MagicMock()
        collector = hector.collector.Collector(bzapi)
        assert collector.group_by == hector.collector.default_group_by

    def test_collect(self):
        bzapi = mock.MagicMock()

        bugs = [
            FakeBug(status='test',
                    component='test',
                    product='test',
                    keywords=['test']),
            FakeBug(status='test',
                    component='test',
                    product='test',
                    keywords=['test']),
        ]
        bzapi.query.return_value = bugs

        collector = hector.collector.Collector(bzapi)
        collector.collect('http://example.com')

        assert collector.stats['total']['bugs'] == 2
        assert collector.stats['product']['test'] == 2
