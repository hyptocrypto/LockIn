import random
import string

import base64
import os
import shutil
from datetime import datetime
from typing import Optional, Tuple

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from exceptions import DuplicateServiceError, ServiceNotFound
from models import (
    Connections,
    Credentials,
    NetConnections,
    NetCredentials,
    TestConnections,
    TestCredentials,
)
from peewee import SqliteDatabase
from settings import DB_URI, NETWORK_DB_URI, NETWORK_SHARE_URI, SALT, TESTING_DB_URI
from smb import with_smb


class CredentialsManager:
    """Main interface for interacting with the data layer"""

    def __init__(self, testing=False):
        """
        The CredentialsManager can use up to three db files.
        One for testing, one on a local network share to sync the db across devices on the same network,
        and the main local file saved to the users home dir.
        """
        if testing:
            self._db = SqliteDatabase(TESTING_DB_URI)
            self.credentials = TestCredentials
            self.connections = TestConnections

            with self._db:
                self._db.create_tables([TestCredentials, TestConnections])
            self._network_db = None
        else:
            # Init manager and db
            self._db = SqliteDatabase(DB_URI)
            self.credentials = Credentials
            self.connections = Connections
            with self._db:
                self._db.create_tables([Credentials, Connections])

            self._network_db = SqliteDatabase(NETWORK_DB_URI)
            # If host is connected to network share, sanity check to create tables.
            if os.path.ismount(NETWORK_SHARE_URI):
                with self._network_db:
                    self._network_db.create_tables([NetCredentials, NetConnections])

            self._startup()

    @with_smb
    def _update_network_db(self):
        """
        Whenever adding or deleting a record from the db,
        we update the connections table and push the newly updated db file to the network share
        """
        shutil.copyfile(DB_URI, NETWORK_DB_URI)

    @with_smb
    def _startup(self):
        """
        When the app starts, check if the network share db exists (if on local network).
        If it does, compare the two db's, and treat the one with the most recent connection
        as the master.
        """
        with self._network_db:
            last_network_db_connections = NetConnections.select().order_by(
                NetConnections.timestamp.desc()
            )

            if last_network_db_connections.exists():
                last_network_db_connection = (
                    last_network_db_connections.first().timestamp
                )
            else:
                last_network_db_connection = None

        with self._db:
            last_local_db_connections = self.connections.select().order_by(
                self.connections.timestamp.desc()
            )
            if last_local_db_connections.exists():
                last_local_db_connection = last_local_db_connections.first().timestamp
            else:
                last_local_db_connection = None

        # If connections from local db and network db exists, compare and update the older db
        if last_network_db_connection and last_local_db_connection:
            ()
            if last_network_db_connection > last_local_db_connection:
                shutil.copy(NETWORK_DB_URI, DB_URI)

            if last_network_db_connection < last_local_db_connection:
                shutil.copy(DB_URI, NETWORK_DB_URI)

    def shutdown(self, cls):
        """
        Make a local backup of the db file.
        This method is called by the main toga apps on_exit method.
        """
        shutil.copy(DB_URI, f"{DB_URI}.backup")

        return cls

    def _gen_kdf(self) -> PBKDF2HMAC:
        """
        Fernet limits use encryption keys to a single use.
        This method will return a new kdf (key derivation function).
        This way each encryption or decryption actions will use a new kdf.
        """
        return PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=SALT,
            iterations=100000,
            backend=default_backend(),
        )

    def _decrypt(
        self, service_name: str, encryption_password: str
    ) -> Optional[Tuple[str, str]]:
        """
        Check for given service name in db, if found, try to decrypt it.
        If decryption is successful, the username and password are returned
        """
        # Test if service_name in in db
        try:
            self._db.connect()
            service = self.credentials.get(
                self.credentials.service == service_name.lower()
            )
        except self.credentials.DoesNotExist:
            raise ServiceNotFound(f"Service {service_name} not found")
        finally:
            self._db.close()

        # Encryption
        kdf = self._gen_kdf()
        f = Fernet(base64.urlsafe_b64encode(kdf.derive(encryption_password.encode())))

        # Try to decrypt with given password. If successful, password was correct.
        try:
            decrypted_username = f.decrypt(service.username.encode())
            decrypted_password = f.decrypt(service.password.encode())
            username = decrypted_username.decode()
            password = decrypted_password.decode()
            return username, password
        except InvalidToken:
            return
        finally:
            self._db.close()

    def _encrypt(
        self,
        service_name: str,
        service_username: str,
        service_password: str,
        encryption_password: str,
    ) -> Optional[Credentials]:
        """
        Use given :param encryption_password to encrypt the username and password, and save them to db under :param service_name
        """
        try:
            self._db.connect()
            kdf = self._gen_kdf()
            f = Fernet(
                base64.urlsafe_b64encode(kdf.derive(encryption_password.encode()))
            )
            service_list = [row.service for row in self.credentials.select()]

            if service_name.lower() in service_list:
                raise DuplicateServiceError(f"Service {service_name} already exists.")

            encrypted_username = f.encrypt(service_username.encode())
            encrypted_password = f.encrypt(service_password.encode())

            # Create new entry in the db
            new_credentials = self.credentials.create(
                service=service_name.lower(),
                username=encrypted_username,
                password=encrypted_password,
            )
            # If new credentials created, update the network db
            if new_credentials:
                self.connections.create(timestamp=datetime.now())
                self._update_network_db()
                return new_credentials

        # Catch if something goes wrong
        except Exception as e:
            raise e
        finally:
            self._db.close()

    def gen_random_pass(self) -> str:
        chrs = string.ascii_letters + string.digits + string.punctuation
        return "".join([random.choice(chrs) for _ in range(15)])

    def list_services(self):
        self._db.connect()
        services = sorted(
            [row.service.capitalize() for row in self.credentials.select()]
        )
        self._db.close()
        return services

    def save_service(
        self, service_name, service_username, service_password, encryption_password
    ):
        saved = self._encrypt(
            service_name.lower(),
            service_username,
            service_password or self.gen_random_pass(),
            encryption_password,
        )
        if saved:
            return True
        return

    def fetch_service(self, service_name, encryption_password):
        try:
            username, password = self._decrypt(service_name, encryption_password)
            return username, password
        except TypeError:
            return

    def edit_service(
        self,
        service_name,
        encryption_password,
        update_name=None,
        update_username=None,
        update_password=None,
    ):
        service_name = service_name.lower()
        username, password = self._decrypt(service_name, encryption_password)
        if username and password:
            self.credentials.delete().where(
                self.credentials.service == service_name.lower()
            ).execute()
            saved = self._encrypt(
                (update_name or service_name).lower(),
                update_username or username,
                update_password or password,
                encryption_password,
            )
            return saved
        else:
            print("Error")

    def delete_service(self, service_name, encryption_password):
        try:
            username, password = self._decrypt(service_name, encryption_password)
            if all([username, password]):
                self.credentials.delete().where(
                    self.credentials.service == service_name.lower()
                ).execute()
                self.connections.create(timestamp=datetime.now())
                self._update_network_db()
                return True
        except TypeError:
            return
