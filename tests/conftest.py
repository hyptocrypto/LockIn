from settings import TESTING_DB_URI
import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def gen_test_db(request):    
    def tear_down():
        os.remove(TESTING_DB_URI)
    request.addfinalizer(tear_down)
