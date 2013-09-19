salt-stats
==========

A collection of modules for collecting stats

Usage
-----

Clone the repo to your Salt master and adjust `file_roots` in `/etc/salt/master`.

```
file_roots:
  base:
    - /srv/salt
    - /path/to/salt-stats/salt
```

Modules
-------

* [memcached.stats](https://github.com/lincolnloop/salt-stats/blob/master/salt/_modules/memcached.py)
* [nginx.status](https://github.com/lincolnloop/salt-stats/blob/master/salt/_modules/nginx.py)
* [redis.info](https://github.com/lincolnloop/salt-stats/blob/master/salt/_modules/redis.py)
* [uwsgi.stats](https://github.com/lincolnloop/salt-stats/blob/master/salt/_modules/uwsgi.py)

Returners
---------

* [librato](https://github.com/lincolnloop/salt-stats/blob/master/salt/_returners/librato.py)
