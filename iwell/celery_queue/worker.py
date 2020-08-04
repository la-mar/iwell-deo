from __future__ import annotations

import logging
import os
from typing import List, Union

from celery import Celery
from celery.schedules import crontab
from celery.signals import after_setup_logger  # after_setup_task_logger

from celery_queue.task import Task
import loggers
import collector.endpoint
from collector.tasks import post_heartbeat, sync_endpoint, sync_production
from config import get_active_config
from iwell import create_app

logger = logging.getLogger(__name__)

conf = get_active_config()


def create_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["BROKER_URL"],
        include=app.config["CELERY_TASK_LIST"],
    )
    celery.conf.update(app.config)
    # celery.conf.update({"worker_max_memory_per_child": True})
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


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """ Schedules a periodic task for each configured collection task """
    tasks = Task.from_config(conf)
    for task in tasks:
        if task.enabled:
            logger.debug("Registering periodic task: %s", task.task_name)
            sender.add_periodic_task(
                task.schedule,
                sync_endpoint.s(task.model_name, mode=task.mode, **task.options),
                name=task.qualified_name,
            )

        else:
            logger.warning("Task %s is DISABLED -- skipping", task.task_name)

    sender.add_periodic_task(
        60, post_heartbeat.s(), name="heartbeat",
    )

    sender.add_periodic_task(
        900, sync_production.s(), name="heartbeat",
    )


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):  # pylint: disable=unused-argument
    loggers.config(logger=logger)
