import os
import sys
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from peewee import *
from lockin.models import Credentials
from typing import Optional

class CredentialsManager:
    def __init__(self, db: "peewee.SqliteDatabase" ):
        self._kdf = PBKDF2HMAC(
            algorithm = hashes.SHA256(),
            length =32, 
            salt = b'Y\xa8B\x85\x8d\x95\xe1\xb9\x0e\x19\x11\x17\x03.\n\x9d',
            iterations = 100000,
            backend = default_backend()
        )
        self._db = db
        self._db.create_tables([Credentials])
        
    def _decrypt(self, service_name: str, password: str) -> Optional(str, str):
        #Test if service_name in in db
        try:
            self._db.open()
            service = Credentials(Credentials.service == service_name)
        except Credentials.DoesNotExist:
            raise Exception(f"Service {service_name} not found")
        finally:    
            self._db.close()
        
        # Encryption 
        key = base64.urlsafe_b64encode(self._kdf.derive(password)) 
        f = Fernet(key)

        # Try to decrypt with given password. If successful, password was correct. 
        try:
            decrypted_username = f.decrypt(service.username)
            decrypted_password = f.decrypt(service.password)
            username = decrypted_username.decode()
            password = decrypted_password.decode()
            return username, password
        except TypeError:
            raise Exception("Password incorrect")
        finally:
            self._db.close()
        
    def _encrypt(
        self, 
        service_name: str, 
        service_username: str,
        service_password: str,
        encryption_password: str) -> Credentials:
        try:
            self._db.open()
            f = Fernet(base64.urlsafe_b64encode(self._kdf.derive(encryption_password)))
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
