# pylint: disable=arguments-differ, method-hidden

from typing import Any
import json
from datetime import datetime, date, timedelta


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        # let base class raise the type error
        return super().default(obj)


class ObjectEncoder(json.JSONEncoder):
    """Class to convert an object into JSON."""

    def default(self, obj: Any):
        """Convert `obj` to JSON."""
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            return obj.__class__.__name__
        elif isinstance(obj, timedelta):
            return obj.__str__()
        else:
            # generic, captures all python classes irrespective.
            cls = type(obj)
            result = {
                "__custom__": True,
                "__module__": cls.__module__,
                "__name__": cls.__name__,
            }
            return result


if __name__ == "__main__":

    data = """[{
            "id": 16677,
            "name": "test well 1",
            "alias": "test well 1",
            "type": "OIL",
            "is_active": true,
            "latest_production_time": 1525123811,
            "created_at": 1525123811,
            "updated_at": 1525123811
        },
        {
            "id": 16681,
            "name": "test well 2",
            "alias": "test well 2",
            "type": "OIL",
            "is_active": true,
            "latest_production_time": 1525123811,
            "created_at": 1525123811,
            "updated_at": 1525123811
        },
        {
            "id": 16682,
            "name": "test well 3",
            "alias": "test well 3",
            "type": "OIL",
            "is_active": true,
            "latest_production_time": 1525123811,
            "created_at": 1525123811,
            "updated_at": 1525123811
        },
        {
            "id": 16768,
            "name": "test well 4",
            "alias": "test well 4",
            "type": "OIL",
            "is_active": false,
            "latest_production_time": 1525123811,
            "created_at": 1525123811,
            "updated_at": 1525123811
        }
    ]"""

    data = {"key": datetime.utcfromtimestamp(0), "key2": "test_string"}
    js = json.dumps(data, cls=DateTimeEncoder)
    js

    d = DateTimeEncoder()
    d.encode({"test": "test"})
    d.default(datetime.now())

    class ObjectForEncoding:
        key = "value"

        def to_json(self):
            return json.dumps({"key": self.key})

    data = {"test_obj": ObjectForEncoding()}

    from datetime import timedelta

    data = {"test_obj": timedelta(hours=1).__str__()}

    encoded = json.dumps(data, cls=ObjectEncoder)
