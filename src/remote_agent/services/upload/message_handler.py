"""A message handler to upload moblab and dut data to google cloud"""

import logging
from google.protobuf.json_format import MessageToDict

from moblab_common import pubsub_client
from remoteagentrpc_pb2 import MoblabHost, MoblabDut


_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# TODO(chromium:1108631): Will change the topic to prod topic.
_PUBSUB_REMOTE_AGENT_TOPIC = "moblab-remote-console-notification-dev"


class MessageHandler:
    """Class that converts protobuf messages to pubsub messages and publish
       them to the cloud.

    Attributes:
        pubsub_client: A pubsub client based on pubsub_v1.PublisherClient.
    """

    def __init__(self, ):
        self.pubsub_client = pubsub_client.PubSubBasedClient()

    def _create_pubsub_attr(self, proto_msg):
        """Creates a map of attributes to be used in a pubsub message.

        Args:
            proto_msg: A MoblabHost or MoblabDut protobuf message to be converted
                to the format of a python map.

        Returns:
            A map of pubsub message attributes, or None if proto_msg is not an
            instance of MoblabHost or MoblabDut.
        """
        message_type = 'MoblabHost'
        if isinstance(proto_msg, MoblabDut):
            message_type = 'MoblabDut'
        elif not isinstance(proto_msg, MoblabHost):
            _LOGGER.error("Failed to create pubsub attributes map because of "
                          "unknown proto message type: %s", type(proto_msg))
            return None

        attr_map = MessageToDict(proto_msg, preserving_proto_field_name=True)

        # All attributes published to pubsub must be sent as strings.
        # Converts all non-string attributes to strings:
        for key, val in attr_map.items():
            if not isinstance(val, str):
                attr_map[key] = str(val)
        attr_map['moblab_remote_console_message_type'] = message_type
        return attr_map

    def upload_messages(self, proto_msgs):
        """Uploads a list of pubsub messages containing moblab or dut information from
           the given protobuf messages.

        Args:
            proto_msgs: A list of protobuf messages to be converted to a pubsub messages.

        Returns:
            A list of pubsub message ids, and empty if fails.
        """
        if proto_msgs is None:
            return []

        pubsub_msg_attr_maps = []
        for proto_msg in proto_msgs:
            pubsub_attr = self._create_pubsub_attr(proto_msg)
            if pubsub_attr:
                pubsub_msg_attr_maps.append(pubsub_attr)

        return self.pubsub_client.send_messages_with_attributes(
            _PUBSUB_REMOTE_AGENT_TOPIC,
            pubsub_msg_attr_maps,
            b'remote agent logs'
        )
