import pytest
from manager import CredentialsManager
from mocks import mock_service
from exceptions import DuplicateServiceError, ServiceNotFound

test_credentials_manager = CredentialsManager(testing=True)

SERVICE_UPDATE_NAME = "new_test_name"


@pytest.fixture(scope="module", autouse=True)
def init_service():
    """Create mock_service and yield execution. Resume and delete possible test services."""

    test_credentials_manager.save_service(**mock_service.save_props)
    yield

    try:
        test_credentials_manager.delete_service(**mock_service.query_props)
    except TypeError:
        pass
    except ServiceNotFound:
        pass

    try:
        test_credentials_manager.delete_service(
            SERVICE_UPDATE_NAME, mock_service.encryption_password
        )
    except TypeError:
        pass
    except ServiceNotFound:
        pass


def test_decrypt(init_service):
    username, password = test_credentials_manager.fetch_service(
        **mock_service.query_props
    )
    assert username == "test_user"
    assert password == "test_password"


def test_edit(init_service):
    test_credentials_manager.edit_service(
        **mock_service.query_props,
        update_username="new_test_username",
        update_password="new_test_password"
    )
    edited_username, edited_password = test_credentials_manager.fetch_service(
        **mock_service.query_props
    )
    assert edited_username == "new_test_username"
    assert edited_password == "new_test_password"

    test_credentials_manager.edit_service(
        **mock_service.query_props, update_name="new_test_name"
    )
    edited_username, edited_password = test_credentials_manager.fetch_service(
        "new_test_name", mock_service.encryption_password
    )

    assert edited_username == "new_test_username"
    assert edited_password == "new_test_password"


def test_duplicate_service(init_service):
    test_credentials_manager.save_service(**mock_service.save_props)
    with pytest.raises(DuplicateServiceError):
        test_credentials_manager.save_service(**mock_service.save_props)


def test_delete(init_service):
    deleted = test_credentials_manager.delete_service(**mock_service.query_props)
    assert deleted
