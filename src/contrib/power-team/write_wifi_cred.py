#!/usr/bin/python2
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
This is a simple tool to write WiFi credentials into stateful.tgz in moblab
cache or into the cloud. Upon provisioning, the DUT will load this WiFi
credential and connect to the moblab access point over WiFi.
"""

from __future__ import print_function
import argparse
import datetime
import os
import shutil
import shlex
import subprocess
import sys
import tempfile

_CACHE = "cache"
_CACHE_DIR = "/mnt/moblab/static/"
_CLOUD = "cloud"
_DEST = [_CACHE, _CLOUD]
_STATEFUL = "stateful.tgz"
_WIFI_CRED = "dev_image_new/etc/wifi_cred"
_CLOUD_LOC_PATH = "/usr/local/autotest/shadow_config.ini"


def _write_wifi_cred_to_tgz(tgz_dir, ssid, pw=None):
    """Write WiFi credentials to downloaded stateful.tgz.

    Args:
        tgz_dir: directory where stateful.tgz is at.
        ssid: WiFi SSID in string.
        pw: WiFi password in string, optional.
    """

    # Create a working directory.
    start_ts = datetime.datetime.now()
    work_dir = os.path.join(
        tempfile.gettempdir(), "tgz%s" % start_ts.strftime("%Y%m%d%H%M%S")
    )
    os.mkdir(work_dir)

    try:
        # Untar stateful.tgz into working directory.
        tgz_path = os.path.join(tgz_dir, _STATEFUL)
        cmd = "tar --directory=%s -xvzf %s" % (work_dir, tgz_path)
        subprocess.check_output(shlex.split(cmd))
        extract_ts = datetime.datetime.now()
        delta_sec = (extract_ts - start_ts).total_seconds()
        print("Extract took %f seconds." % delta_sec)

        # Write WiFi credentials into the unpacked stateful.tgz in working
        # directory.
        wifi_cred = ssid + "\n"
        if pw:
            wifi_cred += pw + "\n"
        wifi_cred_path = os.path.join(work_dir, _WIFI_CRED)
        with open(wifi_cred_path, "w") as wifi_cred_file:
            wifi_cred_file.write(wifi_cred)

        # Tar stateful.tgz into tgz directory again.
        cmd = "tar -czvf %s --directory=%s %s" % (
            tgz_path,
            work_dir,
            " ".join(os.listdir(work_dir)),
        )
        subprocess.check_output(shlex.split(cmd))
        compress_ts = datetime.datetime.now()
        delta_sec = (compress_ts - extract_ts).total_seconds()
        print("Compress took %f seconds." % delta_sec)

        shutil.rmtree(work_dir)

    except:
        # In case of exception, make sure that working directory is deleted.
        shutil.rmtree(work_dir)
        raise


def write_wifi_cred_to_cache(builder, version, ssid, pw=None):
    """Write WiFi credentials to stateful.tgz in cache.

    Args:
        builder: builder name in string, eg. nocturne-release.
        version: OS version in string, eg. R76-12202.0.0.
        ssid: WiFi SSID in string.
        pw: WiFi password in string, optional.
    """
    cache_dir = os.path.join(_CACHE_DIR, builder, version)
    _write_wifi_cred_to_tgz(cache_dir, ssid, pw)


def get_cloud_location():
    """Get the gs cloud location for the current moblab setup.

    Returns:
        gs cloud location in string.
    """
    with open(_CLOUD_LOC_PATH, "r") as f:
        for line in f.readlines():
            if line.startswith("image_storage_server"):
                return line.split(" = ")[1].strip()


def write_wifi_cred_to_cloud(builder, version, ssid, pw=None):
    """Write WiFi credentials to stateful.tgz in cache.

    Args:
        builder: builder name in string, eg. nocturne-release.
        version: OS version in string, eg. R76-12202.0.0.
        ssid: WiFi SSID in string.
        pw: WiFi password in string, optional.
    """
    # Create a temporary cache directory.
    start_ts = datetime.datetime.now()
    tmp_cache_dir = os.path.join(
        tempfile.gettempdir(),
        "cache%s" % start_ts.strftime("%Y%m%d%H%M%S"),
        "",
    )
    os.mkdir(tmp_cache_dir)

    try:
        cloud_tgz_dir = os.path.join(
            get_cloud_location(), builder, version, ""
        )
        print("Cloud directory: %s" % cloud_tgz_dir)
        cmd = "gsutil -m cp %s %s" % (
            os.path.join(cloud_tgz_dir, _STATEFUL),
            tmp_cache_dir,
        )
        subprocess.check_output(shlex.split(cmd))
        download_ts = datetime.datetime.now()
        delta_sec = (download_ts - start_ts).total_seconds()
        print("Download took %f seconds." % delta_sec)

        _write_wifi_cred_to_tgz(tmp_cache_dir, ssid, pw)

        start_ts = datetime.datetime.now()
        cmd = "gsutil -m cp %s %s" % (
            os.path.join(tmp_cache_dir, _STATEFUL),
            cloud_tgz_dir,
        )
        subprocess.check_output(shlex.split(cmd))
        upload_ts = datetime.datetime.now()
        delta_sec = (upload_ts - start_ts).total_seconds()
        print("Upload took %f seconds." % delta_sec)

        shutil.rmtree(tmp_cache_dir)

    except:
        # In case of exception, make sure that the temporary cache directory is
        # deleted.
        shutil.rmtree(tmp_cache_dir)
        raise


def main(argv=None):
    """Write WiFi credentials to stateful.tgz in configured destination."""
    if argv is None:
        argv = sys.argv[1:]
    # Command line argument description.
    parser = argparse.ArgumentParser(
        description="Write WiFi credentials to stateful.tgz"
    )
    parser.add_argument(
        "dest",
        type=str,
        help="Destination to write WiFi credentials to",
        choices=_DEST,
    )
    parser.add_argument(
        "builder", type=str, help="Builder, eg. nocturne-release"
    )
    parser.add_argument("version", type=str, help="Version, eg. R76-12202.0.0")
    parser.add_argument("ssid", type=str, help="WiFi ssid, eg. ssid")
    parser.add_argument(
        "pw",
        type=str,
        help="WiFi password, eg. password",
        nargs="?",
        default=None,
    )
    args = parser.parse_args(argv)

    if args.dest == _CACHE:
        print("Writing to moblab cache...")
        write_wifi_cred_to_cache(
            args.builder, args.version, args.ssid, args.pw
        )
    elif args.dest == _CLOUD:
        print("Writing to cloud bucket...")
        write_wifi_cred_to_cloud(
            args.builder, args.version, args.ssid, args.pw
        )


if __name__ == "__main__":
    main()
