# -*- coding: utf-8 -*-
'''
Salt returner that reports stats to Salmon
(https://github.com/lincolnloop/salmon). The returner will
inspect the payload coercing values into floats where possible.
Text responses will be ignored

Pillar needs something like::

    salmon_returner:
      url: http://salmon.example.com
      api_key: abc1234def
'''

import base64
import fnmatch
import logging
import json
import urllib2

logger = logging.getLogger(__name__)


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


def _post_to_salmon(data, api_key, url):
    url = '{0}/api/v1/metric/'.format(url)
    logger.info("Sending %s metrics to %s", len(data), url)
    payload = json.dumps(data)
    logger.debug("Salmon payload: %s", payload)
    req = urllib2.Request(url, payload,
                          {'Content-Type': 'application/json'})

    encoded = base64.standard_b64encode(api_key)
    req.add_header("Authorization", "Basic {0}".format(encoded))
    try:
        handler = urllib2.urlopen(req)
    except urllib2.HTTPError as exp:
        logger.error("Salmon request failed with code %s", exp.code)
    handler.close()


def _matches_pattern(name, pattern_list):
    for pattern in pattern_list:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def returner(ret):
    pillar = __salt__['pillar.raw']()
    url = pillar['salmon_returner']['url']
    api_key = pillar['salmon_returner']['api_key']
    exclude_keys = pillar['salmon_returner'].get('exclude_keys', [])

    metric_base = ret['fun']
    source = ret['id']
    metrics = []
    flattened = _flatten_and_collect_floats(ret['return'], base=metric_base)
    for name, value in flattened.items():
        if _matches_pattern(name, exclude_keys):
            continue
        data = {
            'name': name,
            'value': value,
            'source': source,
        }
        metrics.append(data)
    _post_to_salmon(metrics, api_key, url)
