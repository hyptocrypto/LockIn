import base64
import os
from datetime import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from lockin.settings import NETWORK_SHARE_URI, NETWORK_DB_URI, TESTING_DB_URI, DB_URI, SALT
from lockin.models import Credentials, Connections, NetCredentials, NetConnections, TestCredentials, TestConnections
from lockin.exceptions import ServiceAlreadyExists, ServiceNotFound
from peewee import SqliteDatabase
from typing import Optional, Tuple
import shutil


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
            

            # If host is connected to network share
            if os.path.exists(NETWORK_SHARE_URI):
                self._network_db = SqliteDatabase(NETWORK_DB_URI)
                with self._network_db:
                    self._network_db.create_tables([NetCredentials, NetConnections])
            else:
                self._network_db = None

            self._startup()

    def _update_network_db(self):
        """
        Whenever we add or delete a record from the db,
        we update the most recent connection and push the newly updated db file to the network share
        """
        self.connections.create(timestamp=datetime.now())
        if self._network_db:
            shutil.copyfile(DB_URI, NETWORK_DB_URI)

    def _startup(self):
        """
        When the app starts, check if the network share db exists (if on local network).
        If it does, compare the two db's, and treat the one with the most recent connection
        as the master.
        """
        if self._network_db:
            with self._network_db:
                last_network_db_connections = NetConnections.select().order_by(
                    NetConnections.timestamp.desc()
                )

                if len(last_network_db_connections):
                    last_network_db_connection = last_network_db_connections[
                        0
                    ].timestamp
                else:
                    last_network_db_connection = None

            with self._db:
                last_local_db_connections = self.connections.select().order_by(
                    self.connections.timestamp.desc()
                )
                if len(last_local_db_connections):
                    last_local_db_connection = last_local_db_connections[0].timestamp
                else:
                    last_local_db_connection = None

            # If connections from local db and network db exists, compare and update the older db
            if last_network_db_connection and last_local_db_connection:
                if last_network_db_connection > last_local_db_connection:
                    shutil.copy(NETWORK_DB_URI, DB_URI)
                    
                if last_local_db_connection > last_network_db_connection:
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
            service = self.credentials.get(self.credentials.service == service_name.lower())
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

            if service_name in service_list:
                raise ServiceAlreadyExists(f"Service {service_name} already exists.")

            encrypted_username = f.encrypt(service_username.encode())
            encrypted_password = f.encrypt(service_password.encode())

            # Create new entry in the db
            new_credentials = self.credentials.create(
                service=service_name,
                username=encrypted_username,
                password=encrypted_password,
            )
            # If new credentials created, update the network db
            if new_credentials:
                self._update_network_db()
                return new_credentials

        # Catch if something goes wrong
        # Pass the exception up so the app can handle if ServiceAlreadyExists exception is thrown
        except Exception as e:
            raise e
        finally:
            self._db.close()

    def list_services(self):
        self._db.connect()
        services = sorted([row.service.capitalize() for row in self.credentials.select()])
        self._db.close()
        return services

    def save_service(
        self, service_name, service_username, service_password, encryption_password
    ):
        saved = self._encrypt(
            service_name, service_username, service_password, encryption_password
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

    def delete_service(self, service_name, encryption_password):
        try:
            username, password = self._decrypt(service_name, encryption_password)
            if all([username, password]):
                delete = self.credentials.delete().where(
                    self.credentials.service == service_name.lower()
                )
                delete.execute()
                self._update_network_db()
                return True
        except TypeError:
            return
