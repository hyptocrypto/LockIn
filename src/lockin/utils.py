import base64
import os
from datetime import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from lockin.settings import NETWORK_DB_URI, DB_URI, SALT
from lockin.models import Credentials, Connections, NetCredentials, NetConnections
from lockin.exceptions import ServiceAlreadyExists, ServiceNotFound
from peewee import SqliteDatabase
from typing import Optional, Tuple
import shutil


class CredentialsManager:
    """Main interface for interacting with the data layer"""

    def __init__(self):
        # Init manager and db
        self._db = SqliteDatabase(DB_URI)
        self._db.connect()
        self._db.create_tables([Credentials, Connections])
        self._db.close()

        if os.path.exists(NETWORK_DB_URI):
            self._network_db = SqliteDatabase(NETWORK_DB_URI)
            self._network_db.connect()
            self._network_db.create_tables([NetCredentials, NetConnections])
            self._network_db.close()
        else:
            self._network_db = None

    def startup(self):
        """
        When the app starts, check if the network share db exists (if on local network).
        If it does, compare the two db's, and treat the one with the most recent connection
        as the master. If the network share is the master (most recently edited),
        update the local db with the data from the master. Otherwise, update the network share k
        """
        if self._network_db:
            try:
                self._network_db.connect()
                last_network_db_connection = (
                    NetConnections.select()
                    .order_by(NetConnections.timestamp.desc())
                    .get(NetConnections.timestamp)
                )
                self._network_db.close()

                self._db.connect()
                last_local_db_connection = (
                    Connections.select()
                    .order_by(Connections.timestamp.desc())
                    .get(Connections.timestamp)
                )
                self._db.close()

                if last_network_db_connection > last_local_db_connection:
                    shutil.copy(NETWORK_DB_URI, DB_URI)

            finally:
                self._network_db.close()
                self._db.close()

    def shutdown(self, cls):
        """
        Update the most recent connection to the db, make a backup,
        and update the network based database.
        This method is called by the main toga apps on_exit method.
        """
        Connections.create(timestamp=datetime.now())
        shutil.copy(DB_URI, f"{DB_URI}.backup")

        # If connected to local network, update network db.
        if self._network_db:
            shutil.copy(DB_URI, NETWORK_DB_URI)
            shutil.copy(DB_URI, f"{NETWORK_DB_URI}.backup")

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
            service = Credentials.get(Credentials.service == service_name.lower())
        except Credentials.DoesNotExist:
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
            service_list = [row.service for row in Credentials.select()]

            if service_name in service_list:
                raise ServiceAlreadyExists(f"Service {service_name} already exists.")

            encrypted_username = f.encrypt(service_username.encode())
            encrypted_password = f.encrypt(service_password.encode())

            # Create new entry in the db
            return Credentials.create(
                service=service_name,
                username=encrypted_username,
                password=encrypted_password,
            )
        # Catch if something goes wrong
        # Pass the exception up so the app can handle if ServiceAlreadyExists exception is thrown
        except Exception as e:
            raise e
        finally:
            self._db.close()

    def list_services(self):
        self._db.connect()
        services = sorted([row.service.capitalize() for row in Credentials.select()])
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
                delete = Credentials.delete().where(
                    Credentials.service == service_name.lower()
                )
                delete.execute()
                return True
        except TypeError:
            return
