import threading
import time
from cachetools import TTLCache

_ONE_DAY = 24 * 60 * 60
_ONE_MINUTE = 60

class Cache:
    def __init__(self,maxsize=20, delay=_ONE_MINUTE, ttl=_ONE_DAY):
        self.delay = delay
        self.data = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key: int, or_default=None, force_update=False):
        res = self.data.get(key, None)

        if or_default:
            if res is None or force_update:
                res = self._refresh(key, force_update=True, or_default=or_default)
            else:
                job = threading.Thread(target=self._refresh, args=(key, or_default, False))
                job.start()

        return res[0] if res else None

    def clear(self):
        self.data.clear()

    def _refresh(self, key: int, or_default, force_update=False):
        # should update consider three things.
        # 1. force_update: if force_update is True, it should update the cache.
        # 2. time: if last_update_time is `None` or now - last_update_time > delay, it should update the cache.
        # 3. data: if data is None, it should update the cache.
        data_from_cache = self.data.get(key, None)
        is_data_expired = data_from_cache is None or (data_from_cache and (time.time() - data_from_cache[1]) > self.delay)
        should_udpate = force_update or is_data_expired
        res = (None, None)
        if should_udpate:
            res = (or_default(), time.time())
            self.data[key] = res

        return res
