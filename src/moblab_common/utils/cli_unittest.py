# -*- coding: utf-8 -*-
# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
import mock

import cli

class TestRunCommand(unittest.TestCase):
    def test_run_command(self):
        output = cli.run_command(['echo', 'hello'])
        self.assertEqual(output, 'hello\n')

    def test_run_command_error(self):
        with self.assertRaises(cli.RunCommandError):
            cli.run_command(['false'])

    def test_run_command_error_code_ok(self):
        output = cli.run_command(['false'], error_code_ok=True)

    @mock.patch('cli.LOGGER')
    def test_run_command_log(self, MockLogger):
        cli.run_command(['echo', 'hello'], log=True)
        MockLogger.info.assert_any_call('echo hello')
        MockLogger.info.assert_any_call('hello\n')

class TestSudoRunCommand(unittest.TestCase):
    @mock.patch('cli.LOGGER')
    @mock.patch('cli.subprocess')
    def test_sudo_as_root(self, MockLogger, MockSubprocess):
        cli.subprocess.check_output.return_value = 'test'
        output = cli.sudo_run_command(['echo', 'hello'])

        self.assertEqual(output, 'test')
        cli.subprocess.check_output.assert_called_with(
            ['sudo', 'echo', 'hello'], shell=False)
        cli.LOGGER.info.assert_any_call('sudo echo hello')

    @mock.patch('cli.LOGGER')
    @mock.patch('cli.subprocess')
    def test_sudo_as_other_user(self, MockLogger, MockSubprocess):
        cli.subprocess.check_output.return_value = 'test'
        output = cli.sudo_run_command(['echo', 'hello'], user='moblab')

        self.assertEqual(output, 'test')
        cli.subprocess.check_output.assert_called_with(
            ['sudo', '-u', 'moblab', 'echo', 'hello'], shell=False)
        cli.LOGGER.info.assert_any_call('sudo -u moblab echo hello')

class TestCreateTarball(unittest.TestCase):
    @mock.patch('cli.run_command')
    def test_create_tarball(self, MockRunCommand):
        cli.create_tarball('mytarball.tgz', '/my/dir')
        cli.run_command.assert_called_with(
            ['tar', '-czf', 'mytarball.tgz', '/my/dir'])

class TestSafeMkdir(unittest.TestCase):
    @mock.patch('cli.run_command')
    def test_safe_mkdir(self, MockRunCommand):
        cli.safe_mkdir('/path/to/my/dir')
        cli.run_command.assert_called_with(
            ['mkdir', '-p', '/path/to/my/dir'])

class TestRmDir(unittest.TestCase):
    @mock.patch('cli.shutil')
    @mock.patch('cli.run_command')
    def test_rm_dir(self, MockShutil, MockRunCommand):
        cli.rm_dir('rm/this/old/dir')

    @mock.patch('cli.shutil')
    @mock.patch('cli.run_command')
    def test_rm_dir_error(self, MockShutil, MockRunCommand):
        cli.shutil.rmtree.side_effect = EnvironmentError()
        with self.assertRaises(EnvironmentError):
            cli.rm_dir('rm/this/old/dir')

    @mock.patch('cli.shutil')
    @mock.patch('cli.run_command')
    def test_ignore_missing(self, MockShutil, MockRunCommand):
        def side_effect(arg):
            error = EnvironmentError()
            error.errno = cli.errno.ENOENT
        cli.shutil.rmtree.side_effect = side_effect
        cli.rm_dir('rm/this/old/dir', ignore_missing=True)

    @mock.patch('cli.shutil')
    @mock.patch('cli.run_command')
    def test_rm_dir_root(self, MockShutil, MockRunCommand):
        cli.rm_dir('rm/this/old/dir', sudo=True)
        cli.run_command.assert_called_with(
            ['sudo', 'rm', '-r', '--', 'rm/this/old/dir'],
            log=True, error_code_ok=False, shell=False)

    @mock.patch('cli.shutil')
    @mock.patch('cli.run_command')
    @mock.patch('cli.os')
    def test_rm_dir_root_ignore_missing(
            self, MockShutil, MockRunCommand, MockOs):
        cli.rm_dir('rm/this/old/dir', sudo=True, ignore_missing=True)
        cli.run_command.side_effect = cli.RunCommandError('', 1)
        cli.os.path.exists.return_value = False
        cli.run_command.assert_called_with(
            ['sudo', 'rm', '-rf', '--', 'rm/this/old/dir'],
            log=True, error_code_ok=False, shell=False)

    @mock.patch('cli.shutil')
    @mock.patch('cli.run_command')
    @mock.patch('cli.os')
    def test_rm_dir_root_error(
            self, MockShutil, MockRunCommand, MockOs):
        cli.run_command.side_effect = cli.RunCommandError('', 1)
        with self.assertRaises(cli.RunCommandError):
            cli.rm_dir('rm/this/old/dir', sudo=True)

class TestResolveSymlink(unittest.TestCase):
    @mock.patch('cli.os')
    def test_resolve_symlink(self, MockOs):
        cli.os.path.islink.side_effect = [True, False]
        cli.os.readlink.return_value = '/my/file'
        cli.os.path.join.return_value = '/path/to/my/file'
        file_name = cli.resolve_symlink('file')
        self.assertEqual(file_name, '/path/to/my/file')

    @mock.patch('cli.os')
    def test_symlink_error(self, MockOs):
        cli.os.path.islink.return_value = True
        cli.os.readlink.return_value = '/my/file'
        cli.os.path.join.return_value = '/path/to/my/file'
        with self.assertRaises(ValueError):
            cli.resolve_symlink('file')


if __name__ == '__main__':
    unittest.main()
