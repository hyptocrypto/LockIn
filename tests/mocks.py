class MockService:
    def __init__(self):
        self.service_name = "test"
        self.service_username = "test_user"
        self.service_password = "test_password"
        self.encryption_password = "encrypt"

    @property
    def save_props(self):
        return {
            "service_name": self.service_name,
            "service_username": self.service_username,
            "service_password": self.service_password,
            "encryption_password": self.encryption_password,
        }

    @property
    def query_props(self):
        return {
            "service_name": self.service_name,
            "encryption_password": self.encryption_password,
        }


mock_service = MockService()
