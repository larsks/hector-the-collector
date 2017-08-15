from __future__ import print_function

import argparse
import bugzilla
import datetime
import json
import logging
import os
import sys

import bzstats.collector

LOG = logging.getLogger(__name__)

def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--config', '-f')
    p.add_argument('--url', '-u',
                   default='https://bugzilla.redhat.com')

    g = p.add_argument_group('Logging')
    g.add_argument('--debug', '-d',
                   action='store_const',
                   const='DEBUG',
                   dest='loglevel')
    g.add_argument('--verbose', '-v',
                   action='store_const',
                   const='INFO',
                   dest='loglevel')

    p.add_argument('query_url', nargs='*')

    p.set_defaults(loglevel='WARNING')

    return p.parse_args()

def main():
    args = parse_args()
    logging.basicConfig(level=args.loglevel)

    if args.config:
        with open(args.config) as fd:
            config = json.load(fd)
    else:
        config = {}

    LOG.info('config=%s', config)

    url = args.url if args.url else config.get('url')
    if url is None:
        LOG.error("you must provide a bugzilla url")
        sys.exit(2)

    queries = args.query_url if args.query_url else config.get('query_urls')
    if not queries:
        LOG.error("you must provide at least one query")
        sys.exit(2)

    bzapi = bugzilla.Bugzilla(url=args.url)
    c = bzstats.collector.Collector(bzapi)
    for query in queries:
        c.collect(query)

    print(json.dumps({'date': datetime.datetime.utcnow().isoformat(),
                      'stats': c.stats}))

if __name__ == '__main__':
    main()
