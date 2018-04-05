# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unittests for the diagnostic check manager."""

import unittest
import mock

import manager
import abstract_diagnostic_check
import diagnostic_error

class MockDiagnosticCheck(abstract_diagnostic_check.AbstractDiagnosticCheck):
    category = 'test'
    name = 'test'
    description = 'just a test'

    def run(self):
        return 'some results'

class TestDiagnosticCheckManager(unittest.TestCase):

    def setUp(self):
        self.manager = manager.DiagnosticCheckManager()
        self.manager.CHECKS = [MockDiagnosticCheck]
        self.manager.init_checks()

    def testInitChecks(self):
        self.assertTrue('test' in self.manager.diagnostic_checks)
        self.assertTrue('test' in self.manager.diagnostic_checks['test'])
        self.assertEqual('just a test',
                self.manager.diagnostic_checks['test']['test'].description)

    def testListDiagnosticChecks(self):
        expect = [{
            'category': 'test',
            'checks': [{
                'name': 'test',
                'description': 'just a test'
            }]
        }]

        output = self.manager.list_diagnostic_checks()
        self.assertEqual(expect, output)

    def testRunDiagnosticCheck(self):
        expect = 'some results'

        output = self.manager.run_diagnostic_check('test', 'test')
        self.assertEqual(expect, output)

    def testMissingRunDiagnosticCheck(self):
        with self.assertRaises(diagnostic_error.DiagnosticError):
            self.manager.run_diagnostic_check('doesnt', 'exist')


if __name__ == '__main__':
    unittest.main()
