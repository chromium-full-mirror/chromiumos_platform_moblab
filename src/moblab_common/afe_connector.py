# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Interface to the AFE RPC server for all moblab code."""
from __future__ import print_function

import json
import sys
import httplib
import subprocess
import multiprocessing

try:
    from chromite.lib import cros_logging as logging
except ImportError:
    # pylint: disable=cros-logging-import
    import logging

import requests

MOBLAB_RPC_SERVER = 'localhost:80'


def enroll_dut(ip_address):
    cmd = '/usr/local/autotest/cli/atest host create %s' % ip_address
    logging.error(cmd)
    subprocess.call(cmd, shell=True)


class AFEConnector(object):
    """Class that provides moblab an inferface to AFE."""

    def __init__(self):
        """Setup the JSON encoder/decoder."""
        self.json_encoder = json.encoder.JSONEncoder()
        self.json_decoder = json.decoder.JSONDecoder()

    def send_rpc_command(self, method, params=None):
        """Call the AFE RPC server.

        Args:
            method (string): The name of the AFE RPC
            params (string, optional): Defaults to None. A JSON encoded string
                with any paramaters required for the RPC.
        """
        if not params:
            params = {}

        rpc_url = ('http://%s/afe/server/rpc/' % MOBLAB_RPC_SERVER)
        data = self.json_encoder.encode({
            'id': 0,
            'method': method,
            'params': [params]
        })

        logging.debug('%s %s', rpc_url, data)
        try:
            response = requests.post(rpc_url, data=data)
            error = self.decode_response(response, 'error')
            if error:
                logging.error('AFE RPC called %s failed with error %s', rpc_url,
                              error)
            logging.debug('%s %s', response.text, response.content)

            return response
        except requests.exceptions.RequestException as e:
            logging.error(e)

    def decode_response(self, response, key, expected_code=httplib.OK):
        """Get a specific value from the return of an afe call.

        Args:
            response (string): json formatted data.
            key (string): they key of the data to retrieve.
            expected_code (int, optional): Defaults to httplib.OK. [description]

        Returns:
            dict: {} if the AFE server returned an error else a map k,v
            of the response.
        """

        if not response or response.status_code != expected_code:
            if response:
                # TODO(haddowk): Figure out how to return a useful error
                # message.
                logging.error('AFE RPC Failed %s', response.get('error', ''))
            return {}
        return self.json_decoder.decode(response.text)[key]

    def get_config_values(self):
        """Request all the configuration details from AFE.

        Returns:
            dict: { <section name> : { <config_name> : <config_value> } }
        """

        response = self.send_rpc_command('get_config_values')
        raw_result = self.decode_response(response, 'result')
        result = {}

        if not raw_result:
            return result

        for k, v in raw_result.iteritems():
            try:
                result[k] = dict(v)
            except ValueError:
                logging.error('Error getting config values key: %s value: %s',
                              k, v)

        return result

    def get_connected_devices(self):
        """Get the list of hosts (DUT's) configured in AFE.

        Returns:
            list: host
            host is a dict of information about the host, such
        """

        response = self.send_rpc_command('get_hosts')
        return self.decode_response(response, 'result')

    def run_suite(self,
                  board,
                  build,
                  builds,
                  suite,
                  suite_timeout_mins,
                  pool=None,
                  model=None,
                  suite_args=None,
                  test_args=None):
        """Request AFE run a given suite.

        Args:
            board (string): Software build to run, e.g. octopus
            build (string): Software version to run e.g. R73-11647.24.0
            builds (list): Software versions to run e.g. R73-11647.24.0
            suite (string): Test suite to run e.g. cts_P
            model (string, optional): Specific model to run on e.g. phaser
            release_type (str, optional): Defaults to 'release'. used to
                build the full build name octopus-release/R73-11647.24.0
            suite_args (string, optional): Defaults to None. delimited
                key=val pairs passed to suite control file.
            test_args (string, optional): Defaults to None.  delimited
                key=val pairs passed to test control file.
            suite_timeout_mins (integer, optional): Number of minutes until the
                suite times out.
            pool (string, optional): Pool label to target suite on.
        """

        params = {
            'board': board,
            'builds': builds,
            'name': suite,
            'pool': pool,
            'run_prod_code': False,
            'test_source_build': build,
            'wait_for_results': True,
            'suite_args': suite_args,
            'test_args': test_args,
            'job_retry': True,
            'max_retries': sys.maxint,
            'model': model,
            'timeout_mins': suite_timeout_mins,
            'max_runtime_mins': suite_timeout_mins
        }
        response = self.send_rpc_command('create_suite_job', params)

        logging.info(response)
        return response.text

    def enroll_duts(self, ip_addresses):
        p = multiprocessing.Pool(20)
        p.map(enroll_dut, ip_addresses)
        p.close()
        p.join()

    def unenroll_duts(self, ip_addresses):
        hosts = self.get_connected_devices()
        for host in hosts:
            hostname = host.get('hostname')
            params = {'id': host.get('id')}
            logging.error(params)
            if hostname in ip_addresses:
                response = self.send_rpc_command('delete_host', params)
            logging.error(response)
