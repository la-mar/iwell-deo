import pytest  # pylint: disable=unused-import
import requests
import re
from datetime import datetime
from requests_mock import ANY


class TestRequest:
    def test_request_path(self, req):
        assert req.path == "/v3/path/1/subpath/2/values"

    def test_request_get(self, req, requests_mock):
        requests_mock.register_uri("GET", ANY, text="response_text")
        assert req.get().text == "response_text"

    def test_request_has_auth_header(self, req, requests_mock):
        requests_mock.register_uri("GET", ANY, text="response_text")
        response = req.get()
        auth_header = response.request.headers["Authorization"]
        assert bool(re.match("Bearer\s.*", auth_header))
