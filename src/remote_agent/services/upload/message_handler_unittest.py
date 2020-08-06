"""Unit tests for message_handler module"""

from unittest import TestCase, main
from unittest.mock import patch

from remote_agent.remoteagentrpc_pb2 import MoblabHost, MoblabDut, DutStatus, DiskStats
import message_handler
# pylint: disable=missing-function-docstring
# pylint: disable=no-member


class MessageHandlerTest(TestCase):
    """Unit tests for MessageHandler class."""

    TEST_DUT_STATUS = 'DUT_STATUS_READY'
    TEST_HOST_ID = 'host_id'

    def _create_moblab_proto_msg(self, moblab_host_id_str, milestone_int,
                                 total_disk_size_bytes_int):
        moblab_proto_msg = MoblabHost()
        moblab_proto_msg.moblab_host_id = moblab_host_id_str
        moblab_proto_msg.milestone = milestone_int
        moblab_proto_msg.disk_stats.total_disk_size_bytes = total_disk_size_bytes_int
        return moblab_proto_msg

    def _create_dut_proto_msg(self, status_str, is_locked_bool, label_list):
        dut_proto_msg = MoblabDut()
        dut_proto_msg.status = DutStatus.Value(status_str)
        dut_proto_msg.is_locked = is_locked_bool
        dut_proto_msg.label.extend(label_list)
        return dut_proto_msg

    def _create_expected_map_moblab(self, moblab_host_id_str, milestone_as_str,
                                    total_disk_size_bytes_as_str):
        return {
            'moblab_host_id': moblab_host_id_str,
            'milestone': milestone_as_str,
            'disk_stats': "{'total_disk_size_bytes': '" + total_disk_size_bytes_as_str + "'}",
            'moblab_remote_console_message_type': 'MoblabHost'
        }

    def _create_expected_map_dut(self, status_str, is_locked_bool_as_str, label_list_as_str):
        return {
            'status': status_str,
            'is_locked': is_locked_bool_as_str,
            'label': label_list_as_str,
            'moblab_remote_console_message_type': 'MoblabDut'
        }

    def setUp(self):
        self.pubsub_client_patcher = patch('message_handler.pubsub_client.PubSubBasedClient')
        self.pubsub_client_mock = self.pubsub_client_patcher.start()

        self.test_handler = message_handler.MessageHandler()

        self.topic = "moblab-remote-console-notification-dev"
        self.data = b'remote agent logs'

    def test_upload_messages_converts_non_str_attr_to_str(self):
        moblab_proto_msg = self._create_moblab_proto_msg(
            moblab_host_id_str=self.TEST_HOST_ID,
            milestone_int=80,
            total_disk_size_bytes_int=100
        )
        dut_proto_msg = self._create_dut_proto_msg(
            status_str=self.TEST_DUT_STATUS,
            is_locked_bool=True,
            label_list=['board:octopus', 'model:caroline']
        )
        expected_map_moblab = self._create_expected_map_moblab(
            moblab_host_id_str=self.TEST_HOST_ID,
            milestone_as_str='80',
            total_disk_size_bytes_as_str='100',
        )
        expected_map_dut = self._create_expected_map_dut(
            status_str=self.TEST_DUT_STATUS,
            is_locked_bool_as_str='True',
            label_list_as_str="['board:octopus', 'model:caroline']"
        )
        expected_attr_maps = [expected_map_moblab, expected_map_dut]

        self.test_handler.upload_messages([moblab_proto_msg, dut_proto_msg])

        self.pubsub_client_mock.return_value.send_messages_with_attributes. \
            assert_called_with(self.topic, expected_attr_maps, self.data)

    def test_upload_messages_removes_wrong_type_proto_msg(self):
        moblab_proto_msg = self._create_moblab_proto_msg(
            moblab_host_id_str=self.TEST_HOST_ID,
            milestone_int=80,
            total_disk_size_bytes_int=100
        )
        expected_map_moblab = self._create_expected_map_moblab(
            moblab_host_id_str=self.TEST_HOST_ID,
            milestone_as_str='80',
            total_disk_size_bytes_as_str='100',
        )
        expected_attr_maps = [expected_map_moblab]

        with self.assertLogs('message_handler', level='INFO') as log:
            self.test_handler.upload_messages([DiskStats(), moblab_proto_msg])

        self.pubsub_client_mock.return_value.send_messages_with_attributes. \
            assert_called_with(self.topic, expected_attr_maps, self.data)
        self.assertIn("Failed to create pubsub attributes map because of "
                      "unknown proto message type", log.output[0])

    def test_upload_messages_returns_empty_list_with_none_input(self):
        msg_ids = self.test_handler.upload_messages(None)
        self.assertEqual(msg_ids, [])

if __name__ == '__main__':
    main()
