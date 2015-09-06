import os
import pickle
import zlib

from cachetools import LFUCache

from pycrest.eve import APICache


class FileCache(APICache):
    def __init__(self, path):
        self._cache = LFUCache(maxsize=512)
        self.path = path
        if not os.path.isdir(self.path):
            os.mkdir(self.path, 0o700)

    def _getpath(self, key):
        return os.path.join(self.path, str(hash(key)) + '.cache')

    def put(self, key, value):
        with open(self._getpath(key), 'wb') as f:
            f.write(zlib.compress(pickle.dumps(value, -1)))
        self._cache[key] = value

    def get(self, key):
        if key in self._cache:
            return self._cache[key]

        try:
            with open(self._getpath(key), 'rb') as f:
                return pickle.loads(zlib.decompress(f.read()))
        except IOError as ex:
            if ex.errno == 2:  # file does not exist (yet)
                return None
            else:
                raise

    def invalidate(self, key):
        self._cache.pop(key, None)

        try:
            os.unlink(self._getpath(key))
        except OSError as ex:
            if ex.errno == 2:  # does not exist
                pass
            else:
                raise
