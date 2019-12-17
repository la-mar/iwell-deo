import pytest  # noqa
import re
from datetime import datetime

from attrdict import AttrDict

from collector.collector import Collector
from collector.endpoint import Endpoint

from config import TestingConfig

conf = TestingConfig()
# endpoints = config.endpoints
# functions = config.functions

from celery_queue.worker import Task, tasks_from_app_config
from celery.schedules import crontab


class TestTask:
    def test_create_task_with_seconds(self):
        Task("wells", "test_task", seconds=60)

    def test_create_task_with_cron(self):
        cron = dict(minute="*/1")
        t = Task("wells", "test_task", cron=cron)
        assert t.cron == crontab(minute="*/1")

    def test_overlapping_definition(self):
        cron = dict(minute="*/1")
        t = Task("wells", "test_task", seconds=60, cron=cron)
        assert t.schedule == 60


# tasks_from_app_config(conf)
