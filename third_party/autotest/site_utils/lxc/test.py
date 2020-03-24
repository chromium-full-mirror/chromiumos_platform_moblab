
import common

from autotest_lib.site_utils import lxc


if __name__=='__main__':
    bucket = lxc.ContainerBucket()
    bucket.setup_test("test_95_1580745818_13349", 95, "http://192.168.100.50:8080/static/eve-release/R83-12993.0.0/autotest_server_package.tar.bz2", "/usr/local/autotest/results/95-moblab/192.168.231.116", "/usr/local/autotest/results/95-moblab/192.168.231.116/lucifer/control_attach", False, "lxc_job_folder", "192.168.231.116")


