mapman
======
mapman scans a network to determine what hosts are available, and what services
those hosts offer. It then automatically configures [Rackspace Cloud
Monitoring](http://www.rackspace.com/cloud/monitoring/) with appropriate
entities, checks, and alarms to monitor the discovered hosts.

![screenshot](http://i.fluffy.cc/TMnvDLhXcWL8FDxLkLRDZFDpBF9MnHGw.png)

Rackspace Cloud Monitoring is an awesome (and free!) way to keep track of the
uptime and performance of your servers and applications.

mapman was written during a [Rackspace](http://www.rackspace.com/) Hack Day at
the San Francisco office. Testing was done using the [Open Computing
Facility](https://www.ocf.berkeley.edu/) network at UC Berkeley.

## Technical Details
mapman performs an [nmap](http://nmap.org/) scan of your network to determine
what hosts are available, and does a standard port scan to find services which
are offered.

Entities, checks, and alarms are added using the [Rackspace Cloud Monitoring
Python library](https://github.com/racker/rackspace-monitoring).

mapman is written in python3 and uses the nifty libraries:
* [python-nmap](http://xael.org/norman/python/python-nmap/)
* [dnspython3](https://pypi.python.org/pypi/dnspython3/)
* [rackspace-monitoring](https://github.com/racker/rackspace-monitoring) and
  [libcloud](https://libcloud.apache.org/)

## Usage
Currently, mapman has a mostly-functioning command-line tool (`cli.py`) and a
partially-completed web interface (which is not ready for use). For best results:

1. `git clone` the repository
2. Install requirements (`pip-3.2 install -r requirements.txt`)
3. Install a [slightly modified
   version](https://github.com/chriskuehl/rackspace-monitoring) of
   rackspace-monitoring (see [racker/rackspace-monitoring
   #46](https://github.com/racker/rackspace-monitoring/issues/46))
4. Execute `./cli.py`
5. Check out your new monitoring configuration at [Rackspace
   Intelligence](https://intelligence.rackspace.com/)!

You will need your Rackspace username and API key.

## Future Plans
* Add all remote check types (currently only a few are defined); this is easy!
* Finishing the web UI and allowing additional configuration of checks before
  creation
* Easy diff-ing of network scans to allow monitoring configuration to be
  modified after updates (instead of just destroyed and recreated)

## Contributing and License
mapman is copyright &copy; 2014 Chris Kuehl, with original code released under
an MIT license (see LICENSE). Contributions (in the form of issues and PRs) are
welcome!
