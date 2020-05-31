#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import argparse
import concurrent.futures
import logging
import subprocess
import sys
import time
import netifaces

import grpc
import netifaces

# pylint: disable=import-error
import hostservices_pb2
# pylint: disable=import-error
import hostservices_pb2_grpc


class HostService(hostservices_pb2_grpc.MoblabHostServiceServicer):

    # ChromeOS update engine client binary location
    _UPDATE_ENGINE_CLIENT = '/usr/bin/update_engine_client'

    def get_host_identifier(self, unused_request, unused_context):
        response = hostservices_pb2.HostIdentifierResponse()
        response.identifier = 'NoSerialNumber'
        for vpd_key in ['serial_number', 'ethernet_mac']:
            try:
                cmd_result = subprocess.run(['vpd', '-g', vpd_key],
                                            stdout=subprocess.PIPE)
                if (cmd_result and cmd_result.returncode == 0 and
                        cmd_result.stdout):
                    response.identifier = cmd_result.stdout
                    break
            except subprocess.SubprocessError:
                logging.exception('Error retrieving vpd value %s', vpd_key)
        return response

    def is_service_running(self, request, unused_context):
        """Test if |service| is running on moblab.

        Returns:
            True if the job |service| is in 'start/running' state.
            False otherwise.
        """
        response = hostservices_pb2.ServiceRunningResponse()
        response.is_running = False
        cmd = ['status', request.service]
        cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        if (cmd_result and cmd_result.returncode == 0 and cmd_result.stdout):
            response.is_running == 'start/running' in cmd_result.stdout
        return response

    def get_disk_info(self, unused_request, unused_context):
        result = 'df -h\n'
        cmd = ['df -h | sort -r -k 5 -i | grep dev']
        cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        if (cmd_result and cmd_result.returncode == 0 and cmd_result.stdout):
            result += cmd_result.stdout.decode('utf-8')

        result += '\nlsblk\n'
        cmd = ['lsblk']
        cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        if (cmd_result and cmd_result.returncode == 0 and cmd_result.stdout):
            result += cmd_result.stdout.decode('utf-8')

        response = hostservices_pb2.DiskInfoResponse()
        response.disk_info = result
        return response

    def get_ip(self, unused_request, unused_context):
        MOBLAB_SUBNET_ADDR = '192.168.231.1'
        response = hostservices_pb2.IpResponse()
        response.ip_address = 'localhost'
        for iface in netifaces.interfaces():
            if 'eth' not in iface:
                continue
            addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET)
            if not addrs:
                continue
            for addr in addrs:
                if MOBLAB_SUBNET_ADDR != addr.get('addr'):
                    response.ip_address = addr['addr']
        return response

    def check_for_system_update(self, unused_request, unused_context):
        """Run the ChromeOS update client to check update server.

        If an update exists, the update client begins downloading it
        in the background.
        """
        subprocess.call([self._UPDATE_ENGINE_CLIENT, '-check_for_update'])
        # wait for update engine to finish checking
        tries = 0
        while (b'CHECKING_FOR_UPDATE' in self._get_system_update_status()
               [b'CURRENT_OP'] and tries < 10):
            time.sleep(.1)
            tries = tries + 1

        return hostservices_pb2.SystemUpdateCheckResponse()

    def _get_system_update_status(self):
        """Run the ChromeOS update client to check status.

        @return: A dictionary containing {
            PROGRESS: str containing percent progress of an update download
            CURRENT_OP: str current status of the update engine,
                ex UPDATE_STATUS_UPDATED_NEED_REBOOT
            NEW_SIZE: str size of the update
            NEW_VERSION: str version number for the update
            LAST_CHECKED_TIME: str unix time stamp of the last update check
        }
        """
        cmd_out = subprocess.check_output(
            [self._UPDATE_ENGINE_CLIENT, '--status'])
        split_lines = [x.split(b'=') for x in cmd_out.strip().split(b'\n')]
        status = dict((key, val) for [key, val] in split_lines)
        return status

    def get_system_update_status(self, unused_request, unused_context):
        """Check to see if current update status of host device."""

        response = hostservices_pb2.SystemUpdateStatusResponse()
        status = self._get_system_update_status()

        response.progress = status.get(b'PROGRESS')
        response.current_op = status.get(b'CURRENT_OP')
        response.new_size = status.get(b'NEW_SIZE')
        response.new_version = status.get(b'NEW_VERSION')
        response.last_checked_time = status.get(b'LAST_CHECKED_TIME')

        return response

    def install_system_update(self, unused_request, unused_context):
        """Installs a ChromeOS update, will cause the system to reboot."""

        response = hostservices_pb2.SystemUpdateInstallResponse()
        # first run a blocking command to check, fetch, prepare an update
        # then check if a reboot is needed
        try:
            subprocess.check_call([self._UPDATE_ENGINE_CLIENT, '--update'])
            # --is_reboot_needed returns 0 if a reboot is required
            subprocess.check_call(
                [self._UPDATE_ENGINE_CLIENT, '--is_reboot_needed'])
            subprocess.call([self._UPDATE_ENGINE_CLIENT, '--reboot'])

        except subprocess.CalledProcessError:
            response.error = subprocess.check_output(
                [self._UPDATE_ENGINE_CLIENT, '--last_attempt_error'])

        return response

    def reboot(self, unused_request, unused_context):
        """Reboot the moblab."""
        response = hostservices_pb2.RebootResponse()
        subprocess.check_call(['reboot'])
        return response

    def factory_reset(self, unused_request, unused_context):
        """Powerwash the moblab."""
        response = hostservices_pb2.FactoryResetResponse()
        subprocess.check_call(['echo', 'safe fast keepimg', '>',
             '/mnt/stateful_partition/factory_install_reset'])
        subprocess.check_call(['reboot'])


def setup_logging(level):
    """Enable the correct level of logging.

    Args:
        level (int): One of the predefined logging levels, e.g loging.DEBUG.
    """
    logging.getLogger().handlers = []
    logging.getLogger().setLevel(level)
    fh = logging.FileHandler('/var/log/moblab/hostservices.log')
    fh.setLevel(level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logging.getLogger().addHandler(fh)


def parse_arguments(argv):
    """Creates the argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        '-v', '--verbose', action='store_true', help='Turn on debug logging.')
    return parser.parse_args(argv)


def serve():
    options = parse_arguments(sys.argv[1:])
    logging_severity = logging.INFO
    if options.verbose:
        logging_severity = logging.DEBUG
    setup_logging(logging_severity)

    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=500))

    host_service = HostService()

    try:
        hostservices_pb2_grpc.add_MoblabHostServiceServicer_to_server(
            host_service, server)

        server.add_insecure_port('[::]:7002')
        logging.info('Starting server')
        server.start()
        while True:
            logging.info('Server sleepin')
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
