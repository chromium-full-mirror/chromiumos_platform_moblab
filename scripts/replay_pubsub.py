#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from __future__ import print_function

import argparse
import base64
import logging
import os
import re
import sys

from datetime import datetime, timedelta, tzinfo

# pylint: disable=no-name-in-module, import-error
from google.cloud import pubsub_v1, storage


os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS",
                      "%s/.service_account.json" % os.environ["HOME"])

_PUBSUB_TOPIC = "moblab-notification"

# Current notification version.
CURRENT_MESSAGE_VERSION = '1'

# Test upload pubsub notification attributes
LEGACY_ATTR_VERSION = 'version'
LEGACY_ATTR_GCS_URI = 'gcs_uri'
LEGACY_ATTR_MOBLAB_MAC = 'moblab_mac_address'
LEGACY_ATTR_MOBLAB_ID = 'moblab_id'
# the message data for new test result notification.
LEGACY_TEST_OFFLOAD_MESSAGE = 'NEW_TEST_RESULT'


class PubSubException(Exception):
    """Exception to be raised when the test to push to prod failed."""
    pass


def callback(message_future):
    # When timeout is unspecified, the exception method waits indefinitely.
    if message_future.exception(timeout=30):
        raise PubSubException(
            'Publishing message on {} threw an Exception {}.'.format(
                "Moblab notifications", message_future.exception()))
    else:
        logging.info(message_future.result())


class PubSubClient(object):
    """A generic pubsub client."""

    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()

    def publish_notifications(self, topic, messages=None):
        """Publishes a test result notification to a given pubsub topic.

        @param topic: The Cloud pubsub topic.
        @param messages: A list of notification messages.

        @returns A list of pubsub message ids, and empty if fails.

        @raises PubSubException if failed to publish the notification.
        """
        topic_path = self.publisher.topic_path("chromeos-partner-moblab", topic)
        for message in messages:
            resp = self.publisher.publish(topic_path, message['data'],
                                          **message['attributes'])
            resp.add_done_callback(callback)


class PubSubBasedClient(object):
    """A Cloud PubSub based implementation of the CloudConsoleClient interface.
    """

    def __init__(self):
        """Constructor.

        @param credential: The service account credential filename. Default to
            '/home/moblab/.service_account.json'.
        @param pubsub_topic: The cloud pubsub topic name to use.
        """
        self.pubsub_client = PubSubClient()

    def _create_message(self, data, msg_attributes):
        """Creates a cloud pubsub notification object.

        @param data: The message data as a string.
        @param msg_attributes: The message attribute map.

        @returns: A pubsub message object with data and attributes.
        """
        message = {}
        if data:
            message['data'] = data
        if msg_attributes:
            message['attributes'] = msg_attributes
        return message

    def _create_test_job_offloaded_message(self, gcs_uri, serial_number,
                                           moblab_id):
        """Construct a test result notification.

        TODO(ntang): switch LEGACY to new message format.
        @param gcs_uri: The test result Google Cloud Storage URI.

        @returns The notification message.
        """
        data = base64.b64encode(LEGACY_TEST_OFFLOAD_MESSAGE)
        msg_attributes = {}
        msg_attributes[LEGACY_ATTR_VERSION] = CURRENT_MESSAGE_VERSION
        msg_attributes[LEGACY_ATTR_MOBLAB_MAC] = serial_number
        msg_attributes[LEGACY_ATTR_MOBLAB_ID] = moblab_id
        msg_attributes[LEGACY_ATTR_GCS_URI] = gcs_uri

        return self._create_message(data, msg_attributes)

    def send_test_job_offloaded_message(self, gcs_uri, serial_number,
                                        moblab_id):
        """Notify the cloud console a test job is offloaded.

        @param gcs_uri: The test result Google Cloud Storage URI.

        @returns True if the notification is successfully sent.
            Otherwise, False.
        """
        logging.info('Notification on gcs_uri %s', gcs_uri)
        message = self._create_test_job_offloaded_message(
            gcs_uri, serial_number, moblab_id)
        return self.pubsub_client.publish_notifications(_PUBSUB_TOPIC, [message])


ZERO = timedelta(0)
class UTCtzinfo(tzinfo):

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


class ReplayMoblabNotification(object):

    def __init__(self, moblab_bucket_name):
        self.moblab_bucket_name = moblab_bucket_name
        self.storage_client = storage.Client()
        self.utc = UTCtzinfo()

    def get_partial_object_path(self, prefix, _):
        blob_itr = self.storage_client.bucket(
            self.moblab_bucket_name).list_blobs(prefix=prefix)
        # pylint: disable=pointless-statement
        #start = datetime(year=2019, month=4, day=26, hour=15, tzinfo=self.utc)
        #end = datetime(
        #    year=2019, month=4, day=28, hour=12, minute=32, tzinfo=self.utc)

        results = []
        for blob in blob_itr:
            if ("job.serialize" in blob.name):
                print(".", end='')
                sys.stdout.flush()
            if ("job.serialize" in blob.name and "moblab" in blob.name):
                #and start < blob.time_created < end):
                yield (blob.name)

    def run(self, extra_prefix=""):
        console_client = PubSubBasedClient()
        for gsuri in self.get_partial_object_path("results/%s" % extra_prefix,
                                                  "-moblab"):
            match = re.match(r'results/(.*)/(.*)/(.*)-moblab/.*', gsuri)
            gsuri = "gs://%s/results/%s/%s/%s-moblab" % (
                self.moblab_bucket_name, match.group(1), match.group(2),
                match.group(3))
            serial = match.group(1)
            moblab_id = match.group(2)
            print(gsuri, serial, moblab_id)
            console_client.send_test_job_offloaded_message(
                gsuri, serial, moblab_id)


def _parse_arguments(argv):
    """Creates the argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-b',
        '--bucket_name',
        type=str,
        default=None,
        help='What partners bucket to create commands in.')
    parser.add_argument(
        '-p', '--prefix', type=str, default="", help='Serial/id prefix.')
    return parser.parse_args(argv)


def main(args):
    cmd_arguments = _parse_arguments(args)
    cli = ReplayMoblabNotification(cmd_arguments.bucket_name)
    cli.run(cmd_arguments.prefix)


if __name__ == "__main__":
    main(sys.argv[1:])
