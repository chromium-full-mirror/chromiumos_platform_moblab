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
        'cachetools==3.1.1',         # via google-auth
        'certifi==2020.6.20',        # via requests
        'chardet==3.0.4',            # via requests
        'enum34==1.1.10',            # via google-cloud-pubsub, grpcio
        'future==0.18.2',            # via -r requirements.txt
        'futures==3.3.0;python_version<"3.0"',            # via google-api-core, grpcio
        'google-api-core[grpc]==1.16.0',  # via google-cloud-core, google-cloud-pubsub
        'google-auth==1.14.1',       # via -r requirements.txt, google-api-core, google-cloud-storage
        'google-cloud-core==1.3.0',  # via google-cloud-storage
        'google-cloud-pubsub==1.5.0',  # via -r requirements.txt
        'google-cloud-storage==1.28.1',  # via -r requirements.txt
        'google-resumable-media==0.5.1',  # via google-cloud-storage
        'googleapis-common-protos[grpc]==1.52.0',  # via google-api-core, grpc-google-iam-v1
        'grpc-google-iam-v1==0.12.3',  # via google-cloud-pubsub
        'grpcio==1.30.0',            # via google-api-core, googleapis-common-protos, grpc-google-iam-v1
        'idna==2.9',                 # via requests
        'protobuf==3.12.2',          # via google-api-core, googleapis-common-protos
        'pyasn1-modules==0.2.8',     # via google-auth
        'pyasn1==0.4.8',             # via pyasn1-modules, rsa
        'pytz==2020.1',              # via google-api-core
        'requests==2.24.0',          # via -r requirements.txt, google-api-core
        'rsa==4.0',                  # via google-auth
        'six==1.15.0',               # via google-api-core, google-auth, google-resumable-media, grpcio, protobuf
        'urllib3==1.25.9',           # via requests
    ],
    scripts=[
        'src/tools/create-moblab-id.py',
    ])
