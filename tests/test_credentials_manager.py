import pytest
from lockin.manager import CredentialsManager
from lockin.exceptions import ServiceAlreadyExists

test_credentials_manager = CredentialsManager(testing=True)

def test_encrypt_and_decrypt():
    test_credentials_manager.save_service(
        service_name="test",
        service_username="test_user", 
        service_password="test_password", 
        encryption_password="encrypt"
    )
    username, password = test_credentials_manager.fetch_service(
        service_name="test", encryption_password="encrypt"
    )
    assert username == "test_user"
    assert password == "test_password"

def test_duplicate_service():
    with pytest.raises(ServiceAlreadyExists):
        test_credentials_manager.save_service(
        service_name="test",
        service_username="test_user", 
        service_password="test_password", 
        encryption_password="encrypt"
        )

def test_delete():
    deleted = test_credentials_manager.delete_service(service_name='test', encryption_password="encrypt")
    assert deleted
