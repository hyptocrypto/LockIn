from asyncio.proactor_events import _ProactorBaseWritePipeTransport
import os
from typing import Callable
from settings import PASSWORD, NAS_HOST, NETWORK_SHARE_URI


class SMBClient:
    "Main connector for network volumes"

    def __init__(self):
        self.pre_connected = os.path.isdir(NETWORK_SHARE_URI)

    def __enter__(self):
        if not self.pre_connected:
            os.system("echo %s|sudo -S %s" % (PASSWORD, f"mkdir {NETWORK_SHARE_URI}"))
            os.system(
                "echo %s|sudo -S %s"
                % (PASSWORD, f"mount_smbfs {NAS_HOST} {NETWORK_SHARE_URI}")
            )
        return self

    def __exit__(self):
        if not self.pre_connected:
            os.system("echo %s|sudo -S %s" % (PASSWORD, f"umount {NETWORK_SHARE_URI}"))
