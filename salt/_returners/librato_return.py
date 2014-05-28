# -*- coding: utf-8 -*-
'''
Salt returner that reports stats to Librato. The returner will
inspect the payload coercing values into floats where possible.
Text responses will be ignored

Pillar needs something like::

    librato:
      email: me@example.com
      api_token: abc1234def
'''

import base64
import fnmatch
import logging
import json
import urllib2

logger = logging.getLogger(__name__)

__virtualname__ = 'librato'

def __virtual__():
    return __virtualname__


def _flatten_and_collect_floats(obj, base=None):
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
            flattened.update(_flatten_and_collect_floats(item, base=key))
        else:
            try:
                flattened[key] = float(item)
            except ValueError:
                pass
    return flattened


def _post_to_librato(data, user, token, metric='gauges'):
    url = 'https://metrics-api.librato.com/v1/metrics'
    logger.info("Sending %s %s to Librato", len(data), metric)
    payload = {metric: data}
    req = urllib2.Request(url, json.dumps(payload),
                          {'Content-Type': 'application/json'})

    encoded = base64.standard_b64encode(':'.join([user, token]))
    req.add_header("Authorization", "Basic {0}".format(encoded))
    try:
        handler = urllib2.urlopen(req)
    except urllib2.HTTPError as exp:
        logger.error("Librato request failed with code %s", exp.code)

    handler = urllib2.urlopen(req)
    handler.close()


def _matches_pattern(name, pattern_list):
    for pattern in pattern_list:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def returner(ret):
    pillar = __salt__['pillar.raw']()
    email = pillar['librato']['email']
    api_token = pillar['librato']['api_token']
    exclude_keys = pillar['librato'].get('exclude_keys', [])
    counter_keys = pillar['librato'].get('counter_keys', [])

    metric_base = ret['fun']
    source = ret['id']
    gauges = []
    counters = []
    flattened = _flatten_and_collect_floats(ret['return'], base=metric_base)
    for name, value in flattened.items():
        if _matches_pattern(name, exclude_keys):
            continue
        data = {
            'name': name,
            'value': value,
            'source': source,
        }
        if _matches_pattern(name, counter_keys):
            counters.append(data)
        else:
            gauges.append(data)
    if counters:
        _post_to_librato(counters, email, api_token, metric='counters')
    if gauges:
        _post_to_librato(gauges, email, api_token)
