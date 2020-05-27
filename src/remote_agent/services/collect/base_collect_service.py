from abc import ABC, abstractmethod


class BaseCollectService(ABC):

    @abstractmethod
    def collect(self):
        pass
