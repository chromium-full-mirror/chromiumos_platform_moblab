from moblab_common.dut_connector import (
    MoblabDUTConnector,
    MoblabDUTConnectorException,
)


class MoblabDUTConnectorForFwupd(MoblabDUTConnector):
    def get_peripheral_information(self, ip_address):
        (host, stdout, stderr, exit_code) = self.run_command_on_ips(
            "fwupdmgr get-devices --json", [ip_address]
        )[0]
        if exit_code != 0:
            raise MoblabDUTConnectorException(
                f"not able to retrieve peripheral information. Error: {stderr}"
            )
        return stdout
