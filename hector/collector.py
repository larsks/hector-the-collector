import logging
from collections import defaultdict

LOG = logging.getLogger(__name__)

default_group_by = ['status', 'component', 'product', 'keywords']


class Collector(object):

    def __init__(self, bzapi, group_by=None):
        self.group_by = group_by if group_by else default_group_by
        self._stats = defaultdict(lambda: defaultdict(int))
        self.bzapi = bzapi
        self.seen = set()

    def collect(self, query_url):
        query = self.bzapi.url_to_query(query_url)
        LOG.debug('query: %s', query)
        res = self.bzapi.query(query)

        for bug in res:

            # avoiding processing the same bug multiple times if it
            # is found in multiple queries
            if bug.id in self.seen:
                continue
            self.seen.add(bug.id)
            self._stats['total']['bugs'] += 1

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
