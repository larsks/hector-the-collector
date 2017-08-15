# Hector the Collector: Bugzilla statistics collector

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

