import datetime

_DEFAULT_MIN_AGE_TO_PRUNE = datetime.timedelta(days=3)


class UploaderConfiguration(object):
    """Holds the dynamic configuration, that can be modified at runtime"""

    def __init__(self):
        self._min_age_to_prune = _DEFAULT_MIN_AGE_TO_PRUNE

    def get_min_age_to_prune(self):
        """Returns the local retention period
        for locally stored results"""
        return self._min_age_to_prune

    def set_min_age_to_prune(self, period: datetime.timedelta):
        """Allows to modify the local retention
        period for locally stored results"""
        self._min_age_to_prune = period
