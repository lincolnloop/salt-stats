# -*- coding: utf-8 -*-
'''
Salt returner that reports stats to InfluxDB. The returner will
inspect the payload coercing values into floats where possible.

Pillar needs something like::

    influxdb_returner:
      url: http://localhost:8086
      user: root
      password: root
      database: salt
'''

import base64
import fnmatch
import logging
import json
import urllib2

logger = logging.getLogger(__name__)

__virtualname__ = 'influxdb'

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
        if isinstance(item, dict):
            flattened.update(_flatten_values(item, base=key))
        else:
            try:
                flattened[key] = float(item)
            except ValueError:
                flattened[key] = item
    return flattened

def returner(ret):
    user = __salt__['pillar.get']('influxdb_returner:user', '')
    password = __salt__['pillar.get']('influxdb_returner:password', '')
    database = __salt__['pillar.get']('influxdb_returner:database', '')
    host = __salt__['pillar.get']('influxdb_returner:url', '')

    data = _flatten_values(ret['return'])
    series = "{host}-{function}".format(host=ret['id'], function=ret['fun'])
    logger.debug("InfluxDB series name: %s", series)
    payload = json.dumps([{
        'name': series,
        'columns': data.keys(),
        'points': [data.values()],
    }])
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain'}
    url = "{host}/db/{db}/series?u={user}&p={pw}".format(
        host=host, db=database, user=user, pw=password)
    req = urllib2.Request(url, payload, headers)
    try:
        handler = urllib2.urlopen(req)
        logger.debug("InfluxDB responded %s", handler.getcode())
    except urllib2.HTTPError as exp:
        logger.error("InfluxDB request failed with code %s", exp.code)

    handler.close()
