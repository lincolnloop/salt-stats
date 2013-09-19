"""
Support for getting info from a Redis Server.

:maintainer: Peter Baumgartner <pete@lincolnloop.com>
:maturity:   new
:platform:   all
"""
import salt.utils


def __virtual__():
    """
    Only load the module if redis-cli is installed
    """
    if salt.utils.which('redis-cli'):
        return 'redis'
    return False


def info(host='localhost', port='6379', password=None):
    """
    Return the data from `redis-cli info` as a dictionary.

    host
        The hostname to connect to. Defaults to 'localhost'
    port
        The port to connect to. Defaults to '6379'
    password
        An optional password to use while connecting

    CLI Example::

        salt '*' redis.info
    """

    cmd = ['redis-cli -h {host} -p {port}'.format(host=host, port=port),
           'info']
    if password:
        cmd.insert(1, '-a {password}'.format(password=password))
    out = __salt__['cmd.run'](' '.join(cmd)).splitlines()
    data = {}
    for line in out:
        if ':' in line:
            key, value = line.split(':')
            if ',' in value:
                subdata = value.split(',')
                value = dict([kv.split('=') for kv in subdata])
            data[key] = value
    return data
