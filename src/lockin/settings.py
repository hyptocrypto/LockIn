import os

# Name of DB owner
HOST = "julian"

# DB location if on a network share
NETWORK_DB_URI = f"/Volumes/NAS/{HOST}_credentials.db"

# Location of DB on host without network share
DB_URI = os.path.join(os.path.expanduser("~"), f"{HOST}_credentials.db")


SALT = b"Y\xa8B\x85\x8d\x95\xe1\xb9\x0e\x19\x11\x17\x03.\n\x9d"
