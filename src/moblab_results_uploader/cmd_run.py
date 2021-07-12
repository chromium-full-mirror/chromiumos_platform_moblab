# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""The implementation of subcommand `run`."""

import argparse
import asyncio
import datetime
import functools
import logging  # pylint: disable=cros-logging-import
import os
import shutil
import stat
import yaml

from uploader_configuration import UploaderConfiguration
from moblab_common import afe_connector
from moblab_common import config_connector

from moblab_common import moblabrpc_connector
from moblab_common.moblab_configuration_connector import (
    MoblabConfigurationRpcConnector,
)
from moblab_common import result_upload_status_connector
from moblab_common.result_upload_status_connector import Status as UploadStatus
from moblab_common.proto import moblabrpc_pb2

import gs_api_wrapper
import processing_step
import result_dir_status
import result_file_filter
import result_uploader
import test_result_registry as test_result_registry_module

SUB_COMMAND_NAME = "run"
_LOGGER = logging.getLogger("moblab_uploader")

_DEFAULT_UPLOAD_TIMEOUT = datetime.timedelta(days=3)
_DEFAULT_MIN_AGE_TO_UPLOAD = datetime.timedelta(days=0)

_RUN_INTERVAL = datetime.timedelta(minutes=1)

# We cache all live test result objects in a dictionary. The key is the abs
# path of it. We only remove them from the cache when they are removed from
# disk.
_TEST_RESULT_CACHE = {}


async def _enumerate_test_results(test_result_registry):
    """Enumerate and yield all test results registered."""
    for registry_entry in test_result_registry:
        for cls in registry_entry.classes:
            root_dir = registry_entry.root_dir
            for d in root_dir.glob(cls.GLOB_PATTERN):
                test_result = cls.create(
                    root_dir=root_dir, relative_path=d.relative_to(root_dir)
                )
                if test_result:
                    # Give other coroutine chance to run.
                    await asyncio.sleep(0.01)
                    yield _TEST_RESULT_CACHE.setdefault(
                        test_result.abs_path, test_result
                    )


async def _prune_test_result(dry_run, test_result):
    """Check the `test_result` and try to prune it if we should."""
    # In the results directory remove all subdirectores before deleting the
    # root directory as that is where the marker file is assumed to be.
    # Leaving the marker file to as late as possible in the process ensures
    # that cleanup will resume in the event of a process crash.
    try:
        _LOGGER.debug("Removing test result %s", test_result)
        if dry_run:
            _LOGGER.debug("DRYRUN: Removed: %s", test_result)

        def log_error(func, path, _):
            "Log prune failures, catching them preventing them being raised."
            # Even the chmod failed to fix the issue, just log and leave
            # the problem behind, nothing we can do.
            _LOGGER.error("PRUNE: Failed to remove file %s", path)

        def remove_readonly(func, path, _):
            "Clear the readonly bit and re-attempt the removal"
            _LOGGER.error("PRUNE: Fixing read only %s", path)
            try:
                os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
            # If the process is not the owner of the file then just give up
            # with out crashing.
            except PermissionError as e:
                _LOGGER.exception(e)
            else:
                # Successful chmod on the problem file, retry the delete.
                func(path, onerror=log_error)

        # To be safe - delete all the subdirs first, then the whole directory
        # which will leave the marker file to last.
        # example structure
        #  1-moblab/
        #       .uploader_status
        #       192.168.238.100/
        #           status.log
        #            debug/

        _, topdirs, _ = next(os.walk(test_result.abs_path), [])
        # In the example this will delete directory 192.168.23.100 and all
        # the subdirs, it will also delete any sibling directores - there are
        # none in this example.
        for topdir in topdirs:
            shutil.rmtree(
                os.path.join(test_result.abs_path, topdir),
                onerror=remove_readonly,
            )
        # This will remove 1-moblab and all its subdirs
        shutil.rmtree(test_result.abs_path, onerror=remove_readonly)
        del _TEST_RESULT_CACHE[test_result.abs_path]

        # Update upload-status after result's deletion
        _result_upload_status_store = (
            result_upload_status_connector.ResultUploadStatusConnector()
        )
        _result_upload_status_store.set_job_upload_status(
            test_result.id, result_upload_status_connector.Status.DELETED
        )

        _LOGGER.debug("Removed: %s", test_result)
    except Exception as e:
        _LOGGER.exception(e)


async def _async_prune(args, registry, configuration):
    """Scan and prune all EXPIRED test results."""
    status_checker = result_dir_status.ResultStatusChecker(
        min_age_to_upload=args.min_age_to_upload,
        configuration=configuration,
    )
    status_filter = result_dir_status.StatusFilter(
        result_dir_status.Status.EXPIRED
    )

    # Steps needed to prune a result directory:
    # check status -> for each EXPIRED directories -> prune it.
    status_checker.next_step = status_filter.filter
    status_filter.next_step = functools.partial(
        _prune_test_result, args.dry_run
    )

    while True:
        async for test_result in _enumerate_test_results(registry):
            await status_checker.check(test_result)

        if args.once:
            break
        await asyncio.sleep(_RUN_INTERVAL.total_seconds())


async def _resume_aborted_uploading(args, registry, status_checker, uploader):
    """Resume the uploading of last run.

    This script indented to be run as a daemon. When the daemon interrupted for
    any reason, it aborts the current uploading job and leave it in UPLOADING
    status. When restart the daemon, we resume it and eventually change the
    state to allow future processing (pruning, or re-uploading).

    This is only for one time before we start the main loop.
    """
    # We hook up a status filter which only interests in directories UPLOADING
    # state, and an uploading context which doesn't change directory status
    # before uploading.
    uploader.uploading_context = result_uploader.UploadingContext(
        gs_bucket=args.gs_api.bucket_name,
        dry_run=args.dry_run,
        resume_aborted=True,
    )
    status_filter = result_dir_status.StatusFilter(
        result_dir_status.Status.UPLOADING
    )
    status_checker.next_step = status_filter.filter
    status_filter.next_step = uploader.try_upload_dir

    _LOGGER.info("First scan for aborted uploading jobs.")
    async for test_result in _enumerate_test_results(registry):
        await status_checker.get_last_status(test_result)


async def _run_upload_status_backfill_migration(registry, status_checker):
    # 0. Get all jobs with status;
    jobs = moblabrpc_connector.MoblabRpcConnector.get_jobs(
        query_start=0, query_limit=10000
    )

    # 1. If exist at least one record skip migration;
    _LOGGER.info("Checking whether job upload status backfill is needed.")
    if not jobs or any(
        job.upload_state.status
        != moblabrpc_pb2.Job.UploadStatus.UPLOAD_STATUS_UNKNOWN
        for job in jobs
    ):
        return

    _LOGGER.info("Migrating jobs upload stutuses to moblab db.")

    # 2. Initialize upload status based on completed/not completed job status;
    jobs_upload_status = {
        job.job_id: UploadStatus.UPLOADED
        if _is_job_finished(job.status)
        else UploadStatus.NOT_READY
        for job in jobs
    }

    # 3. Iterate over existing dirs
    #    - Update jobs based on status;
    async for test_result in _enumerate_test_results(registry):
        if (
            test_result.id in jobs_upload_status
            and jobs_upload_status[test_result.id] == UploadStatus.UPLOADED
        ):
            upload_file_status = await result_dir_status._load_status(
                test_result
            )
            if upload_file_status == result_dir_status.Status.NOT_READY:
                jobs_upload_status[test_result.id] = UploadStatus.NOT_READY

            elif upload_file_status == result_dir_status.Status.READY:
                jobs_upload_status[test_result.id] = UploadStatus.QUEUED

            elif upload_file_status == result_dir_status.Status.UPLOADING:
                jobs_upload_status[test_result.id] = UploadStatus.UPLOADING

            elif upload_file_status == result_dir_status.Status.UPLOADED:
                jobs_upload_status[test_result.id] = UploadStatus.UPLOADED

            elif upload_file_status == result_dir_status.Status.EXPIRED:
                jobs_upload_status[test_result.id] = UploadStatus.DELETED

    # 4. Save back all the upload statuses;
    upload_status_store = (
        result_upload_status_connector.ResultUploadStatusConnector()
    )
    for job_id in jobs_upload_status:
        upload_status_store.set_job_upload_status(
            job_id, jobs_upload_status[job_id]
        )


def _is_job_finished(job_status):
    # SUCCESS = 5
    # FAILED = 6
    # ABORTED = 7
    return job_status in {5, 6, 8}


async def _async_upload(args, registry, configuration):
    """Scan and upload all 'READY' test results."""
    status_checker = result_dir_status.ResultStatusChecker(
        min_age_to_upload=args.min_age_to_upload,
        configuration=configuration,
    )
    uploader = result_uploader.Uploader(
        timeout=datetime.timedelta(minutes=60),
        gs_api=args.gs_api,
        notify_uploaded=result_file_filter.mark_files_uploaded,
    )
    file_filter = result_file_filter.ResultFileFilter(
        filter_config=args.uploading_filter_config
    )
    uploader.next_step = file_filter.filter_files
    file_filter.next_step = uploader.uploading_queue.put

    consumer = asyncio.ensure_future(
        uploader.upload_files(args.jobs, args.dry_run)
    )

    await _run_upload_status_backfill_migration(registry, status_checker)

    # Finish unfinished jobs of last run.
    await _resume_aborted_uploading(args, registry, status_checker, uploader)

    # Then start the main loop.
    # We hook up a new status filter which only interests in directories in
    # READY state, and a new uploading context which changes directory state to
    # UPLOADING before uploading.
    status_filter = result_dir_status.StatusFilter(
        result_dir_status.Status.READY
    )
    status_checker.next_step = status_filter.filter
    status_filter.next_step = uploader.try_upload_dir

    uploader.uploading_context = result_uploader.UploadingContext(
        gs_bucket=args.gs_api.bucket_name,
        dry_run=args.dry_run,
        resume_aborted=False,
    )
    _LOGGER.info("Main uploading scan loop started.")
    while True:
        async for test_result in _enumerate_test_results(registry):
            await status_checker.check(test_result)

        if args.once:
            break
        await asyncio.sleep(_RUN_INTERVAL.total_seconds())

    consumer.cancel()


def _accessible_file_type(file_path):
    """Check if input is an accessible file."""
    if not file_path:
        raise argparse.ArgumentTypeError("No value specified.")

    try:
        with open(file_path):
            pass
        return file_path
    except (FileNotFoundError, PermissionError) as err:
        raise argparse.ArgumentTypeError(err)


def add_arguments(parent_parser):
    """Add arguments for subcommand 'run'.

    Args:
        parent_parser: The argparse.ArgumentParser object to add arguments.
    """
    parser = parent_parser.add_parser(
        SUB_COMMAND_NAME,
        help="Scan, upload and prune the test result directories.",
    )
    parser.add_argument(
        "--once", action="store_true", help="Just run once and exit."
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Dry run mode: just print out directories processed. Only valid "
        "when specified with option --once.",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=1,
        help="Allow N jobs run simultaneously to work.",
    )
    parser.add_argument(
        "--gs-bucket",
        default=config_connector.MoblabConfigConnector(
            afe_connector.AFEConnector()
        ).get_cloud_bucket(),
        help='The Google Storage Bucket to upload (without "gs://" prefix). '
        "Default is reading from Autotest config file, i.e. %(default)s",
    )

    parser.add_argument(
        "--credentials-file",
        default=os.environ.get(gs_api_wrapper.ENV_GOOGLE_APP_CREDENTIALS, ""),
        type=_accessible_file_type,
        help="Google cloud application credentials file. Default is the value "
        'of environment variable {}, i.e. "%(default)s".'.format(
            gs_api_wrapper.ENV_GOOGLE_APP_CREDENTIALS
        ),
    )

    parser.add_argument(
        "--timeout-days",
        type=lambda x: datetime.timedelta(days=float(x)),
        default=_DEFAULT_UPLOAD_TIMEOUT,
        dest="upload_timeout",
        help="The timeout time in days (can be a float number) to give up the "
        "uploading (default: %(default)s).",
    )
    parser.add_argument(
        "--min-age-to-upload",
        type=lambda x: datetime.timedelta(days=float(x)),
        default=_DEFAULT_MIN_AGE_TO_UPLOAD,
        help="Minimum job age in days (can be a float number) before a result "
        "can be uploaded, but not removed from local storage "
        "(default: %(default)s).",
    )

    parser.set_defaults(
        func=run, post_parse_args=functools.partial(_post_parse_args, parser)
    )


def _post_parse_args(arg_parser, args):
    """massage input arguments."""
    _LOGGER.debug("Input arguments: %s", args)
    if not args.gs_bucket:
        gs_bucket = config_connector.MoblabConfigConnector(
            afe_connector.AFEConnector()
        ).get_cloud_bucket()
        if not gs_bucket:
            raise Exception("No GS bucket specified or configured.")
    else:
        gs_bucket = args.gs_bucket

    try:
        args.gs_api = gs_api_wrapper.GsApiWrapper(
            args.gs_bucket, args.credentials_file
        )
    except gs_api_wrapper.GsAccessError as err:
        arg_parser.error(str(err))

    delattr(args, "credentials_file")
    delattr(args, "gs_bucket")

    if (
        args.dry_run
    ):  # It makes no sense to dry run a daemon, so just run once.
        args.once = True


async def _async_config_poll(args, configuration: UploaderConfiguration):
    """Polls the config changes and updates the configuration object."""
    while True:
        results_retention_time = (
            MoblabConfigurationRpcConnector.get_local_results_retention_time()
        )
        if results_retention_time:
            configuration.set_min_age_to_prune(results_retention_time)

        await asyncio.sleep(_RUN_INTERVAL.total_seconds())


def run(args, test_result_registry=None):
    """Main logic to scan, upload and prune the test results.

    Args:
        args: The command line arguments specified.
        test_result_registry: A list of TestResultRegisteryEntry which has
            needed test result directory information.
    """
    _LOGGER.info("Starting to scan, upload and prune test results.")
    _LOGGER.setLevel(logging.DEBUG)

    registry = test_result_registry or test_result_registry_module.REGISTRY
    loop = asyncio.get_event_loop()

    configuration = UploaderConfiguration()
    try:
        loop.run_until_complete(
            asyncio.gather(
                _async_config_poll(args, configuration),
                _async_upload(args, registry, configuration),
                _async_prune(args, registry, configuration),
            )
        )
    except KeyboardInterrupt:
        _LOGGER.info("Program is terminated by user.")
        pass
    finally:
        _LOGGER.info("Shutting down. Bye!")
        loop.close()
