import pytest  # noqa
import re
from datetime import datetime

from collector.requestor import IWellRequestor


# @pytest.fixture()
# def iwell_requestor(app_config, endpoint, functions):
#     yield IWellRequestor(app_config.API_BASE_URL, endpoint=endpoint)


# class TestIWellRequestor:
#     def test_has_default_auth(self, iwell_requestor):
#         bool(re.match("Bearer\s.*", iwell_requestor.headers["Authorization"]))

#     def test_add_since(self, iwell_requestor):
#         ts = datetime(year=1970, month=1, day=1)
#         iwell_requestor.add_since(since=ts)
#         iwell_requestor.params["since"] = ts

#     def test_add_start(self, iwell_requestor):
#         ts = datetime(year=1970, month=1, day=1)
#         iwell_requestor.add_start(start=ts)
#         iwell_requestor.params["start"] = ts

#     def test_add_end(self, iwell_requestor):
#         ts = datetime(year=1970, month=1, day=1)
#         iwell_requestor.add_end(end=ts)
#         iwell_requestor.params["end"] = ts
