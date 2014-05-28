"""
Read ElasticSearch stats
http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/cluster-stats.html
http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/cluster-nodes-stats.html

:maintainer: Peter Baumgartner <pete@lincolnloop.com>
:maturity:   new
:platform:   all
"""
import logging
import urllib2

log = logging.getLogger(__name__)

def _build_url(host, port, endpoint):
    return 'http://{0}:{1}{2}'.format(host, port, endpoint)

def _get_url(url):
    log.debug('Opening %s', url)
    with contextlib.closing(urllib2.urlopen(url)) as resp:
        stats_blob = resp.read()
    log.debug('Decoding %s', stats_blob)
    return json.loads(stats_blob)

def cluster_stats(host="localhost", port=9200):
    """
    Return the cluster stats from an ElasticSearch instance.

    host
        The host running ElasticSearch. Defaults to 'localhost'
    port
        The port for ElasticSearch. Defaults to 9200.
    CLI Example::

        salt '*' elasticsearch.cluster_stats
    """
    url = _build_url(host, port, '/_cluster/stats')
    return _get_url(url)

def nodes_stats(host="localhost", port=9200):
    """
    Return the nodes stats from an ElasticSearch instance.

    host
        The host running ElasticSearch. Defaults to 'localhost'
    port
        The port for ElasticSearch. Defaults to 9200.
    CLI Example::

        salt '*' elasticsearch.nodes_stats
    """
    url = _build_url(host, port, '/_cluster/stats')
    return _get_url(url)
