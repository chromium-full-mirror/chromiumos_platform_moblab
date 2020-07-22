# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import docker
import os
import re
import requests
import socket

from moblab_common import build_connector
from moblab_common import dut_connector
from moblab_common import host_connector
from moblab_common import moblab_info
try:
    from chromite.lib import cros_logging as logging
except ImportError:
    import logging
from moblab_common import afe_connector
from moblab_common import config_connector
from moblab_common import devserver_connector

# File where information about the current device is stored.
_ETC_LSB_RELEASE = '/etc/lsb-release'

_DEFAULT_SUITE_TIMEOUT_MINS = 1440
_SUITE_TIMEOUT_MAP = {
    'hardware_storagequal': 40320,
    'hardware_storagequal_quick': 40320
}

_STORAGE_QUAL_VARIATIONS = {
    0: 'hardware_storagequal',
    1: 'hardware_storagequal_quick',
    2: 'hardware_storagequal_external'
}

HARDWARE_AVL_BUG_ID = 'bug_id'
HARDWARE_AVL_PART_NO = 'part_id'

MOBLAB_DOCKER_REGISTRY = 'gcr.io/chromeos-partner-moblab/'

class MoblabRpcError(Exception):
    pass


class MoblabService(object):
    model_re = re.compile(r'^model:(.*)')
    build_target_re = re.compile(r'^board:(.*)')
    pool_re = re.compile(r'^pool:(.*)')

    afe_connector = None

    def __init__(self):
        self.afe_connector = afe_connector.AFEConnector()
        self.config_connector = config_connector.MoblabConfigConnector(
            self.afe_connector)
        self.setup_devserver_connector()
        self.dut_connector = dut_connector.MoblabDUTConnector()

    def _find_dut_id_given_ip(self, dut_hostname):
        """
            Given an ip address, will return the id given to the DUT by AFE;
            else will raise an error.
        """
        try:
            return self.afe_connector.get_connected_devices(
                hostname=dut_hostname)[0]['id']
        except (IndexError, KeyError):
            msg = 'Unable to find AFE id for dut: {}'.format(dut_hostname)
            logging.error(msg)
            raise MoblabRpcError(msg)

    def setup_devserver_connector(self):
        self.moblab_bucket_name = self.config_connector.get_cloud_bucket()
        logging.info('Using bucket: %s', self.moblab_bucket_name)
        self.devserver_connector = devserver_connector.DevserverConnector(
            self.moblab_bucket_name)
        self._init_build_connector(raise_error=False)

    def _init_build_connector(self, raise_error=True):
        try:
            self._build_connector = build_connector.MoblabBuildConnector(
                self.moblab_bucket_name
            )
        except build_connector.MoblabBuildConnectorException as e:
            logging.exception('Failed to initialize MoblabBuildConnector.')
            if raise_error:
                raise

    @property
    def build_connector(self):
        current_moblab_bucket_name = self.config_connector.get_cloud_bucket(force_reload=True)

        if not hasattr(self, '_build_connector') or \
                not self._build_connector or \
                current_moblab_bucket_name != self.moblab_bucket_name:
            self.moblab_bucket_name = current_moblab_bucket_name
            self._init_build_connector()
        return self._build_connector

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
        connected_duts = self.dut_connector.get_connected_duts()
        afe_formatted_duts = []
        for dut in connected_duts:
            afe_formatted_duts.append({
                'ip': dut[0],
                'isConnected': dut[1],
                'error': dut[2]
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

    def _default_suite_timeout_mins(self, suite):
        if suite in _SUITE_TIMEOUT_MAP:
            return _SUITE_TIMEOUT_MAP[suite]
        else:
            return _DEFAULT_SUITE_TIMEOUT_MINS

    def run_storage_qual_suite(self,
                               build_target,
                               model,
                               milestone,
                               build_version,
                               bug_id,
                               part_id,
                               variation,
                               pool=None,
    ):
        """Starts storage qual suite run. Formats arguments s.t. they can be
        ingested by AFE.

        Args:
            build_target: Ex. octopus
            milestone: Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            model: String identfier for the specific model to be run.
            pool: String identifier for which pool of DUT's to run tests with.
            avl_process_bug_id: Numeric string identifying the associated
            buganizer issue.
            avl_part_number: Numeric string identifying relevant part number.
            variation: RunStorageQualificationSuiteRequest.Variation
            pool: String test pool identifier.
        Returns:
          String response message.
        """
        avl_args = {
            HARDWARE_AVL_BUG_ID: bug_id,
            HARDWARE_AVL_PART_NO: part_id
        }

        return self.run_suite(
            build_target,
            model,
            milestone,
            build_version,
            _STORAGE_QUAL_VARIATIONS[variation],
            pool,
            suite_args=avl_args,
            test_args=avl_args
        )

    def run_memory_qual_suite(self,
                              build_target,
                              model,
                              milestone,
                              build_version,
                              bug_id,
                              part_id,
                              pool=None,
    ):
        """Starts memory qual suite run. Formats arguments s.t. they can be
        ingested by AFE.

        Args:
            build_target: Ex. octopus
            milestone: Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            model: String identfier for the specific model to be run.
            pool: String identifier for which pool of DUT's to run tests with.
            avl_process_bug_id: Numeric string identifying the associated
            buganizer issue.
            avl_part_number: Numeric string identifying relevant part number.
        Returns:
          String response message.
        """
        suite_args = {
            HARDWARE_AVL_BUG_ID: bug_id,
            HARDWARE_AVL_PART_NO: part_id
        }
        return self.run_suite(
            build_target,
            model,
            milestone,
            build_version,
            'hardware_memoryqual', # suite
            pool,
            suite_args=suite_args)

    def run_cts_suite(self,
                      build_target,
                      model,
                      milestone,
                      build_version,
                      suite,
                      pool=None,
                      autotest_tests=None):
        """Starts cts suite run. Formats arguments s.t. they can be ingested by
        AFE.

        Args:
            build_target: Ex. octopus
            milestone: Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            model: String identfier for the specific model to be run.
            pool: String identifier for which pool of DUT's to run tests with.
            specific_modules: List of strings of specific module names to
            run.
        Returns:
          String response message.
        """

        suite_args = {}
        if autotest_tests and len(autotest_tests):
            suite_args['tests'] = [
                test.strip() for test in autotest_tests
            ]

        return self.run_suite(
            build_target,
            model,
            milestone,
            build_version,
            suite,
            pool,
            suite_args=suite_args)

    def run_gts_suite(self,
                      build_target,
                      model,
                      milestone,
                      build_version,
                      pool=None,
                      autotest_tests=None):
        """Starts gts suite run. Formats arguments s.t. they can be ingested by
        AFE.

        Args:
            build_target: Ex. octopus
            milestone: Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            model: String identfier for the specific model to be run.
            pool: String identifier for which pool of DUT's to run tests with.
            specific_modules: Comma-separated string of specific module names to
            run.
        Returns:
          String response message.
        """
        suite_args = {}
        if autotest_tests:
            suite_args['tests'] = [
                test.strip() for test in autotest_tests
            ]

        return self.run_suite(
            build_target,
            model,
            milestone,
            build_version,
            'gts', # suite
            pool,
            suite_args=suite_args)

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
                  model,
                  milestone,
                  build_version,
                  suite,
                  pool=None,
                  suite_args={},
                  test_args={},
                  suite_timeout_mins=None,
                  extra_builds={}):
        """Starts suite run. Formats input arguments s.t. that they can be used
        by an AFE suite run command.

        Args:
            build_target: Ex. octopus
            milestone: Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            suite: String identifier for the suite to be run.
            model: String identfier for the specific model to be run.
            pool: String identifier for which pool of DUT's to run tests with.
            suite_args: Dict containing key=val pairs to be used by suite control
              file.
            test_args: Dict containing key=val pairs to be used by test control
              file.
        Returns:
          String response message.
        """
        build = '{}-release/{}-{}'.format(build_target, milestone, build_version)
        builds = {'cros-version': build}

        builds.update(extra_builds)

        if not suite_timeout_mins:
            suite_timeout_mins = self._default_suite_timeout_mins(suite)

        ap_name, ap_pass = self.config_connector.get_test_wifi_ap_and_password()
        test_args['ssid'] = ap_name
        test_args['wifipass'] = ap_pass

        return self.afe_connector.run_suite(
            build_target,
            build,
            builds,
            suite,
            suite_timeout_mins,
            pool,
            model,
            suite_args=suite_args,
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
            self.build_connector.get_boards_available()
        connected_build_targets = self.list_connected_dut_build_targets()
        return list(
            set(available_build_targets).intersection(connected_build_targets))

    def list_usable_milestones(self, build_target):
        return self.build_connector.get_milestones_available(
            build_target)

    def list_usable_build_versions(self, build_target, milestone):
        return self.build_connector.get_builds_for_milestone(
            build_target, milestone)

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

    def get_job_ids(self,
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
        """Returns the job ID's that match the request filters.

        Args:
            query_start: Int index for start of returned values.
            query_limit: Int for max number of values to return.
            id_filter: String filter for job id.
            name_filter: String filter for job name.
            created_time_lt: A unix timestamp in seconds granularity the sets
                upper bound for jobs returned.
            created_time_gt: A unix timestamp in seconds granularity the sets
                lower bound for jobs returned.
            sub: Boolean, true iff child jobs to be returned.
            suite: Boolean, true iff parent jobs to be returned.
            not_yet_run: Boolean, true iff queued jobs to be returned.
            running: Boolean, true iff running jobs to be returned.
            finished: Boolean, true iff only finished jobs to be returned.
            parent_id_filter: String filter for parent job id.
            dut_hostname_filter: String filter for DUT associated with job.

        Returns:
          List of job ID numbers.
        """
        return [job['id'] for job in
                self.get_jobs(query_start, query_limit, id_filter, name_filter,
                              created_time_lt, created_time_gt, sub, suite,
                              not_yet_run, running, finished, parent_id_filter,
                              dut_hostname_filter)]


    def abort_jobs(self, job_ids):
        result = self.afe_connector.abort_host_queue_entries(job_ids)
        if result:
            aborted_jobs = [str(item['Job']) for item in result]
            if len(aborted_jobs) > 15:
                return 'Aborted {} jobs, please refresh table to see results.'.format(
                    len(aborted_jobs)
                )
            else:
                return 'Aborted the following jobs: {}\nPlease refresh table to see results.'.format(
                    ', '.join(aborted_jobs)
                )
        else:
            return 'No jobs aborted (were selected jobs already aborted/finished)?'

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

    def add_label_to_host(self, dut_hostname, label):
        return self.afe_connector.add_label_to_host(dut_hostname, label)

    def remove_label_from_host(self, dut_hostname, label):
        return self.afe_connector.remove_label_to_host(dut_hostname, label)

    def _apply_edit_to_duts(self, dut_hostnames, afe_edit_func, success_msg, *args):
        """
            A helper function which contains the repeated logic involved in
            applying an edit to multiple DUTs. This logic is repeated for
            adding and removing attributes and labels.
        Args:
            dut_hostnames(string[]): A list of strings representing the hostnames
            of the DUT's to be targeted.
            afe_edit_func((*args) => (tuple(bool,string))): A reference to a
            function of AFEConnector which takes in *args and returns a tuple
            containing a bool indicating success and a results message string.
            This function does the 'edit' to the DUT's. success_msg(int): A
            format-able string to be returned in success cases; It should have
            exactly as many format indexes ({}) as there are arguments in *args.
            *args: Arguments which are meant to be passed into afe_edit_func.
        Returns:
            String message summarizing results.
        """
        failures = {}
        for dut_hostname in dut_hostnames:
            is_success, message = afe_edit_func(dut_hostname, *args)
            if not is_success:
                failures[dut_hostname] = message

        response_message = success_msg.format(*args) +\
            " to {} DUTs\n".format(
                len(dut_hostnames) - len(failures.keys())
            )

        if failures:
            response_message += "Failures on the following DUTs:\n"
            for dut_hostname, message in failures.items():
                response_message += "{}: {}\n".format(dut_hostname, message)

        return response_message

    def add_attribute_to_duts(self, dut_hostnames, key, value):
        """
            Adds attribute key:value to the selected dut_hostnames. Returns a message
            summarizing how many DUT's the attribute was successfully added to
            as well for which DUT's the addition failed.
        Args:
            dut_hostnames(string[]): A list of strings representing the hostnames
            of the DUT's to be targeted.
            key (string): Key of attribute to be added.
            value (string): Value of attribute to be added.
        Returns:
            String message summarizing results.
        """
        return self._apply_edit_to_duts(
            dut_hostnames,
            # self.add_attribute_to_host,
            self.afe_connector.add_attribute_to_host,
            "Successfully added attribute {}:{}",
            key,
            value,
        )

    def remove_attribute_from_duts(self, dut_hostnames, key):
        """
            Removes attribute (referenced by key) from the selected dut_hostnames.
            Returns a message summarizing how many DUT's the attribute was
            successfully removed from as well for which DUT's the remove failed.
        Args:
            dut_hostnames(string[]): A list of strings representing the hostnames
            of the DUT's to be targeted.
            key (string): Key of attribute to be remove.
            value (string): Value of attribute to be remove.
        Returns:
            String message summarizing results.
        """
        return self._apply_edit_to_duts(
            dut_hostnames,
            self.afe_connector.remove_attribute_from_host,
            "Successfully removed attribute {}",
            key,
        )

    def add_label_to_duts(self, dut_hostnames, label):
        """
            Adds label to the selected dut_hostnames. Returns a message summarizing
            how many DUT's the label was successfully added to as well for which
            DUT's the addition failed.
        Args:
            dut_hostnames(string[]): A list of strings representing the hostnames
            of the DUT's to be targeted.
            label (string): Label to be added.
        Returns:
            String message summarizing results.
        """
        return self._apply_edit_to_duts(
            dut_hostnames,
            self.afe_connector.add_label_to_host,
            "Successfully added label {}",
            label,
        )

    def remove_label_from_duts(self, dut_hostnames, label):
        """
            Remove label from the selected dut_hostnames. Returns a message summarizing
            how many DUT's the label was successfully removed from as well as for
            which DUT's the remove failed.
        Args:
            dut_hostnames(string[]): A list of strings representing the hostnames
            of the DUT's to be targeted.
            label (string): Label to be removed.
        Returns:
            String message summarizing results.
        """
        return self._apply_edit_to_duts(
            dut_hostnames,
            self.afe_connector.remove_label_from_host,
            "Successfully removed label {}",
            label,
        )

    def add_pool_to_duts(self, dut_hostnames, pool):
        """
            Adds  pool to the selected dut_hostnames. Returns a message summarizing
            how many DUT's the  pool was successfully added to as well for which
            DUT's the addition failed.
        Args:
            dut_hostnames(string[]): A list of strings representing the hostnames
            of the DUT's to be targeted.
            pool (string): Pool to be added.
        Returns:
            String message summarizing results.
        """
        return self.add_label_to_duts(dut_hostnames, 'pool:' + pool)

    def remove_pool_from_duts(self, dut_hostnames, pool):
        """
            Remove  pool from the selected dut_hostnames. Returns a message summarizing
            how many DUT's the  pool was successfully removed from as well as for
            which DUT's the remove failed.
        Args:
            dut_hostnames(string[]): A list of strings representing the hostnames
            of the DUT's to be targeted.
             pool (string): Pool to be removed.
        Returns:
            String message summarizing results.
        """
        return self.remove_label_from_duts(dut_hostnames, 'pool:' + pool)

    def reverify_host(self, dut_hostname):
        """Starts repair run on given DUT hostname.

        Args:
            dut_hostname(string): String hostname (ex. IP address)
        """
        dut_id = self._find_dut_id_given_ip(dut_hostname)
        if dut_id:
            self.afe_connector.reverify_host(dut_id)

        return 'Successfully set off reverify on {}'.format(dut_hostname)

    def repair_host(self, dut_hostname):
        """Starts repair run on given DUT hostname.

        Args:
            dut_hostname(string): String hostname (ex. IP address)
        """
        dut_id = self._find_dut_id_given_ip(dut_hostname)
        if dut_id:
            self.afe_connector.repair_host(dut_id)

        return 'Successfully set off repair on {}'.format(dut_hostname)

    def get_cloud_configuration(self):
        """
            Gets cloud configuration info.
        Returns:
            A dict of cloud configuration info  ( specifically, 'gs_access_key_id',
            'gs_secret_access_key', 'image_storage_server' )
        """
        return self.afe_connector.get_cloud_storage_info()

    def get_dut_wifi_info(self):
        """
            Gets DUT wifi info.
        Returns:
            A dict with dut_wifi_name, dut_wifi_password
        """
        return self.afe_connector.get_dut_wifi_info()

    def set_dut_wifi_info(self, dut_wifi_name, dut_wifi_password):
        """
            Attempts to set DUT wifi on Moblab.
        Args:
            dut_wifi_name (string): Wifi name
            dut_wifi_password (string): Wifi password
        Returns:
            A result message string.
        """
        if self.afe_connector.set_configuration_info(
            dut_wifi_name=dut_wifi_name,
            dut_wifi_password=dut_wifi_password,
        ):
            return 'Successfully applied DUT Wifi info changes.'
        else:
            return 'Failed to apply DUT Wifi info changes.'

    def set_cloud_configuration(self, boto_key_id, boto_key_secret, gcs_bucket_url):
        """
            Attempts to set configuration values to Moblab.
        Args:
            boto_key_id (string): boto ID string
            boto_key_secret (string): boto secret string
            gcs_bucket_url (string): GCS bucket URL
        Returns:
            A result message string.
        """
        is_valid, details = self.afe_connector.validate_cloud_storage_info(
            boto_key_id, boto_key_secret, gcs_bucket_url)

        if is_valid:
            if self.afe_connector.set_configuration_info(boto_key_id, boto_key_secret, gcs_bucket_url):
                return 'Successfully applied cloud configuration changes.'
            else:
                return 'Failed to apply cloud configuration changes.'
        else:
            return details

    def _get_public_ip_address(self):
        """Gets the public IP address.

        @return: public ip address as string.
        """
        try:
            return host_connector.HostServicesConnector.get_ip()
        except host_connector.HostServicesException:
            logging.exception("Failed to get ip address from host.")
        return "No IP Address"

    def get_network_info(self):
        """
            Gets network info of Moblab.

            TCP socket is used to test the connectivity. If there is no connectivity,
            try to get the public IP with UDP socket.

        Returns:
            A dict of network information ( specifically, a 'server_ip' and
            'is_connected' which is true iff Moblab is connected to internet.
        """
        ip = self._get_public_ip_address()
        if ip is not None:
            logging.info('Established TCP connection with well known server.')
            return {
                'server_ip': ip,
                'is_connected': True
            }
        return {
            'server_ip': None,
            'is_connected': False
        }

    def get_is_update_available(self):
        """
            Check to see if there are any containers that have updated images.

            Scan the running containers, if the watchtower program has pulled down
            a newer image then the container to image reference tag is broken.

            Detect these image tag link breaks and assume that means we have an update.
            Looking through update tools and forums, it seems this is the way
            all update tools work.

        Returns:
            True iff there is an update available.
        """
        client = docker.from_env(timeout=300)
        for container in client.containers.list():
            if len(container.image.tags) == 0:
                return True
        return False

    def update_docker(self):
        """
            Sets off an update of all docker containers, using watchtower

        Returns: String result message.
        """
        client = docker.from_env(timeout=600)

        try:
            container = client.containers.get('update')
            raise MoblabRpcError("Already updating please wait.")
        except docker.errors.NotFound:
            pass

        label = os.environ.get('WATCHTOWER_TAG', 'release')
        container = client.containers.run(
            MOBLAB_DOCKER_REGISTRY + 'watchtower:%s' % label,
            volumes=['/var/run/docker.sock:/var/run/docker.sock'],
            name='update',
            detach=True,
            command='--run-once'
        )

        try:
            container.wait(timeout=600)
        except requests.exceptions.ReadTimeout:
            container.stop()
        finally:
            container.remove()
        return 'Update finished.'

    def get_version_info(self):
        """
            Gets cloud version info of Moblab.
        Returns:
            A dict of ChromeOS and Moblab information (ex. serial number,
            release version )
        """
        lines = open(_ETC_LSB_RELEASE).readlines()
        version_info = {
            x.split('=')[0]: x.split('=')[1] for x in lines if '=' in x}
        version_info['MOBLAB_ID'] = moblab_info.get_or_create_id();
        version_info['MOBLAB_SERIAL_NUMBER'] = moblab_info.get_serial_number();

        try:
            version_info['CHROMEOS_RELEASE_VERSION'] =\
                version_info['CHROMEOS_RELEASE_BUILDER_PATH'].split('/')[1].strip()
        except IndexError:
            msg = 'Unable to parse ChromeOS release version.'
            logging.error(msg)
            raise MoblabRpcError(msg)

        return version_info
