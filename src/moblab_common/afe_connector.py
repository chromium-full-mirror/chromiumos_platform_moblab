# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Interface to the AFE RPC server for all moblab code."""

import http.client
import json
import sys
import multiprocessing

from datetime import datetime

import logging

import docker
import requests

MOBLAB_RPC_SERVER = "autotest-afe:8888"

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


def enroll_dut(ip_address):
    client = docker.from_env()
    afe_container = client.containers.get("autotest-afe")
    cmd = "/usr/local/autotest/cli/atest host create %s" % ip_address
    _LOGGER.debug(cmd)
    (_, output) = afe_container.exec_run(cmd)
    _LOGGER.debug(output)


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

        rpc_url = "http://%s/afe/server/rpc/" % MOBLAB_RPC_SERVER
        data = self.json_encoder.encode(
            {"id": 0, "method": method, "params": [params]}
        )

        _LOGGER.debug("URL: %s Data: %s", rpc_url, data)
        try:
            response = requests.post(rpc_url, data=data)
            error = self.decode_response(response, "error")
            if error:
                _LOGGER.error("AFE %s failed with error %s", method, error)
            _LOGGER.debug("Response: %s", response.text)
            return response
        except requests.exceptions.RequestException as e:
            _LOGGER.error(e)

    def decode_response(self, response, key, expected_code=http.client.OK):
        """Get a specific value from the return of an afe call.

        Args:
            response (string): json formatted data.
            key (string): they key of the data to retrieve.
            expected_code (int, optional): Defaults to http.client.OK.

        Returns:
            dict: {} if the AFE server returned an error else a map k,v
            of the response.
        """
        if not response or response.status_code != expected_code:
            if response:
                # TODO(haddowk): Figure out how to return a useful error
                # message.
                _LOGGER.error("AFE RPC Failed %s", response.get("error", ""))
            return {}
        return self.json_decoder.decode(response.text)[key]

    def get_config_values(self):
        """Request all the configuration details from AFE.

        Returns:
            dict: { <section name> : { <config_name> : <config_value> } }
        """
        response = self.send_rpc_command("get_config_values")
        raw_result = self.decode_response(response, "result")
        result = {}

        if not raw_result:
            return result

        for k, v in list(raw_result.items()):
            try:
                result[k] = dict(v)
            except ValueError:
                _LOGGER.error(
                    "Error getting config values key: %s value: %s", k, v
                )

        return result

    def get_connected_devices(self, hostname=None, get_current_jobs=False):
        """Get the list of hosts (DUT's) configured in AFE ( which match
           the specified hostname, if provided).

            hostname (string): ip for which to return information.
            get_current_jobs (bool): return info about curently executing
                jobs and special tasks on DUT.

        Returns:
            A list of dictionaries, each dict with host information.
        """
        params = {}

        if hostname:
            params["hostname"] = hostname

        if get_current_jobs:
            params["include_current_job"] = "true"

        response = self.send_rpc_command("get_hosts", params)
        return self.decode_response(response, "result")

    def get_num_jobs(
        self,
        id_filter=None,
        name_filter=None,
        created_time_lt=None,
        created_time_gt=None,
        sub=False,
        suite=False,
        not_yet_run=False,
        running=False,
        finished=False,
        completed_status=None,
        parent_id_filter=None,
    ):
        """
            Returns number of jobs that match filter arguments. Any arg that
            evaluates to false is not used for filtering.
        Args:
            id_filter: Filter for only jobs that contain id string, this is a
                contains match rather than an exact match.
            name_filter: Filter for only jobs that contain name string, this
                is a contains match rather than an exact match.
            created_time_lt: Upper bound created time filter. Second
                granularity timestamp.
            created_time_gt: Lower bound created time filter. Second
                granularity timestamp.
            sub: true iff only child jobs are not to be filtered.
            suite: true iff only parent jobs are not to be filtered.
            not_yet_run: true iff only not-yet-run jobs are not to be filtered.
            running: true iff only running jobs are not to be filtered.
            finished: true iff only finished jobs are not to be filtered.
            parent_id_filter: Filter for only jobs that are children of this
                job id, this is an exact match:
        Returns:
            A dict containing 'result' number.
        """
        params = {
            "completed_status": completed_status,
        }

        if id_filter:
            params["id__icontains"] = id_filter
        if name_filter:
            params["name__icontains"] = name_filter
        if created_time_lt:
            params["created_on__lte"] = str(
                datetime.fromtimestamp(created_time_lt).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        if created_time_gt:
            params["created_on__gte"] = str(
                datetime.fromtimestamp(created_time_gt).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

        if sub:
            params["sub"] = "true"
        elif suite:
            params["suite"] = "true"

        if not_yet_run:
            params["not_yet_run"] = "true"
        elif running:
            params["running"] = "true"
        elif finished:
            params["finished"] = "true"

        if parent_id_filter:
            params["parent_job"] = parent_id_filter

        response = self.send_rpc_command("get_num_jobs", params)
        _LOGGER.error(response)
        return self.decode_response(response, "result")

    def get_jobs(
        self,
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
        completed_status=None,
        parent_id_filter=None,
        sort_by=None,
    ):
        """Get attributes of the jobs specified.
        Args:
            id_filter: Filter for only jobs that contain id string, this is a
                contains match rather than an exact match.
            name_filter: Filter for only jobs that contain name string, this
                is a contains match rather than an exact match.
            created_time_lt: Upper bound created time filter. Second
                granularity timestamp.
            created_time_gt: Lower bound created time filter. Second
                granularity timestamp.
            sub: true iff only child jobs are not to be filtered.
            suite: true iff only parent jobs are not to be filtered.
            not_yet_run: true iff only not-yet-run jobs are not to be filtered.
            running: true iff only running jobs are not to be filtered.
            finished: true iff only finished jobs are not to be filtered.
            parent_id_filter: Filter for only jobs that are children of this
        Returns:
            A list of dict. The key, value of the dict is the job attribute
            name and the value.
        """

        if not sort_by:
            sort_by = "-created_on"
        params = {
            "query_start": query_start,
            "query_limit": query_limit,
            "sort_by": [sort_by],
            "completed_status": completed_status,
        }

        if id_filter:
            params["id__iexact"] = id_filter
        if name_filter:
            params["name__icontains"] = name_filter
        if created_time_lt:
            params["created_on__lte"] = str(
                datetime.fromtimestamp(created_time_lt).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        if created_time_gt:
            params["created_on__gte"] = str(
                datetime.fromtimestamp(created_time_gt).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

        if sub:
            params["sub"] = "true"
        elif suite:
            params["suite"] = "true"

        if not_yet_run:
            params["not_yet_run"] = "true"
        elif running:
            params["running"] = "true"
        elif finished:
            params["finished"] = "true"

        if parent_id_filter:
            params["parent_job"] = parent_id_filter

        response = self.send_rpc_command("get_jobs_summary", params)
        return self.decode_response(response, "result")

    def get_jobs_by_ids(self, id_list):
        assert isinstance(id_list, list)
        params = {"id__in": id_list}
        response = self.send_rpc_command("get_jobs_summary", params)
        return self.decode_response(response, "result")

    def get_job_history(self, job_id):
        params = {"job_id": str(job_id)}
        response = self.send_rpc_command("get_job_history", params)
        return self.decode_response(response, "result")

    def get_num_special_tasks(
        self, id_list=[], host_id_list=[], start_time_gt=None, end_time_lt=None
    ):
        """Get attributes of the special tasks specified.
        Args:
            id_list: List of special task id's,
            host_id_list: List of AFE host id's
            start_time_gt(int): Seconds timestamp of a filter to DUT tasks by
                start time.
            end_time_lt(int): Seconds timestamp of a filter to DUT tasks by
                end time.
        Returns:
            Number of tasks that match the given filters ( special_tasks in AFE
            vernacular ).
        """
        params = {}
        if id_list:
            assert isinstance(id_list, list)
            params = {"id__in": id_list}
        if host_id_list:
            assert isinstance(host_id_list, list)
            params = {"host__in": host_id_list}

        if start_time_gt:
            params["start_time"] = str(
                datetime.fromtimestamp(start_time_gt).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        if end_time_lt:
            params["end_time"] = str(
                datetime.fromtimestamp(end_time_lt).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        response = self.send_rpc_command("get_num_special_tasks", params)
        return self.decode_response(response, "result")

    def get_special_tasks(
        self,
        id_list=[],
        host_id_list=[],
        query_start=None,
        query_limit=None,
        start_time_gt=None,
        end_time_lt=None,
        sort_by_most_recent=True,
    ):
        """Get attributes of the special tasks specified.

        Args:
            id_list: A list of special task id to be retrieved.
            host_id_list: A list of AFE host id's to filter results by.
            query_start(int): Parameter specifying index on where to start when
                returning paged results.
            query_limit(int): Upper limit on number of results to return.
            start_time_gt(int): Seconds timestamp of a filter to DUT tasks by
                start time.
            end_time_lt(int): Seconds timestamp of a filter to DUT tasks by
                end time.
        Returns:
            A list of dict. The key, value of the dict is the special task
            attribute name and the value.
        """
        params = {}

        if id_list:
            assert isinstance(id_list, list)
            params["id__in"] = id_list

        if host_id_list:
            assert isinstance(host_id_list, list)
            params["host__in"] = host_id_list

        if query_start is not None and query_limit is not None:
            params["query_start"] = query_start
            params["query_limit"] = query_limit

        if start_time_gt:
            params["start_time"] = str(
                datetime.fromtimestamp(start_time_gt).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        if end_time_lt:
            params["end_time"] = str(
                datetime.fromtimestamp(end_time_lt).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

        if sort_by_most_recent:
            params["sort_by"] = ["-id"]

        response = self.send_rpc_command("get_special_tasks", params)
        return self.decode_response(response, "result")

    def get_num_host_queue_entries(self, job_id=None, host_id=None):
        """
            Get number of HQE's that match given query parameters.
        Args:
            job_id(int): The job id which HQEs associated with.
            host_id(int): The AFE DUT id which HQEs associated with.
        Returns:
            An integer.
        """
        params = {}

        if job_id:
            params["job__id"] = job_id
        if host_id:
            params["host__id"] = host_id

        response = self.send_rpc_command("get_num_host_queue_entries", params)
        return self.decode_response(response, "result")

    def get_host_queue_entries(
        self,
        job_id=None,
        host_id=None,
        query_start=None,
        query_limit=None,
        sort_by=None
    ):
        """Get attributes of all HQE of given id.

        Args:
            job_id(int): The job id which HQEs associated with.
            host_id(int): The AFE DUT id which HQEs associated with.
            query_start(int): Parameter specifying index on where to start when
                returning paged results.
            query_limit(int): Upper limit on number of results to return.
            sort_by: parameter for specifying jobs ordering.

        Returns:
            A list of dict. The dict is the information about the HQE.
        """
        params = {}

        """
        For ordering the afe_jobs table, we add the prefix to sort_by.
        """
        if sort_by and sort_by.startswith("-"):
            params["sort_by"] = ["-afe_jobs.%s" % (sort_by[1:])]
        elif sort_by:
            params["sort_by"] = ["afe_jobs.%s" % sort_by]

        if query_start is not None and query_limit is not None:
            params["query_start"] = query_start
            params["query_limit"] = query_limit

        if job_id:
            params["job__id"] = job_id
        if host_id:
            params["host__id"] = host_id

        response = self.send_rpc_command("get_host_queue_entries", params)
        result = self.decode_response(response, "result")
        error = self.decode_response(response, "error")

        return result, error

    def run_suite(
        self,
        board,
        build,
        builds,
        suite,
        suite_timeout_mins,
        pool=None,
        model=None,
        suite_args=None,
        test_args=None,
    ):
        """Request AFE run a given suite.

        Args:
            board (string): Software build to run, e.g. octopus
            build (string): Software version to run e.g. R73-11647.24.0
            builds (list): Software versions to run e.g. R73-11647.24.0
            suite (string): Test suite to run e.g. cts_P
            suite_timeout_mins (integer, optional): Number of minutes until the
                suite times out.
            pool (string, optional): Pool label to target suite on.
            model (string, optional): Specific model to run on e.g. phaser
            suite_args (string, optional): Defaults to None. delimited
                key=val pairs passed to suite control file.
            test_args (string, optional): Defaults to None.  delimited
                key=val pairs passed to test control file.
        Returns:
            Tuple (int, string): The first element will be an int representing
            ID of the created suite job. The second value is an error message.
            Exactly one of the values will ever not be None. A None ID implies
            failure of the AFE call-through.
        """
        params = {
            "board": board,
            "builds": builds,
            "name": suite,
            "pool": pool,
            "run_prod_code": False,
            "test_source_build": build,
            "wait_for_results": True,
            "suite_args": suite_args,
            "test_args": test_args,
            "job_retry": True,
            "max_retries": sys.maxsize,
            "model": model,
            "timeout_mins": suite_timeout_mins,
            "max_runtime_mins": suite_timeout_mins,
        }
        response = self.send_rpc_command("create_suite_job", params)
        result = self.decode_response(response, "result")
        error = self.decode_response(response, "error")

        return result, error

    def enroll_duts(self, ip_addresses):
        """
        Enroll dut by ip addresses. 
        If more than one ip addresses need to be enrolled, using multiprocessing to do.
        Otherwise, just call the enroll_dut directly.
        """
        _LOGGER.debug("Enroll hosts %s", ip_addresses)
        ip_count = len(ip_addresses)
        if ip_count > 1:
            p = multiprocessing.Pool(20)
            p.map(enroll_dut, ip_addresses)
            p.close()
            p.join()
        elif ip_count == 1:
            enroll_dut(ip_address=ip_addresses[0])
        else:
            logging.error("We can't enroll duts without any ip address")

    def unenroll_duts(self, ip_addresses):
        hosts = self.get_connected_devices()
        for host in hosts:
            hostname = host.get("hostname")
            params = {"id": host.get("id")}
            _LOGGER.error(params)
            if hostname in ip_addresses:
                response = self.send_rpc_command("delete_host", params)
                _LOGGER.error(response)

    def abort_host_queue_entries(self, job_ids):
        response = self.send_rpc_command(
            "abort_host_queue_entries", {"job__id__in": job_ids}
        )
        return self.decode_response(response, "result")

    def _package_edit_action_results(self, response):
        """
        Add/remove attribute label actions are currently implemented by
        calling an AFE endpoint that will return (True, <message>)
        on success cases, but not the same format on failure cases. This
        logic packages failure cases in the same format.

        TO-DO: This logic should disappear when the underlying AFE calls
        are no longer relied upon.
        """
        if self.decode_response(response, "result"):
            return self.decode_response(response, "result")
        else:
            return (False, self.decode_response(response, "error")["message"])

    def add_label_to_host(self, dut_hostname, label):
        """Add label to the specified DUT.

        Args:
            dut_hostname(string): hostname (IP) of targeted DUT.
            label (string): Label to be added.
        Returns:
            A tuple with first value indicating whether action succeeded and
            the second value a message summarizing the result (+ reason for
            failure, if action failed).
        """
        response = self.send_rpc_command(
            "add_moblab_label",
            {"ipaddress": dut_hostname, "label_name": label},
        )
        return self._package_edit_action_results(response)

    def remove_label_from_host(self, dut_hostname, label):
        """
            Removes label from the specified DUT.
        Args:
            dut_hostname(string): hostname (IP) of targeted DUT.
            label (string): Label to be removed.
        Returns:
            A tuple with first value indicating whether action succeeded and
            the second value a message summarizing the result (+ reason for
            failure, if action failed).
        """
        response = self.send_rpc_command(
            "remove_moblab_label",
            {"ipaddress": dut_hostname, "label_name": label},
        )
        return self._package_edit_action_results(response)

    def add_attribute_to_host(self, dut_hostname, key, value):
        """
            Adds attribute key:value to the specified DUT.
        Args:
            dut_hostname(string): hostname (IP) of targeted DUT.
            key (string): Key of attribute to be added.
            value (string): Value of attribute to be added.
        Returns:
            A tuple with first value indicating whether action succeeded and
            the second value a message summarizing the result (+ reason for
            failure, if action failed).
        """
        response = self.send_rpc_command(
            "set_host_attrib",
            {"ipaddress": dut_hostname, "attribute": key, "value": value},
        )
        return self._package_edit_action_results(response)

    def remove_attribute_from_host(self, dut_hostname, key):
        """
            Removes attribute ( referenced by key ) from the specified DUT.
        Args:
            dut_hostname(string): hostname (IP) of targeted DUT.
            key (string): Key of attribute to be removed.
        Returns:
            A tuple with first value indicating whether action succeeded and
            the second value a message summarizing the result (+ reason for
            failure, if action failed).
        """
        response = self.send_rpc_command(
            "delete_host_attrib",
            {
                "ipaddress": dut_hostname,
                "attribute": key,
            },
        )
        return self._package_edit_action_results(response)

    def reverify_host(self, hostnames):
        """
            Sets off reverify job on DUT of given ID.
        Args:
            hostnames([string]): hostnames of DUTs.
        """
        response = self.send_rpc_command(
            "reverify_hosts", {"hostname__in": hostnames}
        )
        return self.decode_response(response, "result")

    def repair_host(self, host_id):
        """Set off repair job on DUT of given ID.

        Args:
            host_id(int): ID of DUT in AFE backend.
        """
        response = self.send_rpc_command("repair_hosts", {"id": host_id})
        return self.decode_response(response, "result")

    def get_cloud_storage_info(self):
        """Get cloud configuration info from AFE.
        Returns:
            A dict of cloud configuration info  ( specifically,
            'gs_access_key_id', 'gs_secret_access_key',
            'image_storage_server' )
        """
        response = self.send_rpc_command("get_cloud_storage_info", {})
        return self.decode_response(response, "result")

    def get_dut_wifi_info(self):
        """
            Gets DUT wifi info from AFE.
        Returns:
            A dict of DUT wifi info  ( specifically, 'dut_wifi_name,
            'dut_wifi_password' )
        """
        response = self.send_rpc_command("get_dut_wifi_info", {})
        return self.decode_response(response, "result")

    def _format_configuration_dict(
        self,
        is_cloud_enabled=True,
        gs_access_key_id="",
        gs_secret_access_key="",
        image_storage_server="",
        dut_wifi_name=None,
        dut_wifi_password="",
    ):
        """
            Helper method for returning params shared between calls to set
            config and validate cloud config. Will assume that submissions
            are only for either DUT WIFI *or* cloud configurations.
        Args:
            is_cloud_enabled (boolean): True iff user has checked 'integrate
                with cloud' on UI
            gs_access_key_id (string): boto ID string
            gs_secret_access_key (string): boto secret string
            image_storage_server (string): GCS bucket URL
            dut_wifi_name (string): Wifi name for DUTs
            dut_wifi_password (string): Wifi password for DUTs
        Returns:
            A dictionary of cloud configuration parameters.
        """
        configuration_dict = {}

        if dut_wifi_name:
            configuration_dict["wifi_info"] = {
                "wifi_dut_ap_name": dut_wifi_name,
                "wifi_dut_ap_pass": dut_wifi_password,
            }
        else:
            configuration_dict["cloud_storage_info"] = {
                "is_cloud_enabled": is_cloud_enabled,
                "gs_access_key_id": gs_access_key_id,
                "gs_secret_access_key": gs_secret_access_key,
                "image_storage_server": image_storage_server,
                "results_storage_server": "",
                # AFE backend services configuration of other values in
                # addition to cloud configs, but Moblab only needs to change
                # these values, so this value is always False.
                "use_existing_boto_file": False,
            }

        return configuration_dict

    def set_configuration_info(
        self,
        is_cloud_enabled=True,
        gs_access_key_id="",
        gs_secret_access_key="",
        image_storage_server="",
        dut_wifi_name=None,
        dut_wifi_password="",
    ):
        """
            Applies given configuration values to AFE.
        Args:
            is_cloud_enabled (boolean): True iff user has checked 'integrate
                with cloud' on UI
            gs_access_key_id (string): boto ID string
            gs_secret_access_key (string): boto secret string
            image_storage_server (string): GCS bucket URL
            dut_wifi_name (string): Wifi name for DUTs
            dut_wifi_password (string): Wifi password for DUTs
        Returns:
            A boolean, true IFF application of new cloud configurations
            succeeded.
        """
        response = self.send_rpc_command(
            "submit_wizard_config_info",
            self._format_configuration_dict(
                is_cloud_enabled,
                gs_access_key_id,
                gs_secret_access_key,
                image_storage_server,
                dut_wifi_name,
                dut_wifi_password,
            ),
        )

        response = self.decode_response(response, "result")
        if "status_ok" in response and response["status_ok"]:
            return True
        else:
            return False

    def validate_cloud_storage_info(
        self, gs_access_key_id, gs_secret_access_key, image_storage_server
    ):
        """Call through to AFE to check validity of boto and bucket
            configuration, returns true iff configurations are valid, and if
            false returns a reason that configuration is not valid.
        Args:
            gs_access_key_id (string): boto ID string
            gs_secret_access_key (string): boto secret string
            image_storage_server (string): GCS bucket URL
        Returns:
            A tuple (boolean, string).
        """
        response = self.send_rpc_command(
            "validate_cloud_storage_info",
            self._format_configuration_dict(
                gs_access_key_id=gs_access_key_id,
                gs_secret_access_key=gs_secret_access_key,
                image_storage_server=image_storage_server,
            ),
        )

        result = self.decode_response(response, "result")
        return result["status_ok"], result.get("status_details", "")

    def set_is_remote_agent_enabled(self, is_enabled=False):
        """Apply given remote agent configuration values to AFE.

        Args:
            is_enabled (bool): enable the remote agent or not
        Returns:
            A boolean, true IFF application of remote agent configurations
            succeeded.
        """
        response = self.send_rpc_command(
            "set_remote_agent_config", {"enabled": is_enabled}
        )

        response = self.decode_response(response, "result")
        return (
            True
            if "status_ok" in response and response["status_ok"]
            else False
        )

    def set_is_remote_command_enabled(self, is_enabled=False):
        """Apply given remote command configuration values to AFE.

        Args:
            is_enabled (bool): enable the remote command or not
        Returns:
            A boolean, true IFF application of remote command configurations
            succeeded.
        """
        response = self.send_rpc_command(
            "set_remote_command_config", {"enabled": is_enabled}
        )

        response = self.decode_response(response, "result")
        return (
            True
            if "status_ok" in response and response["status_ok"]
            else False
        )

    def modify_hosts_lock_state(
        self, new_locked_state, hosts_names, lock_reason
    ):
        """Lock/unlock given DUTs by host name

        Args:
            new_locked_state (bool): lock or unlock DUTs
            hosts_names ([str]): list of host names (DUTs' IPs)
            lock_reason: user facing text message
        Returns:
            A string. Errors message returned by AFE or None.
        """

        connected_duts = self.get_connected_devices()

        _LOGGER.info("Connected DUTs: %s", connected_duts)

        hosts_names = [
            dut["hostname"]
            for dut in connected_duts
            if dut["hostname"] in hosts_names
            and dut["locked"] != new_locked_state
        ]

        params = {
            "host_filter_data": {"hostname__in": hosts_names},
            "update_data": {
                "locked": new_locked_state,
                "lock_reason": lock_reason,
            },
        }
        response = self.send_rpc_command("modify_hosts", params)
        logging.debug(
            "modify_hosts call to modified lock state "
            "request: %s ,response: %s",
            params,
            response,
        )
        return self.decode_response(response, "error")
