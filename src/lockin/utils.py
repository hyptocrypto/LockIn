import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from lockin.settings import DB_URI
from lockin.models import Credentials
from peewee import SqliteDatabase
from typing import Optional, Tuple

class CredentialsManager:
    """Main interface for interacting with the data layer"""
    def __init__(self):
        # Init manager and db
        self._db = SqliteDatabase(DB_URI)
        self._db.connect()
        self._db.create_tables([Credentials])
        self._db.close()
        
    def _gen_kdf(self) -> PBKDF2HMAC:
        """
        Fernet limits use encryption keys to a single use. 
        This method will return a new kdf (key derivation function).
        This way each encryption or decryption actions will use a new kdf. 
        """
        return PBKDF2HMAC(
        algorithm = hashes.SHA256(),
        length =32, 
        salt = b'Y\xa8B\x85\x8d\x95\xe1\xb9\x0e\x19\x11\x17\x03.\n\x9d',
        iterations = 100000,
        backend = default_backend()
        )
        
    def _decrypt(self, service_name: str, encryption_password: str) -> Optional[Tuple[str, str]]:
        """
        Check for given service name in db, if found, try to decrypt it.
        If decryption is successful, the username and password are returned
        """
        #Test if service_name in in db
        try:
            self._db.connect()            
            service = Credentials.get(Credentials.service == service_name.lower())
        except Credentials.DoesNotExist:
            raise Exception(f"Service {service_name} not found")
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
        encryption_password: str) -> Optional[Credentials]:
        """
        Use given :param encryption_password to encrypt the username and password, and save them to db under :param service_name
        """
        try:
            self._db.connect()
            kdf = self._gen_kdf()
            f = Fernet(base64.urlsafe_b64encode(kdf.derive(encryption_password.encode())))
            service_list = [row.service for row in Credentials.select()]
            
            if service_name in service_list:
                raise Exception(f"Service {service_name} already exists.")
            
            encrypted_username = f.encrypt(service_username.encode())
            encrypted_password = f.encrypt(service_password.encode())

            # Create new entry in the db
            return Credentials.create(
                service = service_name,
                username = encrypted_username,
                password = encrypted_password
            )
            
        except Exception as e:
            raise Exception(f"Error encrypting credentials: {e}")
        finally:
            self._db.close()
            
            
    def list_services(self):
        self._db.connect()
        services = sorted([row.service.capitalize() for row in Credentials.select()])
        self._db.close()
        return services

    def save_service(self, service_name, service_username, service_password, encryption_password):
        saved = self._encrypt(service_name, service_username, service_password, encryption_password)
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
                delete =Credentials.delete().where(Credentials.service == service_name.lower())
                delete.execute()
                return True
        except TypeError:
            return
        
            return
        
            return
        
