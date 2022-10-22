import os
import subprocess
from settings import PASSWORD, NAS_HOST, NETWORK_SHARE_URI
from exceptions import NetworkShareConnectionError


class SMBClient:
    """
    Context manager to handle the connection and disconnection of network volumes
    """

    def __init__(self):
        self.pre_connected = os.path.ismount(NETWORK_SHARE_URI)

    def _run_cmd(self, cmd):
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
            timeout=5,
        )

    def __enter__(self):
        """Check if network share is already mounted. If not mount the share"""
        if self.pre_connected:
            return self
        if not PASSWORD:
            raise NetworkShareConnectionError(f"Sudo password missing.")

        # Create NETWORK_SHARE_URI dir if needed
        if not os.path.isdir(NETWORK_SHARE_URI):
            mkdir_cmd = "echo %s|sudo -S %s" % (PASSWORD, f"mkdir {NETWORK_SHARE_URI}")
            self._run_cmd(mkdir_cmd)

        # Mount share
        try:
            mount_cmd = "echo %s|sudo -S %s" % (
                PASSWORD,
                f"mount_smbfs {NAS_HOST} {NETWORK_SHARE_URI}",
            )
            self._run_cmd(mount_cmd)

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
        unmount_cmd = "echo %s|sudo -S %s" % (PASSWORD, f"umount {NETWORK_SHARE_URI}")
        self._run_cmd(unmount_cmd)


def with_smb(func):
    """Decorator to call functions within an SMBClient try except block"""

    def wrap(*args):
        try:
            with SMBClient():
                func(*args)
        except NetworkShareConnectionError:
            pass

    return wrap


# TESTING BLOCK
if __name__ == "__main__":

    @with_smb
    def test():
        breakpoint()

    test()
