"""
Read Nginx stub status http://wiki.nginx.org/HttpStubStatusModule.

:maintainer: Peter Baumgartner <pete@lincolnloop.com>
:maturity:   new
:platform:   all
"""
import telnetlib


def stats(sock="127.0.0.1:11211"):
    """
    Return the data from memcached stats as a dictionary.

    sock
        The socket of the memcached process. Defaults to '127.0.0.1:11211'

    CLI Example::

        salt '*' memcached.stats
    """
    ip, port = sock.split(':')
    client = telnetlib.Telnet(ip, port)
    client.write('stats\n')
    # timeout after 1 second
    resp = client.read_until('END', 1)
    client.close()

    stats = {}
    for line in resp.splitlines():
        if line.startswith('STAT '):
            _, name, val = line.split(' ', 2)
            stats[name] = val
    return stats
