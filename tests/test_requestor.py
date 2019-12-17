import pytest  # noqa
import re
from datetime import datetime

from requests import Session

from collector.request import Request
from collector.requestor import Requestor


class TestRequestor:
    def test_repr(self, requestor):
        repr(requestor)

    def test_iter(self, requestor):
        list(requestor)

    def test_session_property(self, requestor):
        assert isinstance(requestor.session, Session)
        assert isinstance(requestor.s, Session)
        requestor.session = Session()
        assert isinstance(requestor.session, Session)

    def test_get_token(self, requestor):
        assert bool(re.match("Bearer\s.*", requestor.get_token()))

    def test_get_function(self, requestor):
        value = requestor.get_function(
            "since", int(datetime(year=1970, month=1, day=1).timestamp())
        )
        assert value == "since=21600"

    def test_get_function_with_values(self, requestor):
        value = requestor.get_function(func_name="since_values", values=[1, 2, 3])
        assert value == "since_values=1,2,3"

    def test_get_function_not_found(self, requestor):
        with pytest.raises(KeyError):
            requestor.get_function(
                "bad_function_name",
                int(datetime(year=1970, month=1, day=1).timestamp()),
            )

    def test_get_function_no_value(self, requestor):
        with pytest.raises(ValueError):
            requestor.get_function("since")

    def test_get_function_bad_values(self, requestor):
        with pytest.raises(Exception):
            requestor.get_function("since", values={[]})

    def test_add_param(self, conf, endpoint):
        r = Requestor(conf.API_BASE_URL, endpoint, {})
        r.add_param("test_param", 33)
        assert r.params["test_param"] == "33"

    def test_add_param_bad_args(self, requestor):
        with pytest.raises(Exception):
            requestor.add_param({}, None)

    def test_format_url(self, conf, requestor):
        expected = conf.API_BASE_URL + "/path/1/subpath/2/values"
        assert requestor.format(id=1, id2=2) == expected

    def test_format_url(self, requestor):
        with pytest.raises(KeyError):
            requestor.format()

    def test_enqueue_new_request(self, requestor):
        requestor.enqueue(id=1, id2=2)
        request = requestor.requests.pop()
        assert type(request) == Request

    def test_enqueue_request_no_kwargs(self, requestor):
        with pytest.raises(KeyError):
            requestor.enqueue()

    def test_get_all(self, requestor_simple, requests_mock):
        requests_mock.register_uri("GET", requestor_simple.url, text="not_important")
        requestor_simple.enqueue(id=1, id2=2)
        requestor_simple.enqueue(id=1, id2=2)
        requestor_simple.enqueue(id=1, id2=2)
        assert len(list(requestor_simple.get_all())) == 3
