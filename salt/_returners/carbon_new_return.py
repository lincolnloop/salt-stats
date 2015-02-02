# -*- coding: utf-8 -*-
'''
A carbon returner that works

Pillar needs::

    carbon_returner:
      host: localhost
      port: 2003
      prefix: salt.metric
'''

import logging
import socket
import time

log = logging.getLogger(__name__)


__virtualname__ = 'carbon_new'

def __virtual__():
    return __virtualname__


def _flatten_values(obj, base=None):
    """
    Recursive function to flatten dictionaries and
    coerce values to floats.
    """
    flattened = {}
    # convert list to dictionary
    if isinstance(obj, list):
        obj = dict([(str(pair[0]), pair[1]) for pair in enumerate(obj)])
    elif not isinstance(obj, dict):
        obj = {'value': obj}
    for key, item in obj.items():
        key = base and '.'.join([base, key]) or key
        if isinstance(item, dict) or isinstance(item, list):
            flattened.update(_flatten_values(item, base=key))
        else:
            try:
                flattened[key] = float(item)
            except ValueError:
                pass
    return flattened


def returner(ret):
    config = __pillar__.get('carbon_returner', {})
    host = config.get('host', 'localhost')
    port = config.get('port', 2003)
    # don't keep in dictionary so it can easily be set per-pillar
    prefix = __pillar__.get('carbon_returner_prefix', {})

    log.debug('Carbon pillar configured with host: {0}:{1}'.format(host, port))

    try:
        carbon_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM,
                                    socket.IPPROTO_TCP)
        carbon_sock.connect((host, port))
    except socket.error as e:
        log.error('Error connecting to {0}:{1}, {2}'.format(host, port, e))
        return
    # convert to flat plaintext list
    timestamp = int(time.time())
    data = _flatten_values(ret['return'])
    carbon_base = "{prefix}.{host}.{function}".format(prefix=prefix,
        host=ret['id'].replace('.', '_'), function=ret['fun'])
    log.debug("Carbon metric base: %s", carbon_base)
    metrics = []
    for key, value in data.items():
        name = '.'.join([carbon_base, key.replace(' ', '_')])
        metrics.append(" ".join([name, str(value), str(timestamp)]))
    log.info("Sending %s metrics to carbon", len(metrics))
    plaintext = '\n'.join(metrics) + '\n'

    log.debug(plaintext)
    # send to carbon
    total_sent_bytes = 0
    while total_sent_bytes < len(plaintext):
        sent_bytes = carbon_sock.send(plaintext[total_sent_bytes:])
        if sent_bytes == 0:
            log.error('Bytes sent 0, Connection reset?')
            return
        logging.debug('Sent {0} bytes to carbon'.format(sent_bytes))

        total_sent_bytes += sent_bytes
    carbon_sock.shutdown(socket.SHUT_RDWR)
