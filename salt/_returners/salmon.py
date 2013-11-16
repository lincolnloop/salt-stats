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
    url = '{0}/api/v1/metrics'.format(url)
    logger.info("Sending %s to Salmon", len(data))
    req = urllib2.Request(url, json.dumps(data),
                          {'Content-Type': 'application/json'})

    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, url, api_key, '')

    auth_manager = urllib2.HTTPBasicAuthHandler(password_manager)
    opener = urllib2.build_opener(auth_manager)

    urllib2.install_opener(opener)

    handler = urllib2.urlopen(req)
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
