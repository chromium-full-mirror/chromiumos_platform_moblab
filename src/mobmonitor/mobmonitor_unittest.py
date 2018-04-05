# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unittests for the main Mob* Monitor script."""

from __future__ import print_function

import json
import os
import unittest
import mock

import mobmonitor

from checkfile import manager
from util import osutils


class MockCheckFileManager(object):
  """Mock CheckFileManager object that returns 'real' responses for testing."""

  def __init__(self):
    failed_check = manager.HEALTHCHECK_STATUS('hc1', False, 'Failed', [])

    self.service_statuses = [
        manager.SERVICE_STATUS('service1', True, []),
        manager.SERVICE_STATUS('service2', False, [failed_check])]

    self.action_info = manager.ACTION_INFO('DummyAction', '', ['x'], {})

  def GetServiceList(self):
    """Mock GetServiceList response."""
    return ['test_service_1', 'test_service_2']

  def GetStatus(self, service=None):
    """Mock GetStatus response."""
    if service is None:
      return self.service_statuses

    return self.service_statuses[0]

  def ActionInfo(self, _service, _healthcheck, _action):
    """Mock ActionInfo response."""
    return self.action_info

  def RepairService(self, _service, _healthcheck, _action, _args, _kwargs):
    """Mock RepairService response."""
    return self.service_statuses[0]


class MobMonitorRootTest(unittest.TestCase):
  """Unittests for the MobMonitorRoot."""

  STATICDIR = 'static'

  def _mock_checkfile_manager(self):
      mock_checkfile_manager = mock.MagicMock()

      failed_check = manager.HEALTHCHECK_STATUS('hc1', False, 'Failed', [])
      service_statuses = [
          manager.SERVICE_STATUS('service1', True, []),
          manager.SERVICE_STATUS('service2', False, [failed_check])]
      mock_checkfile_manager.service_statuses = service_statuses

      action_info = manager.ACTION_INFO('DummyAction', '', {'x': 'x'})
      mock_checkfile_manager.action_info = action_info

      mock_checkfile_manager.GetServiceList.return_value = [
          'test_service_1', 'test_service_2']

      def status_side_effect(service=None):
          if service is None:
              return service_statuses
          else:
              return service_statuses[0]

      mock_checkfile_manager.GetStatus.side_effect = status_side_effect
      mock_checkfile_manager.ActionInfo.return_value = action_info
      mock_checkfile_manager.RepairService.return_value = service_statuses[0]

      return mock_checkfile_manager

  def _mock_diagnostic_manager(self):
    mock_diagnostic_manager = mock.MagicMock()
    diagnostic_checks = [{
      'category': 'test category',
      'checks': [{
        'name': 'test check',
        'description': 'test check'
      }]
    }]

    check_result = 'test diagnostic result'

    mock_diagnostic_manager.list_diagnostic_checks.return_value = \
        diagnostic_checks
    mock_diagnostic_manager.run_diagnostic_check.return_value = check_result

    return mock_diagnostic_manager

  def setUp(self):
    """Setup directories expected by the Mob* Monitor."""
    self.staticdir = self.STATICDIR
    self.mock_checkfile_manager = self._mock_checkfile_manager()
    self.mock_diagnostic_manager = self._mock_diagnostic_manager()

    patch_os = mock.patch('mobmonitor.os')
    self.addCleanup(patch_os.stop)
    self.mock_os = patch_os.start()

    self.mock_os.path.exists.return_value = True

    self.root = mobmonitor.MobMonitorRoot(
        self.mock_checkfile_manager, self.mock_diagnostic_manager,
        staticdir=self.staticdir)


  def testGetServiceList(self):
    """Test the GetServiceList RPC."""
    cfm = self.mock_checkfile_manager
    self.assertEqual(cfm.GetServiceList(),
        json.loads(self.root.GetServiceList()))

  def testGetStatus(self):
    """Test the GetStatus RPC."""
    cfm = self.mock_checkfile_manager

    # Test the result for a single service.
    status = cfm.service_statuses[0]
    expect = {'service': status.service, 'health': status.health,
              'healthchecks': []}
    self.assertEquals([expect], json.loads(self.root.GetStatus(status.service)))

    # Test the result for multiple services.
    status1, status2 = cfm.service_statuses
    check = status2.healthchecks[0]
    expect = [{'service': status1.service, 'health': status1.health,
               'healthchecks': []},
              {'service': status2.service, 'health': status2.health,
               'healthchecks': [{'name': check.name, 'health': check.health,
                                 'description': check.description,
                                 'actions': []}]}]
    self.assertEquals(expect, json.loads(self.root.GetStatus()))

  def testActionInfo(self):
    """Test the ActionInfo RPC."""
    cfm = self.mock_checkfile_manager

    expect = {'action': 'DummyAction', 'info': '', 'params': {'x': 'x'}}
    self.assertEquals(expect,
                      json.loads(self.root.ActionInfo('service2',
                                                 'dummy_healthcheck',
                                                 'DummyAction')))

  def testRepairService(self):
    """Test the RepairService RPC."""
    cfm = self.mock_checkfile_manager

    status = cfm.service_statuses[0]
    expect = {'service': status.service, 'health': status.health,
              'healthchecks': []}
    string_params = '{"a":1}'
    self.assertEquals(expect,
                      json.loads(self.root.RepairService('dummy_service',
                                                    'dummy_healthcheck',
                                                    'dummy_action',
                                                    string_params)))

  def testListDiagnosticChecks(self):
    """Test the ListDiagnosticChecks RPC."""
    expect = self.mock_diagnostic_manager.list_diagnostic_checks()
    self.assertEquals(expect,
        json.loads(self.root.ListDiagnosticChecks()))

  def testRunDiagnosticCheck(self):
    """Test the RunDiagnosticCheck RPC."""
    expect = {
      'result': 'test diagnostic result'
    }
    self.assertEquals(expect,
        json.loads(self.root.RunDiagnosticCheck('testcategory', 'testname')))


if __name__ == '__main__':
    unittest.main()
