from __future__ import annotations
from typing import List, Dict, Tuple
import random
import time
from datetime import datetime, timedelta

from celery.signals import task_postrun, setup_logging
from celery.utils.log import get_task_logger
from flask_sqlalchemy import Model
import numpy as np


# it is important that this celery instance is t`he same as the primary flask app and NOT a new instance from celery_worker.py
from iwell import celery, db, create_app
from api.models import *
from collector.collector import IWellCollector
from collector.endpoint import load_from_config
from collector.requestor import IWellRequestor
from collector.request import Request
from collector.endpoint import Endpoint
from config import get_active_config, project
from celery_queue.task import Task
import metrics

conf = get_active_config()
endpoints = load_from_config(conf)


logger = get_task_logger(__name__)


def log_transform(
    x: float, vs: float = 1, hs: float = 1, ht: float = 0, vt: float = 0, mod: float = 1
) -> float:
    """ Default parameters yield the untransformed natural log curve.

        f(x) = (vs * ln(hs * (x - ht)) + vt) + (x/mod)

        vs = vertical stretch or compress
        hs = horizontal stretch or compress
        ht = horizontal translation
        vt = vertical translation
        mod = modulate growth of curve W.R.T x

     """

    return np.round((vs * np.log(hs * (x + ht)) + vt) + (x / mod), 2)


def spread_countdown(x: float, vs: float = None, hs: float = None) -> float:
    return log_transform(x=x, vs=vs or 25, hs=hs or 0.25, ht=4, vt=0, mod=4)


@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ["Starting up", "Booting", "Repairing", "Loading", "Checking"]
    adjective = ["master", "radiant", "silent", "harmonic", "fast"]
    noun = ["solar array", "particle reshaper", "cosmic ray", "orbiter", "bit"]
    message = ""
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = "{0} {1} {2}...".format(
                random.choice(verb), random.choice(adjective), random.choice(noun)
            )
        self.update_state(
            state="PROGRESS", meta={"current": i, "total": total, "status": message}
        )
        time.sleep(1)
    return {"current": 100, "total": 100, "status": "Task completed!", "result": 42}


@celery.task
def log(message):
    """Print some log messages"""
    logger.debug(message)
    logger.info(message)
    logger.warning(message)
    logger.error(message)
    logger.critical(message)


@celery.task
def post_heartbeat():
    """ Sync model from source to data warehouse"""
    return metrics.post(name=f"{project}.heartbeat", points=1)


@celery.task(bind=True, max_retries=2, ignore_result=True)
def collect_request(self, request: Request, endpoint: Endpoint):
    try:
        return _collect_request(request, endpoint)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


def _collect_request(request: Request, endpoint: Endpoint):
    c = IWellCollector(endpoint)
    logger.info(f"Collecting {request}")
    response = request.get()
    # logger.warning(response)
    if not response.ok:
        if response.status_code == 404:
            logger.warning(f"{request}: Resource not found")
        else:
            raise Exception(
                f"GET {response.url} returned unexpected response code: {response.status_code}"
            )
    result = c.collect(response)
    affected = result.get("affected")
    operation = result.get("operation")
    if affected:
        metrics.post(
            name="model_activity",
            points=affected,
            tags={"model": endpoint.model.__table__.name, "operation": operation},
        )
    return result


@celery.task(bind=True, ignore_result=True)
def sync_production(self):
    endpoint = endpoints["production"]
    endpoint.since_offset = timedelta(days=30)
    endpoint.start_offset = timedelta(days=30)

    task = {t.qualified_name: t for t in Task.from_config(conf)}["production/sync"]
    r = IWellRequestor(conf.API_BASE_URL, endpoint, mode=task.mode, **task.options)

    logger.warning(f"syncing production: {req}")
    req = r.enqueue_with_ids(well_id=17417)  # dogwood
    _collect_request(req, endpoint)
    # for idx, req in enumerate(r.sync_model()):
    #     collect_request.apply_async((req, endpoint), countdown=30 * idx)


@celery.task(bind=True, rate_limit="100/s", ignore_result=True)
def sync_endpoint(self, endpoint_name: str, **kwargs):
    return _sync_endpoint(endpoint_name, celery=True, **kwargs)


def _sync_endpoint(endpoint_name: str, celery: bool = False, **kwargs):
    """ Sync model from source to data warehouse"""
    endpoint = endpoints[endpoint_name]
    requestor = IWellRequestor(conf.API_BASE_URL, endpoint, **kwargs)
    errors: List[str] = []
    if endpoint.enabled:
        for idx, req in enumerate(requestor.sync_model()):
            logger.debug(f"Sending request to {req}")
            try:
                if celery:
                    countdown = spread_countdown(idx, vs=200)
                    logger.info(
                        f"scheduling task: req={req} endpoint={endpoint} countdown={countdown}"  # noqa
                    )
                    result = collect_request.apply_async(
                        (req, endpoint), countdown=countdown
                    )
                else:
                    result = _collect_request(req, endpoint)

            except Exception as e:
                logger.warning(f"Unable to collect request: {req}")
                errors.append(f"{req}: {e}")

        if len(errors) > 0:
            err = "\n".join(errors)
            logger.error(
                f"Captured {len(errors)} errors when syncing endpoint: "
                + "\n"
                + f"{err}"
            )
    else:
        logger.info(f"{endpoint} is disabled. Skipping execution.")


def capture_result(endpoint: Endpoint, result: dict) -> None:
    logger.debug(f"capturing results: {endpoint}: {len(result.keys())}")
    if len(result.keys()) > 0:
        result.update(
            {
                "integrated_at": datetime.now(),
                "model_name": f"{endpoint.model.__module__}.{endpoint.model.__tablename__}",
            }
        )
        IntegrationLog.s.add(IntegrationLog(**result))  # type: ignore
        IntegrationLog.persist()  # type: ignore


# def post_metric(endpoint: Endpoint, result: dict) -> None:
#     for k, v in result.items():
#         try:
#             name = f"{project}.{endpoint.name}.{k}"
#             points = v
#             metrics.post(name, points)
#         except Exception as e:
#             logger.debug(
#                 "Failed to post metric: name=%s, points=%s, error=%s", name, points, e
#             )


@task_postrun.connect
def close_session(*args, **kwargs):
    # Flask SQLAlchemy will automatically create new sessions for you from
    # a scoped session factory, given that we are maintaining the same app
    # context, this ensures tasks have a fresh session (e.g. session errors
    # won't propagate across tasks)
    db.session.remove()


if __name__ == "__main__":
    import logging

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    endpoint_name = "field_values"
    app = create_app()
    app.app_context().push()
