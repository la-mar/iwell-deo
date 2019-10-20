import pytest  # noqa
import re
from datetime import datetime

from collector.request import Request


class TestRequestor:
    def test_get_token(self, requestor):
        assert bool(re.match("Bearer\s.*", requestor.get_token()))

    def test_get_function(self, requestor):
        value = requestor.get_function(
            "since", int(datetime(year=1970, month=1, day=1).timestamp())
        )
        assert value == "since=21600"

    def test_get_function_not_found(self, requestor):
        with pytest.raises(KeyError):
            requestor.get_function(
                "bad_function_name",
                int(datetime(year=1970, month=1, day=1).timestamp()),
            )

    def test_get_function_no_value(self, requestor):
        with pytest.raises(ValueError):
            requestor.get_function("since")

    def test_format_url(self, app_config, requestor):
        assert (
            requestor.format(id=1, id2=2)
            == app_config.API_BASE_URL + "/path/1/subpath/2/values"
        )

    def test_enqueue_new_request(self, app_config, requestor):
        requestor.enqueue(id=1, id2=2)
        request = requestor.requests.pop()
        assert type(request) == Request

    def test_enqueue_request_no_kwargs(self, app_config, requestor):
        with pytest.raises(KeyError):
            requestor.enqueue()
