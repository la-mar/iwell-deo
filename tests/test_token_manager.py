import pytest  # noqa
import requests
import re
from datetime import datetime

from requests_mock import ANY

from collector.token_manager import TokenManager

expected_url = "https://api.example.com/v3/path/to/endpoint"


class TestTokenManager:
    def test_legacy_client_get_token(self, token_manager_legacy, requests_mock):
        requests_mock.register_uri(ANY, ANY, text="Bearer ersvbteyh536425q3r")
        assert bool(re.match(r"Bearer\s.*", token_manager_legacy.get_token()))

    def test_legacy_client_get_token_dict(self, token_manager_legacy, requests_mock):
        requests_mock.register_uri(
            ANY,
            ANY,
            json='{"access_token": "", "expires_at": 1577149458, "expires_in": 604800, "token_type": "Bearer"}',
        )

        expected = ["access_token", "expires_at", "expires_in", "token_type"]
        token = list(token_manager_legacy.get_token_dict().keys())
        assert expected == token

    def test_token_urljoin_vanilla(self, conf):
        url = conf.API_BASE_URL
        path = "/path/to/endpoint"
        assert TokenManager.urljoin(url, path) == expected_url

    def test_token_urljoin_double_slash(self, conf):
        url = f"{conf.API_BASE_URL}/"
        path = "/path/to/endpoint"
        assert TokenManager.urljoin(url, path) == expected_url

    def test_token_urljoin_no_slash(self, conf):
        url = conf.API_BASE_URL
        path = "path/to/endpoint"
        assert TokenManager.urljoin(url, path) == expected_url

