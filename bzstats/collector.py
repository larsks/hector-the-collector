import bugzilla
import logging
from collections import defaultdict

LOG = logging.getLogger(__name__)

default_group_by = ['status', 'component', 'product', 'keywords']

def bug_to_dict(bug):
    bugd = {}
    for field in bug._bug_fields:
        bugd[field] = getattr(bug, field, None)

    return bugd

class Collector(object):
    def __init__(self, url, group_by=None):
        self.url = url
        self.group_by = group_by if group_by else default_group_by
        self._stats = defaultdict(lambda: defaultdict(int))

        self.init_bugzilla()

    def init_bugzilla(self):
        self.bzapi = bugzilla.Bugzilla(self.url)

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
