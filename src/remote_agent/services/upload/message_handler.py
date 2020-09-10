"""A message handler to upload moblab and dut data to google cloud"""

import logging
from google.protobuf.json_format import MessageToDict
from google.cloud import pubsub_v1

from moblab_common import pubsub_client
from moblab_common.proto.remoteagentrpc_pb2 import MoblabHost, MoblabDut
from constants import Constants


_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# TODO(chromium:1113472): Enable the switch between dev and prod pubsub topics
# based on the .env parameter.
_PUBSUB_REMOTE_AGENT_TOPIC = 'moblab-remote-console-notification'


class MessageHandler(Constants):
    """Class that converts protobuf messages to pubsub messages and publish
       them to the cloud.

    Attributes:
        pubsub_client: A pubsub client based on pubsub_v1.PublisherClient.
    """

    def __init__(self, max_messages=30, max_bytes=8000, max_latency=3):
        batch_settings = pubsub_v1.types.BatchSettings(
            max_messages=max_messages,
            max_bytes=max_bytes,
            max_latency=max_latency,
        )
        self.pubsub_client = pubsub_client.PubSubBasedClient(batch_settings=batch_settings)

    def _create_pubsub_attr(self, proto_msg, attr_type):
        """Creates a map of attributes to be used in a pubsub message.

        Args:
            proto_msg: A MoblabHost or MoblabDut protobuf message to be converted
                to the format of a python map.
            attr_type: A string representing the attribute type of the data to be
                uploaded. Attribute types include 'MOBLAB_BASIC', 'DISK', 'NETWORK',
                'DUT_BASIC', and 'DUT_STATUS'.

        Returns:
            A map of pubsub message attributes, or None 1) if proto_msg is not an
            instance of MoblabHost or MoblabDut or 2) if attrbute type is 'DUT_STATUS'
            but the given dut status is unrecognizable.
        """
        message_type = 'MoblabHost'
        if isinstance(proto_msg, MoblabDut):
            message_type = 'MoblabDut'
        elif not isinstance(proto_msg, MoblabHost):
            _LOGGER.error("Failed to create pubsub attributes map because of "
                          "unknown proto message type: %s", type(proto_msg))
            return None

        attr_map = MessageToDict(proto_msg, preserving_proto_field_name=True)

        if attr_type == self.DUT_STATUS:
            try:
                attr_map[self.STATUS] = self._reformat_dut_status(attr_map[self.STATUS])
            except IndexError:
                _LOGGER.exception('DutStatus does not have enum value: %s.', attr_map[self.STATUS])
                return None

        # All attributes published to pubsub must be sent as strings.
        # Converts all non-string attributes to strings:
        for key, val in attr_map.items():
            if not isinstance(val, str):
                if isinstance(val, dict):
                    attr_map[key] = self._map_to_str(val)
                else:
                    attr_map[key] = str(val)
        attr_map['moblab_remote_console_message_type'] = message_type
        return attr_map

    def _reformat_dut_status(self, dut_status):
        """Remove the prefix of the given dut status and convert it to lower case.

        For example: 'DUT_STATUS_REPAIR_FAILED' will be converted to 'repair_failed'.

        Args:
            dut_status: A string representing the value of the 'status' field of MoblabDut
                proto message.

        Returns:
            A string representing the dut status without prefix and in lower case.

        Raises:
            IndexError if the given dut status has wrong format.
        """
        status_splitted = dut_status.lower().split('_')
        try:
            result = status_splitted[2]
            for index in range(3, len(status_splitted)):
                result += ('_' + status_splitted[index])
            return result
        except IndexError:
            _LOGGER.exception('Failed to parse dut status, %s, because it has wrong format.',
                              dut_status)
            raise

    def _map_to_str(self, subattr_map):
        """Converts a python map to a semicolon-separated string.

        For example: {'key1': 'string', 'key2': 10} will be converted to 'key1: string; key2: 10'.

        Args:
            subattr_map: A python map representing some subattributes of a proto message.

        Returns:
            A semicolon-separated string representing some subattributes of a proto message.
        """
        result = ''
        for key, val in subattr_map.items():
            result += (key + ': ' + str(val) + '; ')
        if len(result) > 2:
            result = result[:-2]
        return result

    def upload_messages(self, proto_msgs, attr_type):
        """Uploads a list of pubsub messages containing moblab or dut information from
           the given protobuf messages.

        Args:
            proto_msgs: A list of protobuf messages to be converted to a pubsub messages.
            attr_type: A string representing the attribute type of the data to be
                uploaded. Attribute types include 'MOBLAB_BASIC', 'DISK', 'NETWORK',
                'DUT_BASIC', and 'DUT_STATUS'.

        Returns:
            A list of pubsub message ids, and empty if fails.
        """
        if proto_msgs is None:
            return []

        pubsub_msg_attr_maps = []
        for proto_msg in proto_msgs:
            pubsub_attr = self._create_pubsub_attr(proto_msg, attr_type)
            if pubsub_attr:
                pubsub_msg_attr_maps.append(pubsub_attr)

        return self.pubsub_client.send_messages_with_attributes(
            _PUBSUB_REMOTE_AGENT_TOPIC,
            pubsub_msg_attr_maps,
            b'remote agent logs'
        )
