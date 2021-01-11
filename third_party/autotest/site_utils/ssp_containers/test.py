
import common

from site_utils import ssp_containers


if __name__=='__main__':
    bucket = ssp_containers.ContainerBucket()
    bucket.setup_test("test_10_1588872482_17954", 95,
    "http://192.168.100.50:8080/static/caroline-release/R84-13031.0.0/autotest_server_package.tar.bz2",
    "/usr/local/autotest/results/10-moblab/192.168.231.127", "/usr/local/autotest/results/10-moblab/192.168.231.127/lucifer/control_attach",
    False,
    "container_ssp_job_folder",
    "192.168.231.127")


