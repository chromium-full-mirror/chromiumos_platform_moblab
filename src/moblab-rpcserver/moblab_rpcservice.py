# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import re

from moblab_common import build_connector
from moblab_common import dut_connector
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

HARDWARE_AVL_BUG_ID = 'bug_id'
HARDWARE_AVL_PART_NO = 'part_id'

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

    def run_storage_qual_suite(self,
                               build_target,
                               model,
                               milestone,
                               build_version,
                               bug_id,
                               part_id,
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
            'hardware_storagequal', # suite
            pool,
            suite_args=suite_args
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
            specific_modules: Comma-separated string of specific module names to
            run.
        Returns:
          String response message.
        """

        suite_args = {}
        if autotest_tests:
            suite_args['tests'] = [
                test.strip() for test in autotest_tests.split(',')
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
                test.strip() for test in autotest_tests.split(',')
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
                  suite_timeout_mins=_DEFAULT_SUITE_TIMEOUT_MINS,
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

        ap_name, ap_pass = self.config_connector.get_test_wifi_ap_and_password()
        test_args['ssid'] = ap_name
        test_args['wifipass'] = ap_pass

        # TODO(mattmallett b/92031054) Standardize bug id, part id passing
        # for memory/storage qual
        processed_suite_args = dict()
        processed_test_args = dict()

        # set processed_suite_args to None instead of empty dict when there
        # is no argument in processed_suite_args
        if len(processed_suite_args) == 0:
            processed_suite_args = None

        return self.afe_connector.run_suite(
            build_target,
            build,
            builds,
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
            self.build_connector.get_boards_available()
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
            return str(result)
        else:
            # AFE implementation of aborting jobs does not seem to return
            # anything in success scenarios, so we need this placeholder
            # message until a more descriptive replacement is used.
            return 'Successfully applied abort action to selected jobs. ' +\
                'Please refresh jobs list to see results.'

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
