from __future__ import print_function
from __future__ import absolute_import

import argparse
import json
import logging
import sys
import time

import hector.collector
import hector.gnocchi
import hector.defaults
import hector.common
import hector.exc

LOG = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser()

    hector.common.add_bugzilla_options(p)
    hector.common.add_logging_options(p)
    hector.common.add_config_options(p)

    p.add_argument('--interval',
                   type=int,
                   help='Update every INTERVAL seconds')

    g = p.add_argument_group('Gnocchi')
    g.add_argument('--gnocchi-instance-name',
                   default=hector.defaults.gnocchi_instance_name,
                   help='Name of resource with which to associate metrics')
    g.add_argument('--gnocchi-url',
                   default=hector.defaults.gnocchi_url,
                   help='URL to a Gnocchi instance')
    g.add_argument('--gnocchi-username',
                   default=hector.defaults.gnocchi_username,
                   help='Username for authenticating to Gnocchi')
    g.add_argument('--skip-policy',
                   action='store_true',
                   help='Do not attempt to create Gnocchi policy')

    p.add_argument('query_url', nargs='*')

    return p.parse_args()


def _real_main():
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
    g = hector.gnocchi.GnocchiWriter(
        args.gnocchi_instance_name,
        username=args.gnocchi_username,
        endpoint=args.gnocchi_url)
    if not args.skip_policy:
        g.apply_policy()

    while True:
        time_start = time.time()

        c = hector.collector.Collector(bzapi)

        LOG.info('start collecting statistics')
        for query in queries:
            c.collect(query)
        LOG.info('finish collecting statistics')

        g.write(c.stats)

        if not args.interval:
            break

        time_end = time.time()
        LOG.debug('collection took %d seconds', time_end - time_start)
        time.sleep(args.interval - (time_end - time_start))


def main():
    try:
        return _real_main()
    except hector.exc.HectorException as err:
        LOG.error(err)
        sys.exit(1)


if __name__ == '__main__':
    main()
