"""A module to maintain the reusable constant values"""

class Constants:
    """Class to maintain the reusable constant values in the moblab project."""

    # Dut status
    CLEANING = 'DUT_STATUS_CLEANING'
    PENDING = 'DUT_STATUS_PENDING'
    PROVISIONING = 'DUT_STATUS_PROVISIONING'
    READY = 'DUT_STATUS_READY'
    REPAIRING = 'DUT_STATUS_REPAIRING'
    REPAIR_FAILED = 'DUT_STATUS_REPAIR_FAILED'
    RESETTING = 'DUT_STATUS_RESETTING'
    RUNNING = 'DUT_STATUS_RUNNING'
    UNKNOWN = 'DUT_STATUS_UNKNOWN'

    # The proto fields shared by MoblabHost and MoblabDut
    LAST_UPDATE_TIME = 'last_update_time'
    MOBLAB_HOST_ID = 'moblab_host_id'
    MOBLAB_INSTALL_ID = 'moblab_install_id'
    IP_ADDRESS = 'ip_address'

    # The proto fields of MoblabHost
    BUILD_VERSION = 'build_version'
    CHANNEL = 'channel'
    DESCRIPTION = 'description'
    DISK_STATS = 'disk_stats'
    MILESTONE = 'milestone'
    NETWORK_STATS = 'network_stats'

    # The proto fields of MoblabDut
    BUILD_TARGET = 'build_target'
    IS_LOCKED = 'is_locked'
    LABEL = 'label'
    LOCK_REASON = 'lock_reason'
    MOBLAB_DUT_ID = 'moblab_dut_id'
    MODEL = 'model'
    STATUS = 'status'

    # The keys of Moblab version info dictionary
    BUILD_VERSION_NAME = 'CHROMEOS_RELEASE_VERSION'
    BUILDER_PATH = 'CHROMEOS_RELEASE_BUILDER_PATH'
    CHANNEL_NAME = 'CHROMEOS_RELEASE_TRACK'
    DESCRIPTION_NAME = 'CHROMEOS_RELEASE_DESCRIPTION'
    MILESTONE_NAME = 'CHROMEOS_RELEASE_CHROME_MILESTONE'
    MOBLAB_HOST_ID_NAME = 'MOBLAB_SERIAL_NUMBER'
    MOBLAB_INSTALL_ID_NAME = 'MOBLAB_ID'
