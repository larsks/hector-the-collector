# Hector the Collector: Bugzilla statistics collector

## Queries

Queries are specified as a Bugzilla query URL.  You can generate these
using the advanced search web interface, e.g.,
<https://bugzilla.redhat.com/query.cgi>.

## hector-json

Perform queries and print the results as JSON to stdout.

    usage: hector-json [-h] [--bugzilla-url BUGZILLA_URL]
                       [--bugzilla-username BUGZILLA_USERNAME]
                       [--bugzilla-password BUGZILLA_PASSWORD] [--debug]
                       [--verbose] [--config CONFIG]
                       [query_url [query_url ...]]

    positional arguments:
      query_url

    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG, -f CONFIG
                            Path to a JSON configuration file

    Bugzilla:
      --bugzilla-url BUGZILLA_URL
                            URL to a Bugzilla instance
      --bugzilla-username BUGZILLA_USERNAME
                            Username for authenticating to Bugzilla
      --bugzilla-password BUGZILLA_PASSWORD
                            Password for authenticating to Bugzilla

    Logging:
      --debug, -d           Show log messages at debug level and higher
      --verbose, -v         Show log messages at info level and higher

## hector-gnocchi

Perform queries and store the results in Gnocchi.

    usage: hector-gnocchi [-h] [--bugzilla-url BUGZILLA_URL]
                          [--bugzilla-username BUGZILLA_USERNAME]
                          [--bugzilla-password BUGZILLA_PASSWORD] [--debug]
                          [--verbose] [--config CONFIG]
                          [--gnocchi-instance-name GNOCCHI_INSTANCE_NAME]
                          [--gnocchi-url GNOCCHI_URL]
                          [--gnocchi-username GNOCCHI_USERNAME] [--skip-policy]
                          [query_url [query_url ...]]

    positional arguments:
      query_url

    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG, -f CONFIG
                            Path to a JSON configuration file

    Bugzilla:
      --bugzilla-url BUGZILLA_URL
                            URL to a Bugzilla instance
      --bugzilla-username BUGZILLA_USERNAME
                            Username for authenticating to Bugzilla
      --bugzilla-password BUGZILLA_PASSWORD
                            Password for authenticating to Bugzilla

    Logging:
      --debug, -d           Show log messages at debug level and higher
      --verbose, -v         Show log messages at info level and higher

    Gnocchi:
      --gnocchi-instance-name GNOCCHI_INSTANCE_NAME
                            Name of resource with which to associate metrics
      --gnocchi-url GNOCCHI_URL
                            URL to a Gnocchi instance
      --gnocchi-username GNOCCHI_USERNAME
                            Username for authenticating to Gnocchi
      --skip-policy         Do not attempt to create Gnocchi policy

## Configuration

    {
      "query_urls": [
        "https://bugzilla.redhat.com/buglist.cgi?bug_status=NEW..."
        "https://bugzilla.redhat.com/buglist.cgi?bug_status=NEW..."
      ]
    }

## Configuring the CollectD plugin

    LoadPlugin "python"
    <Plugin "python">
      LogTraces true
      Import "bzstats.collectd"

      # You may have multiple module blocks.  You may give them unique
      # names with the "Name" directive, or just accept the default
      # (unknown-0, unknown-1, ...) if you don't care.  The name is
      # used in metric names and log messages.

      <Module "bzstats.collectd">
        URL "https://bugzilla.redhat.com"

        # If you don't provide credentials here, the bugzilla
        # module will look for ~/.bugzillarc.
        Username "batman"
        Password "thedarkknight"

        # How often to collect statistics (in seconds).  The default
        # is every 12 hours.
        Interval 86400

        # There may be multiple Query directives in a single block.
        # Statistics will be calculated across the results of all
        # the queries.
        Query "https://bugzilla.redhat.com/buglist.cgi?bug_status=NEW..."
        Query "https://bugzilla.redhat.com/buglist.cgi?bug_status=NEW..."
      </Module>
    </Plugin>

