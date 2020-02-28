# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import re

import build_connector
import dut_connector
try:
    from chromite.lib import cros_logging as logging
except ImportError:
    import logging
from moblab_common import afe_connector
from moblab_common import config_connector
from moblab_common import devserver_connector

_DEFAULT_SUITE_TIMEOUT_MINS = 1440
_SUITE_TIMEOUT_MAP = {
    'hardware_storagequal': 40320,
    'hardware_storagequal_quick': 40320
}


class MoblabRpcError(Exception):
    pass


class MoblabService(object):
    model_re = re.compile(r'^model:(.*)')
    build_target_re = re.compile(r'^board:(.*)')
    pool_re = re.compile(r'^pool:(.*)')

    def __init__(self):
        self.afe_connector = afe_connector.AFEConnector()
        self.config_connector = config_connector.MoblabConfigConnector(
            self.afe_connector)
        self.setup_devserver_connector()
        self.dut_connector = dut_connector.MoblabDUTConnector()

    def setup_devserver_connector(self):
        self.moblab_bucket_name = self.config_connector.get_cloud_bucket()
        logging.info('Using bucket: %s', self.moblab_bucket_name)
        self.devserver_connector = devserver_connector.DevserverConnector(
            self.moblab_bucket_name)
        try:
            self.build_connector = build_connector.MoblabBuildConnector(
                self.moblab_bucket_name)
        except build_connector.MoblabBuildConnectorException as e:
            self.build_connector = None

    def extract_model_from_labels(self, labels):
        return self.extract_from_labels(self.model_re, labels)

    def extract_build_target_from_labels(self, labels):
        return self.extract_from_labels(self.build_target_re, labels)

    def extract_pool_from_labels(self, labels):
        return self.extract_from_labels(self.pool_re, labels)

    def extract_from_labels(self, rexp, labels):
        result = [
            m.group(1) for m in [rexp.match(label) for label in labels] if m
        ]
        return list(set(result))

    def get_connected_devices(self):
        self.dut_connector.find_duts()
        connected_duts = self.dut_connector.get_connected_duts()
        afe_formatted_duts = []
        for dut in connected_duts:
            afe_formatted_duts.append({
                'ip': dut[0],
                'labels': ['model:' + dut[1]],
                'error': dut[3]
            })
        return afe_formatted_duts

    def list_duts(self):
        afe_hosts = self.afe_connector.get_connected_devices()
        potential_hosts = self.get_connected_devices()
        connected_ips = []
        connected_duts = []

        for dut in afe_hosts:
            dut['enrolled'] = True
            connected_ips.append(dut['hostname'])
            connected_duts.append(dut)

        for dut in potential_hosts:
            if dut['ip'] not in connected_ips:
                dut['hostname'] = dut['ip']
                dut['enrolled'] = False
                dut['status'] = 'Not Enrolled'
                dut['error'] = dut['error']
                connected_duts.append(dut)

        return connected_duts

    def run_suite_storage_qual(self,
                               build_target,
                               build_version,
                               suite,
                               model=None,
                               pool=None,
                               bug_id=None,
                               part_id=None):
        suite_args = {}
        if bug_id:
            suite_args['bug_id'] = bug_id
        if part_id:
            suite_args['part_id'] = part_id
        suite_args['bug_id'] = bug_id or ''
        suite_args['part_id'] = part_id or ''

    def run_suite_memory_qual(self,
                              build_target,
                              build_version,
                              suite,
                              model=None,
                              pool=None,
                              bug_id=None,
                              part_id=None):
        pass

    def run_cts_suite(self,
                      build_target,
                      build_version,
                      suite,
                      model,
                      pool=None,
                      autotest_tests=None):
        test_args = {}
        ap_name, ap_pass = self.config_connector.get_test_wifi_ap_and_password()
        test_args['ssid'] = ap_name
        test_args['wifipass'] = ap_pass

        suite_args = {}
        if autotest_tests:
            suite_args['tests'] = [
                test.strip() for test in autotest_tests.split(',')
            ]

        return self.run_suite(
            build_target,
            build_version,
            suite,
            model,
            pool,
            suite_args=suite_args,
            test_args=test_args)

    def run_suite_faft(
            self,
            build_target,
            build_version,
            suite,
            model=None,
            pool=None,
            ro_firmware=None,
            rw_firmware=None,
    ):
        build_versions = {}
        if rw_firmware:
            build_versions['fwrw-version'] = rw_firmware
        if ro_firmware:
            build_versions['fwro-version'] = ro_firmware

    def run_suite(self,
                  build_target,
                  build_version,
                  suite,
                  model=None,
                  pool=None,
                  suite_args=None,
                  test_args=None,
                  suite_timeout_mins=_DEFAULT_SUITE_TIMEOUT_MINS,
                  extra_build_versions={}):

        build_versions = {'cros-version': build}
        build_versions.update(extra_build_versions)

        # TODO(mattmallett b/92031054) Standardize bug id, part id passing
        # for memory/storage qual
        processed_suite_args = dict()
        processed_test_args = dict()

        # set processed_suite_args to None instead of empty dict when there
        # is no argument in processed_suite_args
        if len(processed_suite_args) == 0:
            processed_suite_args = None

        logging.debug('Test args %s', test_args)
        #if test_args:
        #    try:
        #        processed_test_args['args'] = [test_args]
        ##        for line in test_args.split('\n'):
        #            key, value = line.strip().split('=')
        #            processed_test_args[key] = value
        #    except:
        #        raise MoblabRpcError('Could not parse test args.')

        return self.afe_connector.run_suite(
            build_target,
            build_version,
            build_versions,
            suite,
            suite_timeout_mins,
            pool,
            model,
            suite_args=processed_suite_args,
            test_args=test_args)

    def enroll_duts(self, ip_addresses):
        self.afe_connector.enroll_duts(ip_addresses)

    def unenroll_duts(self, ip_addresses):
        self.afe_connector.unenroll_duts(ip_addresses)

    def list_connected_duts_firmware(self):
        duts = self.dut_connector.get_connected_dut_firmware()
        return duts

    def get_dut_details(self, dut):
        return self.afe_connector.get_connected_devices(dut, get_current_jobs=True)

    def update_duts_firmware(self, ip_addresses):
        self.dut_connector.update_firmware(ip_addresses)

    def list_usable_build_targets(self):
        # Get the intersection of build_target available to this moblab and
        # the build_target on the devices connected.
        available_build_targets = \
            self.build_connector.get_build_targets_available()
        connected_build_targets = self.list_connected_dut_build_targets()
        return list(
            set(available_build_targets).intersection(connected_build_targets))

    def list_connected_dut_build_targets(self):
        afe_hosts = self.afe_connector.get_connected_devices()
        build_targets = []
        for host in afe_hosts:
            build_targets.extend(
                self.extract_build_target_from_labels(host.get('labels', [])))
        return build_targets

    def get_num_jobs(self,
                     id_filter=None,
                     name_filter=None,
                     created_time_lt=None,
                     created_time_gt=None,
                     sub=False,
                     suite=False,
                     not_yet_run=False,
                     running=False,
                     finished=False,
                     parent_id_filter=None,
                     dut_hostname_filter=None):
        # TO_DO(wangmichael): bifurcating on dut_filter is necessary because the
        # Autotest backend that we currently invoke only accepts dut_filter on
        # calls to get_num_host_queue_entries, not get_num_jobs. Even though,
        # in both cases, the results are packaged and returned as jobs. This may
        # change when Autotest RPC itself is refactored.
        if dut_hostname_filter:
            try:
                dut_id = self.afe_connector.get_connected_devices(
                hostname=dut_hostname_filter)[0]['id']
            except (IndexError, KeyError):
                logging.error('Unable to find AFE id for dut: {}'.format(dut_hostname_filter))
                return
            return self.afe_connector.get_num_host_queue_entries(
                host_id=dut_id
            )
        else:
            return self.afe_connector.get_num_jobs(
                id_filter, name_filter, created_time_lt, created_time_gt, sub,
                suite, not_yet_run, running, finished, parent_id_filter)

    def get_jobs(self,
                 query_start,
                 query_limit,
                 id_filter=None,
                 name_filter=None,
                 created_time_lt=None,
                 created_time_gt=None,
                 sub=False,
                 suite=False,
                 not_yet_run=False,
                 running=False,
                 finished=False,
                 parent_id_filter=None,
                 dut_hostname_filter=None):
        # TO_DO(wangmichael): bifurcating on dut_filter is necessary because the
        # Autotest backend that we currently invoke only accepts dut_filter on
        # calls to get_host_queue_entries, not get_jobs. Even though,
        # in both cases, the results are packaged and returned as jobs. This may
        # change when Autotest RPC itself is refactored.
        if dut_hostname_filter:
            try:
                dut_id = self.afe_connector.get_connected_devices(
                    hostname=dut_hostname_filter)[0]['id']
            except (IndexError, KeyError):
                logging.error('Unable to find AFE id for dut: {}'.format(dut_hostname_filter))
                return
            hqes = self.afe_connector.get_host_queue_entries(
                host_id=dut_id,
                query_start=query_start,
                query_limit=query_limit,
            )

            jobs = []
            # Extracting jobs information from HQE entries.
            for hqe in hqes:
                job = hqe['job']
                job['status'] = hqe.get('status')
                jobs.append(job)
            return jobs
        else:
            return self.afe_connector.get_jobs(
                query_start, query_limit, id_filter, name_filter,
                created_time_lt, created_time_gt, sub, suite, not_yet_run,
                running, finished, parent_id_filter)

    def get_job_details(self, job_id):
        return self.afe_connector.get_jobs_by_ids([job_id])

    def get_job_history(self, job_id):
        return self.afe_connector.get_job_history(job_id)

    def get_associated_duts(self, job_id):
        return self.afe_connector.get_host_queue_entries(job_id=job_id)

    def get_num_dut_tasks(self, ip, start_time_gt, end_time_lt):
        """
            Given a DUT's IP, returns a number of tasks (e.g. repairs, reverifies)
            associated with that DUT.
        Args:
            ip (string): DUT IP.
            start_time_gt(int): Seconds timestamp of a filter to DUT tasks by
                start time.
            end_time_lt(int): Seconds timestamp of a filter to DUT tasks by
                end time.
        Returns:
            Returns number of task associated with DUT which match query parameters.
            If DUT itself is not found, returns -1.
        """
        try:
            dut_id = self.afe_connector.get_connected_devices(hostname=ip)[0]['id']
            return self.afe_connector.get_num_special_tasks(
                host_id_list=[dut_id],
                start_time_gt=start_time_gt,
                end_time_lt=end_time_lt
            )
        except (IndexError, KeyError):
            logging.error('Unable to find AFE id for dut: {}'.format(dut_id))
            return -1

    def get_dut_tasks(self, ip, query_start, query_limit, start_time_gt, end_time_lt):
        """
            Given a DUT's IP, returns a list of tasks (e.g. repairs, reverifies)
            requested for that DUT. If DUT is not found, returns None.
        Args:
            query_start(int): Parameter specifying index on where to start when
                returning paged results.
            query_limit(int): Upper limit on number of results to return.
            start_time_gt(int): Seconds timestamp of a filter to DUT tasks by
                start time.
            end_time_lt(int): Seconds timestamp of a filter to DUT tasks by
                end time.
        Returns:
            A list of dicts, each dict specifying a task associated with the
            queried DUT. If DUT is not found returns None.
        """
        try:
            dut_id = self.afe_connector.get_connected_devices(hostname=ip)[0]['id']
            return self.afe_connector.get_special_tasks(
                host_id_list=[dut_id],
                query_start=query_start,
                query_limit=query_limit,
                start_time_gt=start_time_gt,
                end_time_lt=end_time_lt,
            )
        except (IndexError, KeyError):
            logging.error('Unable to find AFE id for dut: {}'.format(dut_id))
