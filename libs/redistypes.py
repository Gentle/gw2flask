from contextlib import contextmanager
from collections import MutableMapping
import re

import json

import sys
connection = None


def get_redis(**kwargs):
    global connection
    if not connection:
        import redis
        kwargs.setdefault('host', 'localhost')
        kwargs.setdefault('port', 6379)
        kwargs.setdefault('db', 6)
        connection = redis.StrictRedis(**kwargs)
    return connection


class RedisObject(object):

    def __init__(self, separator=":", prefix="$", connection=get_redis()):
        self.connection = connection
        # to separate fields, don't use this in your names
        self.separator = separator
        # internal keys begin with this, don't use this in your names
        self.prefix = prefix

    def _join(self, first, second, internal=False):
        result = unicode(first) + self.separator
        if isinstance(second, list):
            if len(second) > 1:
                result += self.separator.join(second[:-1])
                second = second[-1]
            else:
                second = second[0]
        if internal:
            result += self.prefix
        result += unicode(second)
        return result


class RedisHashSet(RedisObject, MutableMapping):

    def __init__(self, basekey, idkey="pk", *args, **kwargs):
        super(RedisHashSet, self).__init__(*args, **kwargs)
        if isinstance(basekey, basestring):
            self.basekey = basekey
        else:
            if len(basekey) > 1:
                result = basekey[0]
                for item in basekey[1:]:
                    result = self._join(result, item)
            else:
                result = basekey[0]
            self.basekey = result
        self.idkey = self._join(self.basekey, idkey, True)
        # an old implementation had a bug
        # try to keep data for bugged key
        wrongkey = self._join(basekey, idkey, True)
        if self.connection.exists(wrongkey):
            self.connection.rename(wrongkey, self.idkey)

    def _save_dict(self, itemkey, data):
        subkey = self._join(itemkey, 'json', True)
        for (key, value) in data.iteritems():
            if not isinstance(value, basestring):
                self.connection.sadd(subkey, key)
                value = json.dumps(value)
            self.connection.hset(itemkey, key, value)

    def add(self, key, data):
        itemkey = self._join(self.basekey, key)
        self._save_dict(itemkey, data)

    def keys(self):
        return self.connection.smembers(self.idkey)

    def __iter__(self):
        return self.connection.smembers(self.idkey).__iter__()

    def __len__(self):
        return self.connection.scard(self.idkey)

    def sorted(self, field, desc=False, alpha=False):
        by = "%s%s*->%s" % (self.basekey, self.separator, field)
        get = "%s%s*" % (self.basekey, self.separator)
        print "by", by
        print "get", get
        return self.connection.sort(self.idkey,
                                    by=by,
                                    #get=get,
                                    desc=desc,
                                    alpha=alpha)

    def __contains__(self, key):
        return self.connection.sismember(self.idkey, key)

    def __getitem__(self, key):
        if self.connection.sismember(self.idkey, key):
            itemkey = self._join(self.basekey, key)
            if not self.connection.exists(itemkey):
                raise KeyError
            return RedisHash(itemkey,
                             separator=self.separator,
                             prefix=self.prefix,
                             connection=self.connection)
        else:
            raise KeyError

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, data):
        itemkey = self._join(self.basekey, key)
        self._save_dict(itemkey, data)
        self.connection.sadd(self.idkey, key)

    def __delitem__(self, key):
        itemkey = self._join(self.basekey, key)
        item = RedisHash(itemkey)
        item.delete()
        self.connection.srem(self.idkey, key)

    def add_index(self, field):
        indexbasekey = self._join(self.basekey, "index", True)


    def find(self, **kwargs):
        for id, row in self.iteritems():
            good = True
            for key in kwargs:
                if not key in row \
                or not kwargs[key] == row[key]:
                    good = False
                    break
            if good:
                yield row

class RedisHashSetQuery(object):

    def __init__(self, hashset):
        self.hashset = hashset

    def all():
        for key in self.hashset:
            pass


class RedisHash(RedisObject):

    def __init__(self, key, *args, **kwargs):
        super(RedisHash, self).__init__(*args, **kwargs)
        self.key = key
        self.jsonkey = self._join(self.key, 'json', True)

    def _as_dict(self):
        data = self.connection.hgetall(self.key)
        for key in self.connection.smembers(self.jsonkey):
            data[key] = json.loads(data[key])
        return data

    def _save(self, **kwargs):
        for (key, value) in kwargs.iteritems():
            if isinstance(value, basestring):
                fn = self.connection.srem
            else:
                fn = self.connection.sadd
                value = json.dumps(value)
            self.connection.hset(self.key, key, value)
            fn(self.jsonkey, key)

    @property
    def dict(self):
        data = self._as_dict()
        return data

    def __getitem__(self, key):
        result = self.connection.hget(self.key, key)
        if result is not None:
            if self.connection.sismember(self.jsonkey, key):
                result = json.loads(result)
            return result
        raise KeyError

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __setitem__(self, key, value):
        self._save(**{key: value})

    def __delitem__(self, key):
        self.connection.hdel(self.key, key)

    def __iter__(self):
        return self.connection.hkeys(self.key).__iter__()

    def __contains__(self, key):
        return key in self.connection.hkeys(self.key)

    def delete(self):
        self.connection.delete(self.key)
        self.connection.delete(self.jsonkey)


def progress(now, final):
    numlen = len(str(final))
    current = str(now).rjust(numlen)
    sys.stdout.write('%s/%s' % (current, final))
    sys.stdout.flush()
    if now == final:
        sys.stdout.write('\n')
    else:
        sys.stdout.write('\b' * (numlen * 2 + 1))


def migrate(key):
    h = RedisHashSet(key)
    ure = re.compile(r"u'.*'")
    sys.stdout.write("migrating %s\n" % (h.basekey))
    sys.stdout.flush()
    size = len(h)
    for (i, itemkey) in enumerate(h, start=1):
        progress(i, size)
        item = h[itemkey]
        for key in item:
            value = item[key]
            if not isinstance(value, basestring):
                continue
            match = ure.search(value)
            if match:
                try:
                    data = eval(value)
                    if isinstance(data, list) or isinstance(data, dict):
                        item[key] = data
                except:
                    pass
