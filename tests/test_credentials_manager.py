import pytest
from manager import CredentialsManager
from mocks import mock_service
from exceptions import DuplicateServiceError

test_credentials_manager = CredentialsManager(testing=True)


def test_encrypt_and_decrypt():
    test_credentials_manager.save_service(**mock_service.save_props)
    username, password = test_credentials_manager.fetch_service(
        **mock_service.query_props
    )
    assert username == "test_user"
    assert password == "test_password"


def test_duplicate_service():
    with pytest.raises(DuplicateServiceError):
        test_credentials_manager.save_service(**mock_service.save_props)


def test_update():
    pass


def test_delete():
    deleted = test_credentials_manager.delete_service(**mock_service.query_props)
    assert deleted
