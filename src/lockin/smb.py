import os
from settings import PASSWORD, NAS_HOST, NETWORK_SHARE_URI


class SMBClient:
    """
    Main connector for network volumes
    TODO: Add some edge case / error handling for if sys calls fail
    """

    def __init__(self):
        self.pre_connected = os.path.ismount(NETWORK_SHARE_URI)

    def __enter__(self):
        """Check if network share is already mounted. If not mount the share"""
        if self.pre_connected:
            return self

        # Create NETWORK_SHARE_URI dir if needed
        if not os.path.isdir(NETWORK_SHARE_URI):
            os.system("echo %s|sudo -S %s" % (PASSWORD, f"mkdir {NETWORK_SHARE_URI}"))

        # Mount share
        os.system(
            "echo %s|sudo -S %s"
            % (PASSWORD, f"mount_smbfs {NAS_HOST} {NETWORK_SHARE_URI}")
        )

        return self

    def __exit__(self, *args):
        """ "Check if network share was pre-mounted. If not, unmount"""
        if self.pre_connected:
            return
        os.system("echo %s|sudo -S %s" % (PASSWORD, f"umount {NETWORK_SHARE_URI}"))


# TESTING BLOCK
if __name__ == "__main__":
    with SMBClient() as cliient:
        os.system("echo %s|sudo -S %s" % (PASSWORD, f"ls {NETWORK_SHARE_URI}"))
