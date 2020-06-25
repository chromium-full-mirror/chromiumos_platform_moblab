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
            'host_services': ['*host-ser*'] # Only need the pb2 files
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
    packages=['moblab_common', 'host_services'],
    package_dir={'': 'src'},
    cmdclass={
        'build_package_protos': build_package_protos,
        'build_py': custom_build_py,
    },
    setup_requires=[
        'grpcio-tools',
    ],
    install_requires=[
        'backports.ssl-match-hostname==3.7.0.1',
        'bcrypt==3.1.7',
        'cachetools==3.1.1',
        'certifi==2020.6.20',
        'cffi==1.14.0',
        'chardet==3.0.4',
        'cryptography==2.9.2',
        'docker==4.2.1',
        'enum34==1.1.10',
        'future==0.18.2',
        'futures==3.3.0;python_version<"3.0"',
        'gevent==20.6.2',
        'google-api-core[grpc]==1.21.0',
        'google-auth==1.18.0',
        'google-cloud-core==1.3.0',
        'google-cloud-pubsub==1.6.0',
        'google-cloud-storage==1.29.0',
        'google-resumable-media==0.5.1',
        'googleapis-common-protos[grpc]==1.52.0',
        'greenlet==0.4.16',
        'grpc-google-iam-v1==0.12.3',
        'grpcio==1.29.0',
        'idna==2.9',
        'ipaddress==1.0.23',
        'parallel-ssh==1.9.1',
        'paramiko==2.7.1',
        'protobuf==3.12.2',
        'pyasn1-modules==0.2.8',
        'pyasn1==0.4.8',
        'pycparser==2.20',
        'pynacl==1.4.0',
        'python-nmap==0.6.1',
        'pytz==2020.1',
        'requests==2.24.0',
        'rsa==4.0',
        'six==1.15.0',
        'ssh2-python==0.18.0.post1',
        'urllib3==1.25.9',
        'websocket-client==0.57.0',
        'zope.event==4.4',
        'zope.interface==5.1.0',
    ],
    scripts=[
        'src/tools/create-moblab-id.py',
    ])
