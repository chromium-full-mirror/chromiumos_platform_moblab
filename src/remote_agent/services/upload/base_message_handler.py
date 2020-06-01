from abc import ABC, abstractmethod


class BaseMessageHandler(ABC):

    @abstractmethod
    def upload_message(self):
        pass
