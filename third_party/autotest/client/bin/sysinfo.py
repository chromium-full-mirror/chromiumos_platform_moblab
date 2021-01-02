from client.common_lib import utils
from client.bin import base_sysinfo
from client.bin import site_sysinfo

sysinfo = utils.import_site_class(__file__,
                                  "client.bin.site_sysinfo",
                                  "site_sysinfo", base_sysinfo.base_sysinfo)

# pull in some data stucture stubs from base_sysinfo, for convenience
logfile = base_sysinfo.logfile
command = base_sysinfo.command
# and some from site_sysinfo
logdir = site_sysinfo.logdir
