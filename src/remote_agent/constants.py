"""A module to maintain the reusable constant values"""

from moblab_common import constants

class Constants(constants.Constants):
    """Class to maintain all reusable constant values within remote agent."""

    # The proto fields of NetworkStats
    BROKEN_CONNECTIONS = 'broken_connections'
    DOWNLOAD_BITS_PER_SECOND = 'download_bits_per_second'
    SERVER_ERRORS = 'server_errors'
    UPLOAD_BITS_PER_SECOND = 'upload_bits_per_second'

    # The proto fields of DiskStats
    FREE_DISK_SIZE_BYTES = 'free_disk_size_bytes'
    TOTAL_DISK_SIZE_BYTES = 'total_disk_size_bytes'
