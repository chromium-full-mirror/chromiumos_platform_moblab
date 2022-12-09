from unittest import IsolatedAsyncioTestCase

from cache import Cache
import time


def compute_to_1():
    return 1

def compute_to_2():
    return 2

def compute_to_3():
    return 3


class CacheTest(IsolatedAsyncioTestCase):
    """
    Testing the cache code.
    """

    def test_can_get_from_default_value(self):
        """
        Testing get data from default function,
        because the cache is fresh.
        """
        c = Cache()
        KEY = 1

        # As the cache is empty now, it triggers the `or_default`
        # immediately. We get the value `1` now.
        res = c.get(KEY, or_default=compute_to_1)
        assert(res == 1)

    def test_can_get_from_cache_data(self):
        """
        Testing get data from the cache. 
        """
        c = Cache(delay=5)
        KEY = 1

        # As the cache is empty now, it triggers the `or_default`
        # immediately. We get the value `1` now.
        res = c.get(KEY, or_default=compute_to_1)
        assert(res == 1)
        # As the default delay is 5s, the cache won't update within
        # 5s. We get the old value from cache is `1`, and the cache
        # keeps the `1` and won't update.
        res = c.get(KEY, or_default=compute_to_2)
        assert(res == 1)

        time.sleep(5.5)
        # Get the value again. We get the old value `1` from cache.
        # As the delay is reached, the cache update the value to `2` for KEY.
        res = c.get(KEY, or_default=compute_to_2)
        assert(res == 1)

    def test_should_refresh_in_background_when_force_updated_is_true(self):
        """
        Testing should update data in background
        when conditions are reached.
        """
        # Arrange - Setup a cache with 60s delay, it means the cache
        # will keep the old value for 60s. Within 60s, the cache only
        # return the value, which is set by first time.
        c = Cache(delay=60)
        KEY = 1

        # As the cache doesn't store any value for KEY.
        # It will execute a default function first, and then
        # set a value for KEY. After that, it returns value.
        res = c.get(KEY, or_default=compute_to_1)
        assert(res == 1)
        # As the value is updated/set within 60s(delay), the
        # cache won't update, so it always keeps the old value
        # and don't refresh the cache.
        for _ in range(0, 5):
            res = c.get(KEY, or_default=compute_to_2)
            assert(res == 1)
        # The test is for setting `force_udpate` to True,
        # the cache should update immediately.
        res = c.get(KEY, or_default=compute_to_2, force_update=True)
        assert(res == 2)
        

    def test_should_refresh_in_background_when_delay_is_reached(self):
        """
        Testing should update data in background
        when conditions are reached.
        """
        c = Cache(delay=5)
        KEY = 1

        # As the cache doesn't store any value for KEY.
        # It will execute a default function first, and then
        # set a value for KEY. After that, it returns value.
        res = c.get(KEY, or_default=compute_to_1)
        assert(res == 1)
        # As the value is updated/set within 5s(delay), the
        # cache won't update, it always keeps the old value
        # and don't refresh the cache.
        for _ in range(0, 5):
            res = c.get(KEY, or_default=compute_to_2)
            assert(res == 1)

        # Simulate keeping the cache over the delay.
        time.sleep(5.5)
        # After over 5s(delay, when the user gets the cache again
        # it returns the old value first, and updates the cache
        # in background, when user gets it again, it should return
        # the new value.
        res = c.get(KEY, or_default=compute_to_2)
        assert(res == 1)
        # Even though, we give the `or_default` returns `3`,
        # but the value sholud be the cache `2`. As the delay
        # isn't reached, the cache won't update, it keeps `2`
        res = c.get(KEY, or_default=compute_to_3)
        assert(res == 2)

        time.sleep(5.5)
        # We get the old value from cache, and then as the
        # delay is reached, the cache updates to `3` now.
        res = c.get(KEY, or_default=compute_to_3)
        assert(res == 2)
        res = c.get(KEY, or_default=compute_to_3)
        assert(res == 3)

    def test_should_refresh_when_ttl_is_reached(self):
        """
        Testing should update data in background
        and return the value
        """

        # Arrange the cache with delay 60s, and ttl 3s.
        c = Cache(delay=60, ttl=3)
        KEY = 1

        # As the cache is empty, it returns the value
        # and updates the value to cache immediately.
        res = c.get(KEY, or_default=compute_to_1)
        assert(res == 1)

        # Make a sleep over ttl limitation, the cache
        # sholud be gone.
        time.sleep(3.5)

        # test the cache is exist, if it is exit, it
        # should return `1`, not the new value `2`.
        res = c.get(KEY, or_default=compute_to_2)
        assert(res == 2)

    def test_should_not_refresh_in_background(self):
        """
        Testing shouldn't update data in background
        when the conditions aren't reached.
        """
        c = Cache(delay=60)
        KEY = 1

        # As the cache is empty, it returns the value
        # and updates the value to cache immediately.
        res = c.get(KEY, or_default=compute_to_1)
        assert(res == 1)
        # As the value is updated/set within 60s(delay), the
        # cache won't update, it always keeps the old value
        # and don't refresh the cache.
        for _ in range(0, 10):
            res = c.get(KEY, or_default=compute_to_2)
            assert(res == 1)
            time.sleep(1)

    def test_should_get_the_value_when_the_cache_is_cleared(self):
        """
        Testing should upate and return the value when the cache is cleared
        """
        c = Cache(delay=60)
        KEY = 1

        # As the cache is empty, it returns the value
        # and updates the value to cache immediately.
        res = c.get(KEY, or_default=compute_to_1)
        assert(res == 1)
        c.clear()
        res = c.get(KEY, or_default=compute_to_2)
        assert(res == 2)

    def test_should_get_none_when_or_default_is_none(self):
        """
        Testing the cache without `or_default` function.
        """
        c = Cache(delay=5)
        KEY = 1
        res = c.get(KEY)
        assert(res is None)


    def test_should_return_cache_value_when_or_default_is_set_at_least_one(self):
        """
        Testing the cache set the value at least one.
        """
        c = Cache()
        KEY = 1

        # As the cache is empty, it returns the value
        # and updates the value to cache immediately.
        res = c.get(KEY, or_default=compute_to_1)
        assert(res == 1)

        # As the `or_default` function is None,
        # but the value is set before, so it will
        # return the cache data.
        res = c.get(KEY)
        assert(res == 1)

    def test_should_return_none_when_or_default_is_none_and_cached_data_is_expired(self):
        """
        Testing the cached data is expired and without `or_default` function
        """
        c = Cache(ttl=3)
        KEY = 1

        # As the cache is empty, it returns the value
        # and updates the value to cache immediately.
        res = c.get(KEY, or_default=compute_to_1)
        assert(res == 1)

        time.sleep(3.5)
        # As the cache is expired and without `or_default`
        # the value should be None.
        res = c.get(KEY)
        assert(res is None)

        

