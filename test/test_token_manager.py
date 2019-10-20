import pytest  # noqa
import requests
import re
from datetime import datetime

from collector.token_manager import TokenManager

expected_url = "https://api.example.com/v3/path/to/endpoint"


class TestTokenManager:
    def test_legacy_client_get_token(self, token_manager_legacy, requests_mock):
        requests_mock.register_uri(
            "GET", token_manager_legacy.url, text="Bearer blah_blah_blah"
        )
        assert bool(re.match("Bearer\s.*", token_manager_legacy.get_token()))

    def test_legacy_client_get_token_dict(self, token_manager_legacy):
        expected = ["access_token", "expires_at", "expires_in", "token_type"]
        token = list(token_manager_legacy.get_token_dict().keys())
        assert expected == token

    def test_token_urljoin_vanilla(self, app_config):
        url = app_config.API_BASE_URL
        path = "/path/to/endpoint"
        TokenManager.urljoin(url, path) == expected_url

    def test_token_urljoin_double_slash(self, app_config):
        url = f"{app_config.API_BASE_URL}/"
        path = "/path/to/endpoint"
        assert TokenManager.urljoin(url, path) == expected_url

    def test_token_urljoin_no_slash(self, app_config):
        url = app_config.API_BASE_URL
        path = "path/to/endpoint"
        assert TokenManager.urljoin(url, path) == expected_url

