import pytest  # noqa
import requests
import re
from datetime import datetime

from requests_mock import ANY

from collector.token_manager import TokenManager

expected_url = "https://api.example.com/v3/path/to/endpoint"


@pytest.mark.usefixtures("mocker")
class TestTokenManager:
    def test_legacy_client_get_token(self, token_manager_legacy):
        # pylint: disable=anomalous-backslash-in-string
        assert bool(re.match("Bearer\s.*", token_manager_legacy.get_token()))

    def test_legacy_client_get_token_dict(self, token_manager_legacy):
        expected = ["access_token", "expires_at", "expires_in", "token_type"]
        token = list(token_manager_legacy.get_token_dict().keys())
        assert expected == token
