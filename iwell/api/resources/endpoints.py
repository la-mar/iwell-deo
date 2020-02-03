from typing import Tuple
import logging

from flask_restful import Resource
from flask import request, jsonify
from sqlalchemy import func

import collector.tasks
from config import get_active_config
from collector.endpoint import load_from_config


logger = logging.getLogger(__name__)

conf = get_active_config()

endpoints = load_from_config(conf)


class ListEndpoints(Resource):
    def get(self):
        result = list(endpoints.keys())
        return jsonify(result)


def describe_endpoint(endpoint: str):
    result = {}
    summary = {}
    ep = endpoints[endpoint]
    summary["updated_at"] = ep.model.s.query(
        func.max(ep.model.updated_at).label("update_at")
    ).one()[0]

    result[endpoint] = summary
    return result


class DescribeEndpoint(Resource):
    def get(self, endpoint: str):
        return jsonify(describe_endpoint(endpoint))


class DescribeEndpoints(Resource):
    def get(self):
        result = {}
        for name in endpoints.keys():
            result.update(describe_endpoint(name))
        return jsonify(result)

