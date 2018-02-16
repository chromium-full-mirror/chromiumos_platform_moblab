# -*- coding: utf-8 -*-
# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
import mock

import osutils

class TestRunCommand(unittest.TestCase):
    def test_run_command(self):
        output = osutils.run_command(['echo', 'hello'])
        self.assertEqual(output, 'hello\n')

    def test_run_command_error(self):
        with self.assertRaises(osutils.RunCommandError):
            osutils.run_command(['false'])

    def test_run_command_error_code_ok(self):
        output = osutils.run_command(['false'], error_code_ok=True)

    @mock.patch('osutils.LOGGER')
    def test_run_command_log(self, MockLogger):
        osutils.run_command(['echo', 'hello'], log=True)
        MockLogger.info.assert_any_call('echo hello')
        MockLogger.info.assert_any_call('hello\n')

class TestSudoRunCommand(unittest.TestCase):
    @mock.patch('osutils.LOGGER')
    @mock.patch('osutils.subprocess')
    def test_sudo_as_root(self, MockLogger, MockSubprocess):
        osutils.subprocess.check_output.return_value = 'test'
        output = osutils.sudo_run_command(['echo', 'hello'])

        self.assertEqual(output, 'test')
        osutils.subprocess.check_output.assert_called_with(
            ['sudo', 'echo', 'hello'])
        osutils.LOGGER.info.assert_any_call('sudo echo hello')

    @mock.patch('osutils.LOGGER')
    @mock.patch('osutils.subprocess')
    def test_sudo_as_other_user(self, MockLogger, MockSubprocess):
        osutils.subprocess.check_output.return_value = 'test'
        output = osutils.sudo_run_command(['echo', 'hello'], user='moblab')

        self.assertEqual(output, 'test')
        osutils.subprocess.check_output.assert_called_with(
            ['sudo', '-u', 'moblab', 'echo', 'hello'])
        osutils.LOGGER.info.assert_any_call('sudo -u moblab echo hello')

class TestCreateTarball(unittest.TestCase):
    @mock.patch('osutils.run_command')
    def test_create_tarball(self, MockRunCommand):
        osutils.create_tarball('mytarball.tgz', '/my/dir')
        osutils.run_command.assert_called_with(
            ['tar', '-czf', 'mytarball.tgz', '/my/dir'])

class TestSafeMkdir(unittest.TestCase):
    @mock.patch('osutils.run_command')
    def test_safe_mkdir(self, MockRunCommand):
        osutils.safe_mkdir('/path/to/my/dir')
        osutils.run_command.assert_called_with(
            ['mkdir', '-p', '/path/to/my/dir'])

class TestRmDir(unittest.TestCase):
    @mock.patch('osutils.shutil')
    @mock.patch('osutils.run_command')
    def test_rm_dir(self, MockShutil, MockRunCommand):
        osutils.rm_dir('rm/this/old/dir')

    @mock.patch('osutils.shutil')
    @mock.patch('osutils.run_command')
    def test_rm_dir_error(self, MockShutil, MockRunCommand):
        osutils.shutil.rmtree.side_effect = EnvironmentError()
        with self.assertRaises(EnvironmentError):
            osutils.rm_dir('rm/this/old/dir')

    @mock.patch('osutils.shutil')
    @mock.patch('osutils.run_command')
    def test_ignore_missing(self, MockShutil, MockRunCommand):
        def side_effect(arg):
            error = EnvironmentError()
            error.errno = osutils.errno.ENOENT
        osutils.shutil.rmtree.side_effect = side_effect
        osutils.rm_dir('rm/this/old/dir', ignore_missing=True)

    @mock.patch('osutils.shutil')
    @mock.patch('osutils.run_command')
    def test_rm_dir_root(self, MockShutil, MockRunCommand):
        osutils.rm_dir('rm/this/old/dir', sudo=True)
        osutils.run_command.assert_called_with(
            ['sudo', 'rm', '-r', '--', 'rm/this/old/dir'],
            log=True, error_code_ok=False)

    @mock.patch('osutils.shutil')
    @mock.patch('osutils.run_command')
    @mock.patch('osutils.os')
    def test_rm_dir_root_ignore_missing(
            self, MockShutil, MockRunCommand, MockOs):
        osutils.rm_dir('rm/this/old/dir', sudo=True, ignore_missing=True)
        osutils.run_command.side_effect = osutils.RunCommandError('', 1)
        osutils.os.path.exists.return_value = False
        osutils.run_command.assert_called_with(
            ['sudo', 'rm', '-rf', '--', 'rm/this/old/dir'],
            log=True, error_code_ok=False)

    @mock.patch('osutils.shutil')
    @mock.patch('osutils.run_command')
    @mock.patch('osutils.os')
    def test_rm_dir_root_error(
            self, MockShutil, MockRunCommand, MockOs):
        osutils.run_command.side_effect = osutils.RunCommandError('', 1)
        with self.assertRaises(osutils.RunCommandError):
            osutils.rm_dir('rm/this/old/dir', sudo=True)

class TestResolveSymlink(unittest.TestCase):
    @mock.patch('osutils.os')
    def test_resolve_symlink(self, MockOs):
        osutils.os.path.islink.side_effect = [True, False]
        osutils.os.readlink.return_value = '/my/file'
        osutils.os.path.join.return_value = '/path/to/my/file'
        file_name = osutils.resolve_symlink('file')
        self.assertEqual(file_name, '/path/to/my/file')

    @mock.patch('osutils.os')
    def test_symlink_error(self, MockOs):
        osutils.os.path.islink.return_value = True
        osutils.os.readlink.return_value = '/my/file'
        osutils.os.path.join.return_value = '/path/to/my/file'
        with self.assertRaises(ValueError):
            osutils.resolve_symlink('file')

class TestListBlockDevices(unittest.TestCase):
    LSBLK_OUT = ('NAME="sda" RM="0" TYPE="disk" SIZE="128035676160"\n'
        'NAME="sda1" RM="0" TYPE="part" SIZE="123578875904"\n'
        'NAME="sda2" RM="0" TYPE="part" SIZE="16777216"')

    @mock.patch('osutils.run_command')
    def test_list_block_devices(self, MockRunCommand):
        osutils.run_command.return_value = self.LSBLK_OUT
        devices = osutils.list_block_devices()

        osutils.run_command.assert_called_with([
            'lsblk', '--pairs', '--bytes', '--output',
            'NAME,RM,TYPE,SIZE'])

        self.assertEqual(devices[0].NAME, 'sda')
        self.assertEqual(devices[0].RM, '0')
        self.assertEqual(devices[0].TYPE, 'disk')
        self.assertEqual(devices[0].SIZE, '128035676160')

        self.assertEqual(devices[1].NAME, 'sda1')
        self.assertEqual(devices[2].NAME, 'sda2')

        self.assertEqual(len(devices), 3)

if __name__ == '__main__':
    unittest.main()
