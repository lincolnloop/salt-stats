"""
Read Nginx stub status http://wiki.nginx.org/HttpStubStatusModule.

:maintainer: Peter Baumgartner <pete@lincolnloop.com>
:maturity:   new
:platform:   all
"""
import urllib2
import salt.utils


def status(url="http://127.0.0.1/status"):
    """
    Return the data from an Nginx status page as a dictionary.

    url
        The URL of the status page. Defaults to 'http://127.0.0.1/status'

    CLI Example::

        salt '*' nginx.status
    """
    resp = urllib2.urlopen(url)
    status = resp.read()
    resp.close()

    lines = status.splitlines()
    if not len(lines) == 4:
        return
    # "Active connections: 1 "
    active_connections = lines[0].split()[2]
    # "server accepts handled requests"
    # "  12 12 9 "
    accepted, handled, requests = lines[2].split()
    # "Reading: 0 Writing: 1 Waiting: 0 "
    _, reading, _, writing, _, waiting = lines[3].split()
    return {
        'active connections': int(active_connections),
        'accepted': int(accepted),
        'handled': int(handled),
        'requests': int(requests),
        'reading': int(reading),
        'writing': int(writing),
        'waiting': int(waiting),
    }
