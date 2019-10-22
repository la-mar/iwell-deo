from __future__ import annotations
from typing import Dict, List, Union
import logging

from celery import Celery
from celery.schedules import crontab

from iwell import create_app
import collector.endpoint
import os

from config import get_active_config
from collector.tasks import log, count_wells, sync_endpoint
from api.models import Well

logger = logging.getLogger(__name__)

conf = get_active_config()


def create_celery(app):
    celery = Celery(
        app.import_name,
        # backend=app.config["CELERY_RESULT_DBURI"],  # CELERY_RESULT_BACKEND
        broker=app.config["BROKER_URL"],
        include=app.config["CELERY_TASK_LIST"],
        result_extended=True,
    )
    celery.conf.update(app.config)
    # celery.conf.update({"result_extended": True})
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


flask_app = create_app()
celery = create_celery(flask_app)


class Task:
    """ A yaml defined task object to be passed to Celery """

    def __init__(
        self,
        model_name: str,
        task_name: str,
        cron: dict = None,
        seconds: int = None,
        mode: str = None,
        **kwargs,
    ):
        self.model_name = model_name
        self.task_name = task_name
        self.cron = self.parse_cron(cron or {})
        self.seconds = seconds
        self.mode = mode

        if not any([self.cron, self.seconds]):
            raise ValueError("Either seconds or cron must be specified")

    def __repr__(self):
        sch = (
            f"{self.schedule}" if self.seconds is None else f"({self.schedule} seconds)"
        )
        return f"Task: {self.qualified_name} {sch}"

    @property
    def qualified_name(self):
        return f"{self.model_name}/{self.task_name}"

    @property
    def schedule(self):
        """ The scheduling expression to be used for task creation. Prefers seconds over cron expressions. """
        return self.seconds or self.cron

    @staticmethod
    def parse_cron(cron: dict):
        """ Return a crontab object if the passed dict has any non-null values """
        notnull = {k: v for k, v in cron.items() if v is not None}
        if len(notnull) > 0:
            return crontab(**notnull)
        else:
            return None


def tasks_from_app_config(conf: object):
    """ Retrieves collection task definitions from the active configuration and parses
    them into Task objects """
    for_scheduling: List[Task] = []
    endpoints = collector.endpoint.load_from_config(conf)
    for model_name in conf.endpoints.keys():  # type: ignore
        tasks = conf.endpoints.get(model_name).get("tasks", {})  # type: ignore
        for task_name, task_def in tasks.items():
            try:
                for_scheduling.append(Task(model_name, task_name, **task_def))
            except ValueError as ve:
                logger.error(
                    f"Failed to create scheduled task ({model_name}/{task_name}) -- {ve}"
                )

    return for_scheduling


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """ Schedules a periodic task for each configured collection task """
    tasks = tasks_from_app_config(conf)

    for task in tasks:
        sender.add_periodic_task(
            task.schedule,
            sync_endpoint.s(task.model_name, mode=task.mode),
            name=task.qualified_name,
        )


if __name__ == "__main__":
    endpoints = collector.endpoint.load_from_config(conf)
    ep = endpoints["tank_readings"]
    model = ep.model

    dir(model)
    dir(model.__table__.foreign_keys)

    fks = list(model.__table__.foreign_keys)
    fk = fks[1]

    dir(fk)
    fk.target_fullname
    dir(fk.column)
    fk.column

