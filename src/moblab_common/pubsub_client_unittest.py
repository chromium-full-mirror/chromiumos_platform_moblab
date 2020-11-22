"""Unit tests for pubsub_client module"""

from unittest import TestCase, main
from unittest.mock import patch
from google.cloud.pubsub_v1.publisher.futures import Future

import pubsub_client

# pylint: disable=missing-function-docstring


class PubSubBasedClientTest(TestCase):
    """Unit tests for PubSubBasedClient class."""

    DUT_ATTR_ONE = {"moblab_dut_id": "id_one", "status": "DUT_STATUS_READY"}
    DUT_ATTR_TWO = {"moblab_dut_id": "id_two", "status": "DUT_STATUS_RUNNING"}

    def _initialize_publish_inputs(
        self,
        msg_attributes_list=[DUT_ATTR_ONE],
        pubsub_topic="test_topic",
        data=b"test data",
    ):
        self.msg_attributes_list = msg_attributes_list
        self.pubsub_topic = pubsub_topic
        self.data = data

    def _mock_publish_attributes(
        self, topic_path="test_topic_path", pubsub_msg_id="test_msg_id"
    ):
        self.mock_publisher_client.return_value.topic_path.return_value = (
            topic_path
        )
        test_future = Future()
        test_future.set_result(pubsub_msg_id)
        self.mock_publisher_client.return_value.publish.return_value = (
            test_future
        )

    def setUp(self):
        self.publisher_client_patcher = patch(
            "pubsub_client.pubsub_v1.PublisherClient"
        )
        self.mock_publisher_client = self.publisher_client_patcher.start()
        self.test_pubsub_based_client = pubsub_client.PubSubBasedClient()

    def tearDown(self):
        self.publisher_client_patcher.stop()

    @patch("pubsub_client.PubSubClient.publish_notifications")
    def test_send_messages_with_attributes_creates_correct_msgs(
        self, mock_publish_notifs
    ):
        msg_attributes_list = [self.DUT_ATTR_ONE, self.DUT_ATTR_TWO]
        self._initialize_publish_inputs(
            msg_attributes_list=msg_attributes_list
        )
        expected_msgs = [
            {"data": self.data, "attributes": self.DUT_ATTR_ONE},
            {"data": self.data, "attributes": self.DUT_ATTR_TWO},
        ]

        self.test_pubsub_based_client.send_messages_with_attributes(
            self.pubsub_topic, self.msg_attributes_list, self.data
        )

        mock_publish_notifs.assert_called_with(
            self.pubsub_topic, expected_msgs
        )

    @patch("pubsub_client.callback")
    def test_send_messages_with_attributes_succeeds_with_two_msgs(
        self, mock_callback
    ):
        self._mock_publish_attributes()
        msg_attributes_list = [self.DUT_ATTR_ONE, self.DUT_ATTR_TWO]
        self._initialize_publish_inputs(
            msg_attributes_list=msg_attributes_list
        )

        msg_ids = self.test_pubsub_based_client.send_messages_with_attributes(
            self.pubsub_topic, self.msg_attributes_list, self.data
        )

        self.assertEqual(len(msg_ids), 2)
        self.assertEqual(msg_ids[0], "test_msg_id")

    def test_send_messages_with_attributes_returns_empty_list_with_empty_msg_attributes_list(
        self,
    ):
        self._mock_publish_attributes()
        self._initialize_publish_inputs(msg_attributes_list=[])

        msg_ids = self.test_pubsub_based_client.send_messages_with_attributes(
            self.pubsub_topic, self.msg_attributes_list, self.data
        )

        self.assertEqual(msg_ids, [])

    def test_send_messages_with_attributes_fails_with_none_data(self):
        self._mock_publish_attributes()
        self._initialize_publish_inputs(data=None)

        with self.assertRaises(KeyError):
            self.test_pubsub_based_client.send_messages_with_attributes(
                self.pubsub_topic, self.msg_attributes_list, self.data
            )


if __name__ == "__main__":
    main()
