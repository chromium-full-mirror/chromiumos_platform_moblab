# Copyright 2009 Google Inc. Released under the GPL v2

"""This is a convenience module to import all available types of hosts.

Implementation details:
You should 'import hosts' instead of importing every available host module.
"""

from client.common_lib import utils
try:
    from client.common_lib.hosts.base_classes import Host
    from client.common_lib.hosts.repair import *
except ImportError:
    from base_classes import Host
    from repair import *
