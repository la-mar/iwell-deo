from typing import Tuple
import logging

import boto3
from flask_restful import Resource
from flask import request

import collector.tasks
from config import get_active_config
from collector.endpoint import load_from_config
import util.sqs

__all__ = ["RunJob", "JobCount"]


logger = logging.getLogger(__name__)

conf = get_active_config()


class RunJob(Resource):
    def post(self, endpoint: str):
        mode = request.args.get("mode")
        if not mode and request.json:
            mode = request.json.get("mode", "sync")
        if not mode:
            mode = "sync"

        kwargs = {}
        if mode:
            kwargs.update(dict(mode=mode))

        if endpoint != "all":
            async_result = collector.tasks.sync_endpoint.delay(endpoint, **kwargs)
        else:
            for name in load_from_config(conf).keys():
                collector.tasks.sync_endpoint(name, **kwargs)

        logger.warning(f"Submitted job {endpoint} mode={mode}")

        return (
            {"status": "success", "job_id": async_result.id, "mode": mode},
            200,
        )


class JobCount(Resource):
    def get(self):

        queue_name = conf.CELERY_DEFAULT_QUEUE
        message_count = util.sqs.get_message_count(queue_name)

        return {"queue": queue_name, "count": message_count}
