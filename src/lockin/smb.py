import os
import subprocess
from settings import PASSWORD, NAS_HOST, NETWORK_SHARE_URI
from exceptions import NetworkShareConnectionError


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
            subprocess.run(
                "echo %s|sudo -S %s" % (PASSWORD, f"mkdir {NETWORK_SHARE_URI}"),
                shell=True,
                timeout=5,
            )

        # Mount share
        print("Checking for network share.")
        try:
            subprocess.run(
                "echo %s|sudo -S %s"
                % (PASSWORD, f"mount_smbfs {NAS_HOST} {NETWORK_SHARE_URI}"),
                shell=True,
                timeout=5,
            )
        except subprocess.TimeoutExpired:
            pass

        if not os.path.ismount(NETWORK_SHARE_URI):
            raise NetworkShareConnectionError(
                f"Net work share not mounted at location: '{NETWORK_SHARE_URI}'"
            )

        return self

    def __exit__(self, *args):
        """ "Check if network share was pre-mounted. If not, unmount"""
        if self.pre_connected:
            return
        subprocess.run(
            "echo %s|sudo -S %s" % (PASSWORD, f"umount {NETWORK_SHARE_URI}"),
            shell=True,
            timeout=5,
        )


# TESTING BLOCK
if __name__ == "__main__":
    with SMBClient() as cliient:
        subprocess.run("echo %s|sudo -S %s" % (PASSWORD, f"ls {NETWORK_SHARE_URI}"))
