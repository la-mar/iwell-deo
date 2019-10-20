import pytest  # noqa
import requests
import re
from datetime import datetime
from flask_sqlalchemy import Model

from collector.endpoint import Endpoint, load_from_config


class TestEndpoint:
    # def test_endpoints_load_from_config(self, app_config):
    #     assert all([type(e) == Endpoint for e in load_from_config(app_config)])

    def test_located_entity_is_subclass_of_model(self, endpoint):
        assert Model in endpoint.model.__mro__

    def test_located_dependency_is_subclass_of_model(self, endpoint):
        assert Model in endpoint.depends_on["test_id"].__mro__

    def test_missing_keys_are_handled(self, endpoints):
        endpoints["no_keys"]

    def test_missing_model_is_handled(self, endpoints):
        endpoints["no_model"]
