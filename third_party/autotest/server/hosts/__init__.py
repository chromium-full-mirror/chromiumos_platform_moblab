#
# Copyright 2007 Google Inc. Released under the GPL v2

"""This is a convenience module to import all available types of hosts.

Implementation details:
You should 'import hosts' instead of importing every available host module.
"""


# host abstract classes
from server.hosts.base_classes import Host
from server.hosts.remote import RemoteHost

# host implementation classes
from server.hosts.ssh_host import SSHHost
from server.hosts.cros_host import CrosHost
from server.hosts.servo_host import ServoHost
# factory function
from server.hosts.factory import create_host
from server.hosts.factory import create_target_machine
