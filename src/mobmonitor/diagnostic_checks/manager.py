# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging
LOGGER = logging.getLogger(__name__)

from diagnostic_checks.cloud_storage_speedtest import CloudStorageSpeedTest
from diagnostic_checks.disk_info import DiskInfo
from diagnostic_checks.diagnostic_error import DiagnosticError

class DiagnosticCheckManager:
    """
    Manages access to diagnostic checks. A diagnostic check
    is an on demand test that gathers some information
    on the system and returns a free-form text response back
    to the user. They shouldn't perform any changes to the
    system, just gather information.

    Diagnostic checks are organized by a category (such as
    network, cloud storage, disk), and then specific diagnostics
    under those categories (network - speed, disk - free space).

    Diagnostic check interface is defined by AbstractDiagnosticCheck,
    and any new diagnostics must inherit from this class.
    """

    # The list of diagnostic checks to provide
    # All checks must inherit from AbstractDiagnosticCheck
    CHECKS = [
        CloudStorageSpeedTest,
        DiskInfo,
    ]

    def __init__(self):
        self.diagnostic_checks = {}

    def init_checks(self):
        """
        Creates instances of all the supported checks
        """
        for check in self.CHECKS:
            self._add_check(check())

    def _add_check(self, check):
        if check.category not in self.diagnostic_checks:
            self.diagnostic_checks[check.category] = {}
        self.diagnostic_checks[check.category][check.name] = check

    def list_diagnostic_checks(self):
        """
        Lists the available diagnostic checks

        Return a list of checks organized by category, then check:
            [
                {
                    'category': 'category 1',
                    'checks': [{
                        'name': 'a test under category 1',
                        'description': '...'
                    }]
                },
                {
                    'category': 'category 2',
                    'checks': [{
                        'name': 'a test under category 2',
                        'description': '...'
                    }]
                }
            ]
        """
        check_list = []
        for category in self.diagnostic_checks:
            category_entry = {'category': category}
            category_checks = []
            for name in self.diagnostic_checks[category]:
                description = self.diagnostic_checks[category][name].description
                category_checks.append({
                    'name': name,
                    'description': description
                })
            category_entry['checks'] = category_checks
            check_list.append(category_entry)
        return check_list

    def run_diagnostic_check(self, category, name):
        """
        Runs the check specified by it's category and name

        Args:
            category: the category of the check to run
            name: the name of the check to run
        Return:
            A freeform text response containing the results of the diagnostic
        Raises:
            DiagnosticError if the check is not found, or encounters an error
        """
        try:
            LOGGER.info('running diagnostic %s %s' % (category, name))
            check = self.diagnostic_checks[category][name]
            if check is None:
                raise DiagnosticError('Check not found')
            return check.run()
        except KeyError:
            raise DiagnosticError('Check not found')
        except DiagnosticError as e:
            LOGGER.error('failed to run diagnostic check: %s', str(e))
            raise e
