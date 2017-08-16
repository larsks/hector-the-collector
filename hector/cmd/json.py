from __future__ import print_function
from __future__ import absolute_import

import argparse
import datetime
import json
import logging
import sys

import hector.collector
import hector.common

LOG = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser()

    hector.common.add_bugzilla_options(p)
    hector.common.add_logging_options(p)
    hector.common.add_config_options(p)

    p.add_argument('query_url', nargs='*')

    return p.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=args.loglevel)

    if args.config:
        with open(args.config) as fd:
            config = json.load(fd)
    else:
        config = {}

    queries = args.query_url if args.query_url else config.get('query_urls')

    if not queries:
        LOG.error("you must provide at least one query")
        sys.exit(2)

    bzapi = hector.common.connect_to_bugzilla(args, config)
    c = hector.collector.Collector(bzapi)
    for query in queries:
        c.collect(query)

    print(json.dumps({'date': datetime.datetime.utcnow().isoformat(),
                      'stats': c.stats}))


if __name__ == '__main__':
    main()
