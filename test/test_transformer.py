import pytest  # noqa
import re
from datetime import datetime

from iwell.collector.transformer import Transformer


class TestTransformer:
    def test_transform_normalized_to_df(self, normalized_json, endpoint_simple):
        t = Transformer(endpoint_simple.mappings.aliases, endpoint_simple.exclude)
        expected = [
            "id",
            "well_name",
            "well_alias",
            "well_type",
            "is_active",
            "latest_production_time",
            "iwell_created_at",
            "iwell_updated_at",
        ]

        assert t.transform(normalized_json).columns.tolist() == expected

    # def test_transform_nested_to_df(self, nested_json, endpoint_simple):
    #     t = Transformer(endpoint_simple.mappings.aliases, endpoint_simple.exclude)
    #     expected = [
    #         "id",
    #         "well_name",
    #         "well_alias",
    #         "well_type",
    #         "is_active",
    #         "latest_production_time",
    #         "iwell_created_at",
    #         "iwell_updated_at",
    #     ]

    #     assert t.transform(nested_json).columns.tolist() == expected

