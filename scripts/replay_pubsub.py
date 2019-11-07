#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from __future__ import print_function

import argparse
import os
import re
import sys
from datetime import datetime, timedelta, tzinfo

# pylint: disable=no-name-in-module, import-error
from google.cloud import storage

from moblab_common import pubsub_client

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS",
                      "%s/.service_account.json" % os.environ["HOME"])


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
        console_client = pubsub_client.PubSubBasedClient()
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
