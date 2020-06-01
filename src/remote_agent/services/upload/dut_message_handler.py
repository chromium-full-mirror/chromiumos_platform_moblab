from moblab_common import pubsub_client
import BaseMessageHandler


class DutMessageHandler(BaseMessageHandler):

    def __init__(self, ):
        self.pubsub_client = pubsub_client.PubSubBasedClient()
        pass

    def upload_message(self):
        raise NotImplementedError()
