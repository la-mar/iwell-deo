# import re
# from datetime import datetime

import pandas as pd
import pytest
from hypothesis import example, given

# from hypothesis.extra.pytz import timezones
from hypothesis.strategies import datetimes, none

from iwell.collector.transformer import Transformer

# variant_datetimes = datetimes(timezones=("UTC", "US\Central", none()))
variant_datetimes = datetimes()


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

    # @given(variant_datetimes)
    def test_date_handler_handles_formats(self, endpoint_simple):
        fmts = [
            "2019-01-01",
            "2019-01-01 12:12:12 AM",
            "2019-01-01 12:12:12 PM",
            "2019-01-01 22:12:12",
            "2019-01-01 22:22",
            "2019-01-01 6:00",
        ]
        t = Transformer(endpoint_simple.mappings.aliases, endpoint_simple.exclude)
        for f in fmts:
            assert isinstance(t.date_handler(f), pd.Timestamp)
