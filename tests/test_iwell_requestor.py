# pylint: disable: unused-argument
import pytest
import re
from datetime import datetime

# from requests_mock import ANY

from collector.requestor import IWellRequestor
from collector.endpoint import Endpoint


@pytest.fixture()
def iwell_requestor(conf, endpoint):
    yield IWellRequestor(conf.API_BASE_URL, endpoint=endpoint)


@pytest.mark.usefixtures("mocker")
class TestIWellRequestor:
    def test_has_default_auth(self, iwell_requestor):
        # pylint: disable=anomalous-backslash-in-string
        bool(re.match("Bearer\s.*", iwell_requestor.headers["Authorization"]))

    def test_add_since(self, iwell_requestor):
        ts = datetime(year=1970, month=1, day=1)
        iwell_requestor.add_since(since=ts)
        assert iwell_requestor.params["since"] == str(int(ts.timestamp()))

    def test_add_start(self, iwell_requestor):
        ts = datetime(year=1970, month=1, day=1)
        iwell_requestor.add_start(start=ts)
        assert iwell_requestor.params["start"] == ts.date().isoformat()

    def test_add_end(self, iwell_requestor):
        ts = datetime(year=1970, month=1, day=1)
        iwell_requestor.add_end(end=ts)
        assert iwell_requestor.params["end"] == ts.date().isoformat()

    def test_constructor_kwargs_since(self, conf, endpoint):
        IWellRequestor(
            conf.API_BASE_URL,
            endpoint=endpoint,
            since=datetime(year=1970, month=1, day=1),
        )

    def test_constructor_kwargs_start(self, conf, endpoint):
        IWellRequestor(
            conf.API_BASE_URL,
            endpoint=endpoint,
            start=datetime(year=1970, month=1, day=1),
        )

    def test_constructor_kwargs_end(self, conf, endpoint):
        IWellRequestor(
            conf.API_BASE_URL,
            endpoint=endpoint,
            end=datetime(year=1970, month=1, day=1),
        )

    def test_constructor_endpoint_mode_delta(self, conf, endpoint):
        r = IWellRequestor(conf.API_BASE_URL, endpoint=endpoint, mode="full",)
        assert (
            r.params["start"] == datetime(year=1970, month=1, day=1).date().isoformat()
        )

    def test_queue_request(self, iwell_requestor):
        iwell_requestor.enqueue_with_ids(id=1, id2=2)
        iwell_requestor.enqueue_with_ids(id=1, id2=2)
        iwell_requestor.enqueue_with_ids(id=1, id2=2)
        assert len(list(iwell_requestor.get_all())) == 3
