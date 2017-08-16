import logging
from collections import defaultdict

LOG = logging.getLogger(__name__)

default_group_by = ['status', 'component', 'product', 'keywords']


class Collector(object):

    def __init__(self, bzapi, group_by=None):
        self.group_by = group_by if group_by else default_group_by
        self._stats = defaultdict(lambda: defaultdict(int))
        self.bzapi = bzapi

    def collect(self, query_url):
        query = self.bzapi.url_to_query(query_url)
        LOG.info('query: %s', query)
        res = self.bzapi.query(query)
        self._stats['total']['bugs'] += len(res)

        for bug in res:
            for field in self.group_by:
                fieldval = getattr(bug, field)
                if isinstance(fieldval, list):
                    for v in fieldval:
                        self._stats[field][v.lower()] += 1
                else:
                    self._stats[field][fieldval.lower()] += 1

    @property
    def stats(self):
        return {k: dict(v) for k, v in self._stats.items()}
