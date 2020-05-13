# -*- coding: utf-8 -*-
# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unittests for Mob* Monitor checkfile manager."""

import imp
import mock
import os
import subprocess
import time
import threading
import unittest
import mock

from cherrypy.process import plugins
import manager

# Test health check and related attributes
class TestHealthCheck(object):
  """Test health check."""

  def Check(self):
    """Stub Check."""
    return 0

  def Diagnose(self, _errcode):
    """Stub Diagnose."""
    return ('Unknown Error.', [])


class TestHealthCheckHasAttributes(object):
  """Test health check with attributes."""

  CHECK_INTERVAL_SEC = 10

  def Check(self):
    """Stub Check."""
    return 0

  def Diagnose(self, _errcode):
    """Stub Diagnose."""
    return ('Unknown Error.', [])


class TestHealthCheckUnhealthy(object):
  """Unhealthy test health check."""

  def __init__(self):
    self.x = -1

  def Check(self):
    """Stub Check."""
    return self.x

  def Diagnose(self, errcode):
    """Stub Diagnose."""
    if errcode == -1:
      return ('Stub Error.', [self.Repair()])
    return ('Unknown Error.', [])

  class Repair():
    action='Repair'

    def run(self, params):
      pass

class RepairUnhealthyCheck():
    action='Repair'
    info='Repair Info'
    param_info={}

    def __init__(self, healthCheck):
      self.healthCheck = healthCheck

    def run(self, params):
      self.healthCheck.x = 0


class TestHealthCheckMultipleActions(object):
  """Unhealthy check with many actions that have different parameters."""

  def __init__(self):
    self.x = -1

  def Check(self):
    """Stub Check."""
    return self.x

  def Diagnose(self, errcode):
    """Stub Diagnose."""
    if errcode == -1:
      return ('Stub Error.', [self.NoParams(), self.Params()])
    return ('Unknown Error.', [])

  class NoParams():
    action='NoParams'
    info="""NoParams Action."""
    param_info={}
    def run(self, params):
        pass

  # pylint: disable=unused-argument
  class Params():
    action='Params'
    info="""Params Action."""
    param_info={'x':'y'}
    def run(self, params):
        pass
    # self.x = 0
  # pylint: enable=unused-argument


class TestHealthCheckQuasihealthy(object):
  """Quasi-healthy test health check."""

  def Check(self):
    """Stub Check."""
    return 1

  def Diagnose(self, errcode):
    """Stub Diagnose."""
    if errcode == 1:
      return ('Stub Error.', [self.RepairStub])
    return ('Unknown Error.', [])

  def RepairStub(self):
    """Stub repair action."""


class TestHealthCheckBroken(object):
  """Broken test health check."""

  def Check(self):
    """Stub Check."""
    raise ValueError()

  def Diagnose(self, _errcode):
    """A broken Diagnose function. A proper return should be a pair."""
    raise ValueError()


class TestAction:
    action = 'TestAction'
    info = """Just a test."""
    param_info = {}

    def run(self, params):
        return true


TEST_SERVICE_NAME = 'test-service'
TEST_MTIME = 100
TEST_EXEC_TIME = 400
CHECKDIR = '.'

# Strings that are used to mock actual check modules.
CHECKFILE_MANY_SIMPLE = '''
SERVICE = 'test-service'

class MyHealthCheck2(object):
  def Check(self):
    return 0

  def Diagnose(self, errcode):
    return ('Unknown error.', [])

class MyHealthCheck3(object):
  def Check(self):
    return 0

  def Diagnose(self, errcode):
    return ('Unknown error.', [])

class MyHealthCheck4(object):
  def Check(self):
    return 0

  def Diagnose(self, errcode):
    return ('Unknown error.', [])
'''

CHECKFILE_MANY_SIMPLE_ONE_BAD = '''
SERVICE = 'test-service'

class MyHealthCheck(object):
  def Check(self):
    return 0

  def Diagnose(self, errcode):
    return ('Unknown error.', [])

class NotAHealthCheck(object):
  def Diagnose(self, errcode):
    return ('Unknown error.', [])

class MyHealthCheck2(object):
  def Check(self):
    return 0

  def Diagnose(self, errcode):
    return ('Unknown error.', [])
'''

NOT_A_CHECKFILE = '''
class NotAHealthCheck(object):
  def NotCheckNorDiagnose(self):
    return -1
'''

ANOTHER_NOT_A_CHECKFILE = '''
class AnotherNotAHealthCheck(object):
  def AnotherNotCheckNorDiagnose(self):
    return -2
'''

ACTION_FILE = '''
class TestAction:
    action = 'TestAction'
    info = """Just a test."""
    param_info = {}

    def run(self, params):
        return true

class AnotherAction:
    action = 'AnotherAction'
    info = """Just a test."""
    param_info = {}

    def run(self, params):
        return false
'''


class RunCommand(threading.Thread):
  """Helper class for executing the Mob* Monitor with a timeout."""

  def __init__(self, cmd, timeout):
    threading.Thread.__init__(self)
    self.cmd = cmd
    self.timeout = timeout
    self.p = None

    self.proc_stdout = None
    self.proc_stderr = None

  def run(self):
    self.p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
    self.proc_stdout, self.proc_stderr = self.p.communicate()

  def Stop(self):
    self.join(self.timeout)

    if self.is_alive():
      self.p.terminate()
      self.join(self.timeout)

      if self.is_alive():
        self.p.kill()
        self.join(self.timeout)

    return self.proc_stdout


class CheckFileManagerHelperTest(unittest.TestCase):
  """Unittests for CheckFileManager helper functions."""

  class CfmTestAction:
      action='test'
      info='testinfo'
      param_info={}
      def run(self, params):
          pass

  def testMapHealthcheckStatusToDict(self):
    """Test mapping a manager.HEALTHCHECK_STATUS to a dict."""


    status = manager.HEALTHCHECK_STATUS(
            'test', False, 'desc', [self.CfmTestAction()])
    expect = {'name': 'test', 'health': False, 'description': 'desc',
              'actions': ['test']}
    self.assertEqual(expect, manager.MapHealthcheckStatusToDict(status))

  def testMapServiceStatusToDict(self):
    """Test mapping a manager.SERVICE_STATUS to a dict."""

    hcstatus = manager.HEALTHCHECK_STATUS(
            'test', False, 'desc', [self.CfmTestAction()])
    hcexpect = {'name': 'test', 'health': False, 'description': 'desc',
                'actions': ['test']}
    status = manager.SERVICE_STATUS('test-service', False, [hcstatus])
    expect = {'service': 'test-service', 'health': False,
              'healthchecks': [hcexpect]}
    self.assertEqual(expect, manager.MapServiceStatusToDict(status))

  def testMapActionInfoToDict(self):
    """Test mapping a manager.ACTION_INFO to a dict."""
    actioninfo = manager.ACTION_INFO('test', 'test', {'a': 1})
    expect = {'action': 'test', 'info': 'test', 'params': {'a': 1}}
    self.assertEqual(expect, manager.MapActionInfoToDict(actioninfo))

  def testIsHealthcheckHealthy(self):
    """Test checking whether health check statuses are healthy."""
    # Test a healthy health check.
    hch = manager.HEALTHCHECK_STATUS('healthy', True, manager.NULL_DESCRIPTION,
                                     manager.EMPTY_ACTIONS)
    self.assertTrue(manager.isHealthcheckHealthy(hch))

    # Test a quasi-healthy health check.
    hcq = manager.HEALTHCHECK_STATUS('quasi-healthy', True, 'Quasi-Healthy',
                                     ['QuasiAction'])
    self.assertFalse(manager.isHealthcheckHealthy(hcq))

    # Test an unhealthy health check.
    hcu = manager.HEALTHCHECK_STATUS('unhealthy', False, 'Unhealthy',
                                     ['UnhealthyAction'])
    self.assertFalse(manager.isHealthcheckHealthy(hcu))

    # Test an object that is not a health check status.
    s = manager.SERVICE_STATUS('service_status', True, [])
    self.assertFalse(manager.isHealthcheckHealthy(s))

  def testIsServiceHealthy(self):
    """Test checking whether service statuses are healthy."""
    # Define some health check statuses.
    hch = manager.HEALTHCHECK_STATUS('healthy', True, manager.NULL_DESCRIPTION,
                                     manager.EMPTY_ACTIONS)
    hcq = manager.HEALTHCHECK_STATUS('quasi-healthy', True, 'Quasi-Healthy',
                                     ['QuasiAction'])
    hcu = manager.HEALTHCHECK_STATUS('unhealthy', False, 'Unhealthy',
                                     ['UnhealthyAction'])

    # Test a healthy service.
    s = manager.SERVICE_STATUS('healthy', True, [])
    self.assertTrue(manager.isServiceHealthy(s))

    # Test a quasi-healthy service.
    s = manager.SERVICE_STATUS('quasi-healthy', True, [hch, hcq])
    self.assertFalse(manager.isServiceHealthy(s))

    # Test an unhealthy service.
    s = manager.SERVICE_STATUS('unhealthy', False, [hcu])
    self.assertFalse(manager.isServiceHealthy(s))

    # Test an object that is not a service status.
    self.assertFalse(manager.isServiceHealthy(hch))

  def testDetermineHealthcheckStatusHealthy(self):
    """Test DetermineHealthCheckStatus on a healthy check."""
    hcname = TestHealthCheck.__name__
    testhc = TestHealthCheck()
    expected = manager.HEALTHCHECK_STATUS(hcname, True,
                                          manager.NULL_DESCRIPTION,
                                          manager.EMPTY_ACTIONS)
    self.assertEqual(expected,
                      manager.DetermineHealthcheckStatus(hcname, testhc))

  def testDeterminHealthcheckStatusUnhealthy(self):
    """Test DetermineHealthcheckStatus on an unhealthy check."""
    hcname = TestHealthCheckUnhealthy.__name__
    testhc = TestHealthCheckUnhealthy()
    desc, actions = testhc.Diagnose(testhc.Check())
    expected = manager.HEALTHCHECK_STATUS(hcname, False, desc, actions)
    result = manager.DetermineHealthcheckStatus(hcname, testhc)
    self.assertEqual(expected.actions[0].action, result.actions[0].action)
    # can't compare instances of the action objects very easily with
    # assertEquals, it tries to compare pointers
    # just compare the names
    self.assertEqual(expected.name, result.name)
    self.assertEqual(expected.health, result.health)
    self.assertEqual(expected.description, result.description)

  def testDetermineHealthcheckStatusQuasihealth(self):
    """Test DetermineHealthcheckStatus on a quasi-healthy check."""
    hcname = TestHealthCheckQuasihealthy.__name__
    testhc = TestHealthCheckQuasihealthy()
    desc, actions = testhc.Diagnose(testhc.Check())
    expected = manager.HEALTHCHECK_STATUS(hcname, True, desc, actions)
    self.assertEqual(expected,
                      manager.DetermineHealthcheckStatus(hcname, testhc))

  def testDetermineHealthcheckStatusBrokenCheck(self):
    """Test DetermineHealthcheckStatus raises on a broken health check."""
    hcname = TestHealthCheckBroken.__name__
    testhc = TestHealthCheckBroken()
    result = manager.DetermineHealthcheckStatus(hcname, testhc)

    self.assertEqual(hcname, result.name)
    self.assertFalse(result.health)
    self.assertFalse(result.actions)

  def testIsHealthCheck(self):
    """Test that IsHealthCheck properly asserts the health check interface."""

    class NoAttrs(object):
      """Test health check missing 'check' and 'diagnose' methods."""

    class NoCheckAttr(object):
      """Test health check missing 'check' method."""
      def Diagnose(self, errcode):
        pass

    class NoDiagnoseAttr(object):
      """Test health check missing 'diagnose' method."""
      def Check(self):
        pass

    class GoodHealthCheck(object):
      """Test health check that implements 'check' and 'diagnose' methods."""
      def Check(self):
        pass

      def Diagnose(self, errcode):
        pass

    self.assertFalse(manager.IsHealthCheck(NoAttrs()))
    self.assertFalse(manager.IsHealthCheck(NoCheckAttr()))
    self.assertFalse(manager.IsHealthCheck(NoDiagnoseAttr()))
    self.assertTrue(manager.IsHealthCheck(GoodHealthCheck()))

  def testApplyHealthCheckAttributesNoAttrs(self):
    """Test that we can apply attributes to a health check."""
    testhc = TestHealthCheck()
    result = manager.ApplyHealthCheckAttributes(testhc)
    self.assertEqual(result.CHECK_INTERVAL_SEC,
                      manager.CHECK_INTERVAL_DEFAULT_SEC)

  def testApplyHealthCheckAttributesHasAttrs(self):
    """Test that we do not override an acceptable attribute."""
    testhc = TestHealthCheckHasAttributes()
    check_interval = testhc.CHECK_INTERVAL_SEC
    result = manager.ApplyHealthCheckAttributes(testhc)
    self.assertEqual(result.CHECK_INTERVAL_SEC, check_interval)

  @mock.patch('manager.os')
  @mock.patch('manager.imp')
  def testImportFileAllHealthChecks(self, MockOs, MockImp):
    """Test that health checks and service name are collected."""
    manager.os.path.splitext.return_value = '/path/to/test_check.py'

    manager.os.path.getmtime.return_value = TEST_MTIME

    checkmodule = imp.new_module('test_check')
    exec(CHECKFILE_MANY_SIMPLE, checkmodule.__dict__)
    manager.imp.load_source.return_value = checkmodule


    healthchecks, mtime = manager.ImportFile(TEST_SERVICE_NAME, '/')

    self.assertEqual(len(healthchecks), 3)
    self.assertEqual(mtime, TEST_MTIME)

  @mock.patch('manager.os')
  @mock.patch('manager.imp')
  def testImportFileSomeHealthChecks(self, MockOs, MockImp):
    """Test importing when not all classes are actually health checks."""
    manager.os.path.splitext.return_value = '/path/to/test_check.py'

    manager.os.path.getmtime.return_value = TEST_MTIME

    checkmodule = imp.new_module('test_check')
    exec(CHECKFILE_MANY_SIMPLE_ONE_BAD, checkmodule.__dict__)
    manager.imp.load_source.return_value = checkmodule

    healthchecks, mtime = manager.ImportFile(TEST_SERVICE_NAME, '/')

    self.assertEqual(len(healthchecks), 2)
    self.assertEqual(mtime, TEST_MTIME)


class CheckFileManagerTest(unittest.TestCase):
  """Unittests for CheckFileManager."""

  @mock.patch('manager.os')
  @mock.patch('manager.imp')
  def testCollectionExecutionCallbackCheckfiles(self, MockOs, MockImp):
    """Test the CollectionExecutionCallback on collecting checkfiles."""
    manager.os.walk.return_value = iter([[CHECKDIR, [TEST_SERVICE_NAME], []]])
    manager.os.listdir.return_value = ['test_check.py']
    manager.os.path.isfile.return_value = True
    manager.imp.find_module.return_value = (None, None, None)

    manager.os.path.join.return_value = './%s/test_check.py' % TEST_SERVICE_NAME

    myobj = TestHealthCheck()
    manager.ImportFile = mock.Mock(return_value=[[myobj], TEST_MTIME])
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)
    cfm.CollectionExecutionCallback()

    manager.ImportFile.assert_called_once_with(
        TEST_SERVICE_NAME, './%s/test_check.py' % TEST_SERVICE_NAME)

    self.assertTrue(TEST_SERVICE_NAME in cfm.service_checks)
    self.assertEqual(cfm.service_checks[TEST_SERVICE_NAME],
                      {myobj.__class__.__name__: (TEST_MTIME, myobj)})

  @mock.patch('manager.os')
  def testCollectionExecutionCallbackNoChecks(self, MockOs):
    """Test the CollectionExecutionCallback with no valid check files."""
    manager.os.walk.return_value = iter([['/checkdir/', [], ['test.py']]])

    manager.ImportFile = mock.Mock(return_value=None)
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)
    cfm.CollectionExecutionCallback()

    self.assertFalse(manager.ImportFile.called)

    self.assertFalse(TEST_SERVICE_NAME in cfm.service_checks)

  def testStartCollectionExecution(self):
    """Test the StartCollectionExecution method."""
    plugins.Monitor = mock.Mock()

    cfm = manager.CheckFileManager(checkdir=CHECKDIR)
    cfm.StartCollectionExecution()

    self.assertTrue(plugins.Monitor.called)

  def testUpdateExistingHealthCheck(self):
    """Test update when a health check exists and is not stale."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    myobj = TestHealthCheck()

    cfm.service_checks[TEST_SERVICE_NAME] = {myobj.__class__.__name__:
                                             (TEST_MTIME, myobj)}

    myobj2 = TestHealthCheck()
    cfm.Update(TEST_SERVICE_NAME, [myobj2], TEST_MTIME)
    self.assertTrue(TEST_SERVICE_NAME in cfm.service_checks)
    self.assertEqual(cfm.service_checks[TEST_SERVICE_NAME],
                      {myobj.__class__.__name__: (TEST_MTIME, myobj)})

  def testUpdateNonExistingHealthCheck(self):
    """Test adding a new health check to the manager."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)
    cfm.service_checks = {}

    myobj = TestHealthCheck()
    cfm.Update(TEST_SERVICE_NAME, [myobj], TEST_MTIME)

    self.assertTrue(TEST_SERVICE_NAME in cfm.service_checks)
    self.assertEqual(cfm.service_checks[TEST_SERVICE_NAME],
                      {myobj.__class__.__name__: (TEST_MTIME, myobj)})

  @mock.patch('manager.time')
  def testExecuteFresh(self, MockTime):
    """Test executing a health check when the result is still fresh."""
    exec_time_offset = TestHealthCheckHasAttributes.CHECK_INTERVAL_SEC / 2
    manager.time.time.return_value = TEST_EXEC_TIME + exec_time_offset

    cfm = manager.CheckFileManager(checkdir=CHECKDIR)
    cfm.service_checks = {TEST_SERVICE_NAME:
                          {TestHealthCheckHasAttributes.__name__:
                           (TEST_MTIME, TestHealthCheckHasAttributes())}}
    cfm.service_check_results = {
        TEST_SERVICE_NAME: {TestHealthCheckHasAttributes.__name__:
                            (manager.HCEXECUTION_COMPLETED, TEST_EXEC_TIME,
                             None)}}

    cfm.Execute()

    _, exec_time, _ = cfm.service_check_results[TEST_SERVICE_NAME][
        TestHealthCheckHasAttributes.__name__]

    self.assertEqual(exec_time, TEST_EXEC_TIME)

  @mock.patch('manager.time')
  def testExecuteStale(self, MockTime):
    """Test executing a health check when the result is stale."""
    exec_time_offset = TestHealthCheckHasAttributes.CHECK_INTERVAL_SEC * 2
    manager.time.time.return_value = TEST_EXEC_TIME + exec_time_offset

    cfm = manager.CheckFileManager(checkdir=CHECKDIR)
    cfm.service_checks = {TEST_SERVICE_NAME:
                          {TestHealthCheckHasAttributes.__name__:
                           (TEST_MTIME, TestHealthCheckHasAttributes())}}
    cfm.service_check_results = {
        TEST_SERVICE_NAME: {TestHealthCheckHasAttributes.__name__:
                            (manager.HCEXECUTION_COMPLETED, TEST_EXEC_TIME,
                             None)}}

    cfm.Execute()

    _, exec_time, _ = cfm.service_check_results[TEST_SERVICE_NAME][
        TestHealthCheckHasAttributes.__name__]

    self.assertEqual(exec_time, TEST_EXEC_TIME + exec_time_offset)

  @mock.patch('manager.time')
  def testExecuteNonExistent(self, MockTime):
    """Test executing a health check when the result is nonexistent."""
    manager.time.time.return_value = TEST_EXEC_TIME

    cfm = manager.CheckFileManager(checkdir=CHECKDIR)
    cfm.service_checks = {TEST_SERVICE_NAME:
                          {TestHealthCheck.__name__:
                           (TEST_MTIME, TestHealthCheck())}}

    cfm.Execute()

    resultsdict = cfm.service_check_results.get(TEST_SERVICE_NAME)
    self.assertTrue(resultsdict is not None)

    exec_status, exec_time, _ = resultsdict.get(TestHealthCheck.__name__,
                                                (None, None, None))
    self.assertTrue(exec_status is not None)
    self.assertTrue(exec_time is not None)

    self.assertEqual(exec_status, manager.HCEXECUTION_COMPLETED)
    self.assertEqual(exec_time, TEST_EXEC_TIME)

  @mock.patch('manager.time')
  def testExecuteForce(self, MockTime):
    """Test executing a health check by ignoring the check interval."""
    exec_time_offset = TestHealthCheckHasAttributes.CHECK_INTERVAL_SEC / 2
    manager.time.time.return_value = TEST_EXEC_TIME + exec_time_offset

    cfm = manager.CheckFileManager(checkdir=CHECKDIR)
    cfm.service_checks = {TEST_SERVICE_NAME:
                          {TestHealthCheckHasAttributes.__name__:
                           (TEST_MTIME, TestHealthCheckHasAttributes())}}
    cfm.service_check_results = {
        TEST_SERVICE_NAME: {TestHealthCheckHasAttributes.__name__:
                            (manager.HCEXECUTION_COMPLETED, TEST_EXEC_TIME,
                             None)}}

    cfm.Execute(force=True)

    _, exec_time, _ = cfm.service_check_results[TEST_SERVICE_NAME][
        TestHealthCheckHasAttributes.__name__]

    self.assertEqual(exec_time, TEST_EXEC_TIME + exec_time_offset)

  def testConsolidateServiceStatesUnhealthy(self):
    """Test consolidating state for a service with unhealthy checks."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    # Setup some test check results
    hcname = TestHealthCheck.__name__
    statuses = [
        manager.HEALTHCHECK_STATUS(hcname, False, 'Failed', ['Repair']),
        manager.HEALTHCHECK_STATUS(hcname, True, 'Quasi', ['RepairQuasi']),
        manager.HEALTHCHECK_STATUS(hcname, True, '', [])]

    cfm.service_check_results.setdefault(TEST_SERVICE_NAME, {})
    for i, status in enumerate(statuses):
      name = '%s_%s' % (hcname, i)
      cfm.service_check_results[TEST_SERVICE_NAME][name] = (
          manager.HCEXECUTION_COMPLETED, TEST_EXEC_TIME,
          status)

    # Run and check the results.
    cfm.ConsolidateServiceStates()
    self.assertTrue(TEST_SERVICE_NAME in cfm.service_states)

    _, health, healthchecks = cfm.service_states[TEST_SERVICE_NAME]
    self.assertFalse(health)
    self.assertEqual(2, len(healthchecks))
    self.assertTrue(all([x in healthchecks for x in statuses[:2]]))

  def testConsolidateServiceStatesQuasiHealthy(self):
    """Test consolidating state for a service with quasi-healthy checks."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    # Setup some test check results
    hcname = TestHealthCheck.__name__
    statuses = [
        manager.HEALTHCHECK_STATUS(hcname, True, 'Quasi', ['RepairQuasi']),
        manager.HEALTHCHECK_STATUS(hcname, True, '', [])]

    cfm.service_check_results.setdefault(TEST_SERVICE_NAME, {})
    for i, status in enumerate(statuses):
      name = '%s_%s' % (hcname, i)
      cfm.service_check_results[TEST_SERVICE_NAME][name] = (
          manager.HCEXECUTION_COMPLETED, TEST_EXEC_TIME,
          status)

    # Run and check the results.
    cfm.ConsolidateServiceStates()
    self.assertTrue(TEST_SERVICE_NAME in cfm.service_states)

    _, health, healthchecks = cfm.service_states[TEST_SERVICE_NAME]
    self.assertTrue(health)
    self.assertEqual(1, len(healthchecks))
    self.assertTrue(statuses[0] in healthchecks)

  def testConsolidateServiceStatesHealthy(self):
    """Test consolidating state for a healthy service."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    # Setup some test check results
    hcname = TestHealthCheck.__name__
    hcname2 = '%s_2' % hcname
    statuses = [
        manager.HEALTHCHECK_STATUS(hcname, True, '', []),
        manager.HEALTHCHECK_STATUS(hcname2, True, '', [])]

    cfm.service_check_results.setdefault(TEST_SERVICE_NAME, {})
    cfm.service_check_results[TEST_SERVICE_NAME][hcname] = (
        manager.HCEXECUTION_COMPLETED, TEST_EXEC_TIME, statuses[0])
    cfm.service_check_results[TEST_SERVICE_NAME][hcname2] = (
        manager.HCEXECUTION_IN_PROGRESS, TEST_EXEC_TIME, statuses[1])

    # Run and check.
    cfm.ConsolidateServiceStates()

    self.assertTrue(TEST_SERVICE_NAME in cfm.service_states)

    _, health, healthchecks = cfm.service_states.get(TEST_SERVICE_NAME)
    self.assertTrue(health)
    self.assertEqual(0, len(healthchecks))

  def testGetServiceList(self):
    """Test the GetServiceList RPC response."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    self.assertEqual([], cfm.GetServiceList())

    status = manager.SERVICE_STATUS(TEST_SERVICE_NAME, True, [])
    cfm.service_states[TEST_SERVICE_NAME] = status

    self.assertEqual([TEST_SERVICE_NAME], cfm.GetServiceList())

  def testGetStatusNonExistent(self):
    """Test the GetStatus RPC response when the service does not exist."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    self.assertFalse(TEST_SERVICE_NAME in cfm.service_states)

    status = manager.SERVICE_STATUS(TEST_SERVICE_NAME, False, [])
    self.assertEqual(status, cfm.GetStatus(TEST_SERVICE_NAME))

  def testGetStatusSingleService(self):
    """Test the GetStatus RPC response for a single service."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    s1name = TEST_SERVICE_NAME
    s2name = '%s_2' % s1name
    status1 = manager.SERVICE_STATUS(s1name, True, [])
    status2 = manager.SERVICE_STATUS(s2name, True, [])
    cfm.service_states[s1name] = status1
    cfm.service_states[s2name] = status2

    self.assertEqual(status1, cfm.GetStatus(s1name))
    self.assertEqual(status2, cfm.GetStatus(s2name))

  def testGetStatusAllServices(self):
    """Test the GetStatus RPC response when no service is specified."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    s1name = TEST_SERVICE_NAME
    s2name = '%s_2' % s1name
    status1 = manager.SERVICE_STATUS(s1name, True, [])
    status2 = manager.SERVICE_STATUS(s2name, True, [])
    cfm.service_states[s1name] = status1
    cfm.service_states[s2name] = status2

    result = cfm.GetStatus('')
    self.assertEqual(2, len(result))
    self.assertTrue(all([x in result for x in [status1, status2]]))

  def testRepairServiceHealthy(self):
    """Test the RepairService RPC when the service is healthy."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    healthy_status = manager.SERVICE_STATUS(TEST_SERVICE_NAME, True, [])
    cfm.service_states[TEST_SERVICE_NAME] = healthy_status

    self.assertEqual(healthy_status, cfm.RepairService(TEST_SERVICE_NAME,
                                                        'HealthcheckName',
                                                        'RepairFuncName',
                                                        {}))

  def testRepairServiceNonExistent(self):
    """Test the RepairService RPC when the service does not exist."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    self.assertFalse(TEST_SERVICE_NAME in cfm.service_states)

    expected = manager.SERVICE_STATUS(TEST_SERVICE_NAME, False, [])
    result = cfm.RepairService(TEST_SERVICE_NAME, 'DummyHealthcheck',
                               'DummyAction', {})
    self.assertEqual(expected, result)

  def testRepairServiceInvalidAction(self):
    """Test the RepairService RPC when the action is not recognized."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    hcobj = TestHealthCheckUnhealthy()
    cfm.service_checks[TEST_SERVICE_NAME] = {
        hcobj.__class__.__name__: (TEST_MTIME, hcobj)}

    unhealthy_status = manager.SERVICE_STATUS(
        TEST_SERVICE_NAME, False,
        [manager.HEALTHCHECK_STATUS(hcobj.__class__.__name__,
                                    False, 'Always fails', [hcobj.Repair])])
    cfm.service_states[TEST_SERVICE_NAME] = unhealthy_status

    status = cfm.GetStatus(TEST_SERVICE_NAME)
    self.assertFalse(status.health)
    self.assertEqual(1, len(status.healthchecks))

    status = cfm.RepairService(TEST_SERVICE_NAME, hcobj.__class__.__name__,
                               'Blah', {})
    self.assertFalse(status.health)
    self.assertEqual(1, len(status.healthchecks))

  def testRepairServiceInvalidActionArguments(self):
    """Test the RepairService RPC when the action arguments are invalid."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    hcobj = TestHealthCheckUnhealthy()
    cfm.service_checks[TEST_SERVICE_NAME] = {
        hcobj.__class__.__name__: (TEST_MTIME, hcobj)}

    unhealthy_status = manager.SERVICE_STATUS(
        TEST_SERVICE_NAME, False,
        [manager.HEALTHCHECK_STATUS(hcobj.__class__.__name__,
                                    False, 'Always fails', [hcobj.Repair])])
    cfm.service_states[TEST_SERVICE_NAME] = unhealthy_status

    status = cfm.GetStatus(TEST_SERVICE_NAME)
    self.assertFalse(status.health)
    self.assertEqual(1, len(status.healthchecks))

    status = cfm.RepairService(TEST_SERVICE_NAME, hcobj.__class__.__name__,
                               'Repair', {})
    self.assertFalse(status.health)
    self.assertEqual(1, len(status.healthchecks))

  def testRepairService(self):
    """Test the RepairService RPC to repair an unhealthy service."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    hcobj = TestHealthCheckUnhealthy()
    cfm.service_checks[TEST_SERVICE_NAME] = {
        hcobj.__class__.__name__: (TEST_MTIME, hcobj)}

    unhealthy_status = manager.SERVICE_STATUS(
        TEST_SERVICE_NAME, False,
        [manager.HEALTHCHECK_STATUS(hcobj.__class__.__name__,
                                    False, 'Always fails',
                                    [RepairUnhealthyCheck(hcobj)])])
    cfm.service_states[TEST_SERVICE_NAME] = unhealthy_status

    status = cfm.GetStatus(TEST_SERVICE_NAME)
    self.assertFalse(status.health)
    self.assertEqual(1, len(status.healthchecks))

    status = cfm.RepairService(TEST_SERVICE_NAME,
                               hcobj.__class__.__name__,
                               'Repair',
                               {})
    self.assertTrue(status.health)
    self.assertEqual(0, len(status.healthchecks))

  def testActionInfoServiceNonExistent(self):
    """Test the ActionInfo RPC when the service does not exist."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    self.assertFalse(TEST_SERVICE_NAME in cfm.service_states)

    expect = manager.ACTION_INFO('test', 'Service not recognized.', {})
    result = cfm.ActionInfo(TEST_SERVICE_NAME, 'test', 'test')
    self.assertEqual(expect, result)

  def testActionInfoServiceHealthy(self):
    """Test the ActionInfo RPC when the service is healthy."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    healthy_status = manager.SERVICE_STATUS(TEST_SERVICE_NAME, True, [])
    cfm.service_states[TEST_SERVICE_NAME] = healthy_status

    expect = manager.ACTION_INFO('test', 'Service is healthy.', {})
    result = cfm.ActionInfo(TEST_SERVICE_NAME, 'test', 'test')
    self.assertEqual(expect, result)

  def testActionInfoActionNonExistent(self):
    """Test the ActionInfo RPC when the action does not exist."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    hcobj = TestHealthCheckUnhealthy()
    cfm.service_checks[TEST_SERVICE_NAME] = {
        hcobj.__class__.__name__: (TEST_MTIME, hcobj)}

    unhealthy_status = manager.SERVICE_STATUS(
        TEST_SERVICE_NAME, False,
        [manager.HEALTHCHECK_STATUS(hcobj.__class__.__name__,
                                    False, 'Always fails', [hcobj.Repair])])
    cfm.service_states[TEST_SERVICE_NAME] = unhealthy_status

    expect = manager.ACTION_INFO('test', 'Action not recognized.', {})
    result = cfm.ActionInfo(TEST_SERVICE_NAME, hcobj.__class__.__name__,
                            'test')
    self.assertEqual(expect, result)

  def testActionInfo(self):
    """Test the ActionInfo RPC to collect information on a repair action."""
    cfm = manager.CheckFileManager(checkdir=CHECKDIR)

    hcobj = TestHealthCheckMultipleActions()
    hcname = hcobj.__class__.__name__
    actions = [hcobj.NoParams, hcobj.Params]

    cfm.service_checks[TEST_SERVICE_NAME] = {hcname: (TEST_MTIME, hcobj)}

    unhealthy_status = manager.SERVICE_STATUS(
        TEST_SERVICE_NAME, False,
        [manager.HEALTHCHECK_STATUS(hcname, False, 'Always fails', actions)])
    cfm.service_states[TEST_SERVICE_NAME] = unhealthy_status

    # Test ActionInfo when the action has no parameters.
    expect = manager.ACTION_INFO('NoParams', 'NoParams Action.', {})
    self.assertEqual(expect,
                      cfm.ActionInfo(TEST_SERVICE_NAME, hcname, 'NoParams'))

    # Test ActionInfo when the action has positional and default parameters.
    expect = manager.ACTION_INFO('Params', 'Params Action.',
                                 {'x': 'y'})
    self.assertEqual(expect, cfm.ActionInfo(TEST_SERVICE_NAME,
                                             hcname, 'Params'))

if __name__ == '__main__':
    unittest.main()
