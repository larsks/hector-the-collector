# Hector the Collector: Bugzilla statistics collector

## Queries

Queries are specified as a Bugzilla query URL.  You can generate these
using the advanced search web interface, e.g.,
<https://bugzilla.redhat.com/query.cgi>.

## Command line

You can run queries on the command line.  Hector will output the
results as JSON to stdout.

    usage: hector [-h] [--config CONFIG] [--url URL] [--username USERNAME]
                  [--password PASSWORD] [--debug] [--verbose]
                  [query_url [query_url ...]]

    positional arguments:
      query_url

    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG, -f CONFIG
      --url URL, -u URL
      --username USERNAME, -U USERNAME
      --password PASSWORD, -P PASSWORD

    Logging:
      --debug, -d
      --verbose, -v

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

