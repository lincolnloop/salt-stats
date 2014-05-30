"""
Provides some of the network modules functions, but returns a parsed dict.
"""
import salt.utils
import re
import sys

def _get_match_groups(ping_output, regex):
    match = regex.search(ping_output)
    if not match:
        raise Exception('Invalid PING output:\n' + ping_output)
    return match.groups()

def _parse(ping_output):
    """
    Parses the `ping_output` string into a dictionary containing the following
    fields:

        `host`: *string*; the target hostname that was pinged
        `sent`: *int*; the number of ping request packets sent
        `received`: *int*; the number of ping reply packets received
        `minping`: *float*; the minimum (fastest) round trip ping request/reply
                    time in milliseconds
        `avgping`: *float*; the average round trip ping time in milliseconds
        `maxping`: *float*; the maximum (slowest) round trip ping time in
                    milliseconds
        `jitter`: *float*; the standard deviation between round trip ping times
                    in milliseconds
    """
    matcher = re.compile(r'PING ([a-zA-Z0-9.\-]+) \(')
    host = _get_match_groups(ping_output, matcher)[0]

    matcher = re.compile(r'(\d+) packets transmitted, (\d+) received')
    sent, received = _get_match_groups(ping_output, matcher)

    try:
        matcher = re.compile(r'(\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)')
        minping, avgping, maxping, jitter = _get_match_groups(ping_output,
                                                              matcher)
    except:
        minping, avgping, maxping, jitter = ['NaN']*4

    return {'host': host, 'sent': sent, 'received': received,
            'minping': minping, 'avgping': avgping, 'maxping': maxping,
            'jitter': jitter}


def ping(host, count=4):
    '''
    Performs a ping to a host

    CLI Example:

    .. code-block:: bash

        salt '*' parsed_network.ping archlinux.org
    '''
    cmd = 'ping -c {0} {1}'.format(count, salt.utils.network.sanitize_host(host))
    return _parse(__salt__['cmd.run'](cmd))