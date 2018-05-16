# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import sys

sys.path.append('..')
from abstract_diagnostic_check import AbstractDiagnosticCheck
from diagnostic_error import DiagnosticError
from util import osutils
from util import config

class BaseContainerClone(AbstractDiagnosticCheck):
    """
    Attempt to clone and start a new container from the base
    container
    """

    CONTAINER_PATH = '/mnt/moblab/containers'

    category = 'lxc'

    name = 'Base Container Clone'

    description = ('Test that the base lxc container is valid and '
        'able to be cloned')

    def _run_command(self, cmd):
        print_cmd = ' '.join(cmd)
        self.output += print_cmd + '\n'
        cmd_out = osutils.sudo_run_command(cmd)
        self.output += cmd_out
        self.output += 'OK\n\n'


    def run(self):
        self.output = ''
        container_base_name = config.Config().get('container_base_name')
        try:
            clone_cmd = ['lxc-copy',
                '-P', self.CONTAINER_PATH, # note uppercase P and lowercase p
                '-p', self.CONTAINER_PATH,
                '-n', container_base_name,
                '-N', 'base_check']

            start_cmd = ['lxc-start',
                '-P', self.CONTAINER_PATH,
                '-n', 'base_check',
                '-d']

            stop_cmd = ['lxc-stop',
                '-P', self.CONTAINER_PATH,
                '-n', 'base_check']

            self._run_command(clone_cmd)
            self._run_command(start_cmd)
            self._run_command(stop_cmd)

        except osutils.RunCommandError as e:
            self.output += str(e) + '\n\n'
        finally:
            try:
                destroy_cmd = ['lxc-destroy',
                '-P', self.CONTAINER_PATH,
                '-n', 'base_check',
                '--force']
                self._run_command(destroy_cmd)
            except osutils.RunCommandError as e:
                self.output += str(e) + '\n\n'

        return self.output
