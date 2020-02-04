from typing import Tuple, List, Dict, Union
import logging
from datetime import datetime
import pytz

from flask_restful import Resource
from flask import request, jsonify
from sqlalchemy import func
import humanize


import collector.tasks
from celery_queue.task import Task
from config import get_active_config
from collector.endpoint import load_from_config
import pandas as pd

__all__ = ["DescribeEndpoint", "DescribeEndpoints", "ListResources"]

logger = logging.getLogger(__name__)

conf = get_active_config()

endpoints = load_from_config(conf)
tasks = Task.from_config(conf)

sync_tasks = {x.model_name: x for x in tasks if x.mode == "sync"}
full_tasks = {x.model_name: x for x in tasks if x.mode == "full"}

UTC = pytz.timezone("UTC")


def desribe_task(task: Task, updated_at: datetime = None) -> Dict:

    summary = {}
    summary["schedule"] = task.hf_schedule
    if updated_at:
        remaining = task.remaining(updated_at)
        summary["remaining"] = str(remaining).split(".")[0]
        summary["remaining_seconds"] = remaining.total_seconds()
        summary["remaining_friendly"] = task.hf_remaining(updated_at)
        summary["is_overdue"] = remaining.total_seconds() < 0

    return summary


class ListEndpoints(Resource):
    def get(self):
        result = list(endpoints.keys())
        return jsonify(result)


def describe_endpoint(endpoint: str):
    summary: Dict[str, Union[str, Dict]] = {}
    ep = endpoints[endpoint]
    updated_at = ep.model.s.query(
        func.max(ep.model.updated_at).label("updated_at")
    ).one()[0]

    updated_at = UTC.normalize(updated_at)

    # ts = pd.Timestamp(updated_at).tz_convert(conf.API_TIMEZONE)
    summary["name"] = endpoint
    summary["updated_at"] = conf.API_TIMEZONE.normalize(updated_at).isoformat()

    sync_task = sync_tasks.get(endpoint)
    full_task = full_tasks.get(endpoint)

    if sync_task:
        summary["sync"] = desribe_task(sync_task, updated_at)

    if full_task:
        summary["full"] = desribe_task(full_task, updated_at)

    # summary["sync_schedule"] =
    # summary["full_schedule"] =

    # summary["seconds_until_next_run"]

    return summary


class DescribeEndpoint(Resource):
    def get(self, endpoint: str):
        return jsonify(describe_endpoint(endpoint))


class DescribeEndpoints(Resource):
    def get(self):
        result = []
        for name in endpoints.keys():
            result.append(describe_endpoint(name))
        return jsonify(result)


class ListResources(Resource):
    def get(self):
        return jsonify([str(x) for x in app.url_map.iter_rules()])


if __name__ == "__main__":
    from iwell import create_app, db

    # from cron_descriptor import get_description, ExpressionDescriptor

    logging.basicConfig()
    logger.setLevel(10)

    app = create_app()
    app.app_context().push()
    endpoint = "wells"

    ep = endpoints[endpoint]
    task = sync_tasks[endpoint]

    describe_endpoint(endpoint)
