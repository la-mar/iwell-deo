import pytest  # noqa
import re
from datetime import datetime

from attrdict import AttrDict

from collector.collector import Collector
from collector.endpoint import Endpoint

from config import TestingConfig

config = TestingConfig()
endpoints = config.endpoints
functions = config.functions


class TestCollector:
    def test_model_import_from_dotted_path(self, endpoints):
        config_name = "test_collector_import_dotted_model"
        c = Collector(config_name, endpoints[config_name])
        c.model  # any raised error will cause the test to fail

    def test_model_import_from_global_namespace(self, endpoints):
        config_name = "test_collector_import_global_model"
        c = Collector(config_name, endpoints[config_name])
        c.model  # any raised error will cause the test to fail

    def test_create_with_functions_override(self, endpoints):
        endpoint = endpoints["no_mappings"]
        temp = {"test_func": "test_value"}
        c = Collector("test", functions=temp)
        assert c.functions == temp
