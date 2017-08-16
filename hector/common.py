import logging
import bugzilla

import hector.defaults

LOG = logging.getLogger(__name__)


def add_bugzilla_options(parser):
    g = parser.add_argument_group('Bugzilla')
    g.add_argument('--bugzilla-url',
                   default=hector.defaults.bugzilla_url,
                   help='URL to a Bugzilla instance')
    g.add_argument('--bugzilla-username',
                   help='Username for authenticating to Bugzilla')
    g.add_argument('--bugzilla-password',
                   help='Password for authenticating to Bugzilla')


def add_logging_options(parser):
    g = parser.add_argument_group('Logging')
    g.add_argument('--debug', '-d',
                   action='store_const',
                   const='DEBUG',
                   dest='loglevel',
                   help='Show log messages at debug level and higher')
    g.add_argument('--verbose', '-v',
                   action='store_const',
                   const='INFO',
                   dest='loglevel',
                   help='Show log messages at info level and higher')

    parser.set_defaults(loglevel=hector.defaults.loglevel)


def add_config_options(parser):
    parser.add_argument('--config', '-f',
                        help='Path to a JSON configuration file')


def connect_to_bugzilla(args, config):
    url = (args.bugzilla_url
           if args.bugzilla_url
           else config.get('bugzilla_url'))
    user = (args.bugzilla_username
            if args.bugzilla_username
            else config.get('bugzilla_username'))
    password = (args.bugzilla_password
                if args.bugzilla_password
                else config.get('bugzilla_password'))

    if not url:
        raise hector.exc.ConfigurationError('Missing Bugzilla URL')

    if not user or not password:
        LOG.warning('Without explicit credentials the bugzilla module '
                    'will use credentials from ~/.bugzillarc')

    return bugzilla.Bugzilla(
        url=url,
        user=user,
        password=password)
