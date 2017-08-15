from __future__ import print_function

import argparse
import bugzilla
import datetime
import json
import logging
import os
import sys

import hector.collector

LOG = logging.getLogger(__name__)

def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--config', '-f')

    p.add_argument('--url', '-u',
                   default='https://bugzilla.redhat.com')
    p.add_argument('--username', '-U')
    p.add_argument('--password', '-P')

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

    url = args.url if args.url else config.get('url')
    username = args.username if args.username else config.get('username')
    password = args.password if args.password else config.get('password')
    queries = args.query_url if args.query_url else config.get('query_urls')

    if url is None:
        LOG.error("you must provide a bugzilla url")
        sys.exit(2)

    if not queries:
        LOG.error("you must provide at least one query")
        sys.exit(2)

    bzapi = bugzilla.Bugzilla(url=args.url,
                              user=username,
                              password=password)
    c = hector.collector.Collector(bzapi)
    for query in queries:
        c.collect(query)

    print(json.dumps({'date': datetime.datetime.utcnow().isoformat(),
                      'stats': c.stats}))

if __name__ == '__main__':
    main()
