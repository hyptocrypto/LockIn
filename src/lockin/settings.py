import os

# Name of DB owner
HOST = "julian"

PASSWORD = ""

# Local mount point location of network share
NETWORK_SHARE_URI = "/Volumes/NAS/"

# Host of the net work share
NAS_HOST = "//guest:@192.168.1.69/NAS"

# DB location if on a network share
NETWORK_DB_URI = os.path.join(NETWORK_SHARE_URI, f"{HOST}_credentials.db")

# Location of DB on host without network share
DB_URI = os.path.join(os.path.expanduser("~"), f"{HOST}_credentials.db")

# Testing db location
TESTING_DB_URI = os.path.join(os.path.expanduser("~"), "__TESTING_DB.db")

# Encryption salt NOTE: Find a better way to store this
SALT = b"Y\xa8B\x85\x8d\x95\xe1\xb9\x0e\x19\x11\x17\x03.\n\x9d"
