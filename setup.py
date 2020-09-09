# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from distutils.command.build_py import build_py as _build_py
import fnmatch
import distutils.command.install
import setuptools

class build_package_protos(setuptools.Command):
    """Command to generate project *_pb2.py modules from proto files."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from grpc.tools import command
        command.build_package_protos(self.distribution.package_dir[''])


excluded = {'moblab_common': ['*unittest*'],
            'host_services': ['*host-ser*'], # Only need the pb2 files
            'moblab_rpcserver': ['*moblab-rpc*'] # Only need the pb2 files
           }


class custom_build_py(_build_py, object):

    def run(self):
       self.run_command('build_package_protos')
       super(custom_build_py, self).run()

    def find_package_modules(self, package, package_dir):
    # Override the find modules function to apply custom filters.
        modules = super(custom_build_py, self).find_package_modules(package, package_dir)
        filtered_modules = []
        for (pkg, mod, fn) in modules:
            exclude = False
            for pattern in excluded.get(pkg, []):
                if fnmatch.fnmatchcase(fn, pat=pattern):
                    exclude = True
            if not exclude:
                filtered_modules.append((pkg, mod, fn))
        return filtered_modules


setuptools.setup(
    name='moblab',
    version='0.1',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    cmdclass={
        'build_package_protos': build_package_protos,
        'build_py': custom_build_py,
    },
    setup_requires=[
        'grpcio-tools==1.29.0',
    ],
    install_requires=[
        'future',
        'requests',
        'google-cloud-storage',
        'google-cloud-pubsub',
        'docker',
        'parallel-ssh',
        'python-nmap',
    ],
    scripts=[
        'src/tools/create-moblab-id.py',
    ])
