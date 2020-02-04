from __future__ import annotations
from typing import List
import logging
from datetime import timedelta, datetime
import pytz

from celery.schedules import crontab
from cron_descriptor import get_description, ExpressionDescriptor
import humanize

import collector.endpoint
from config import get_active_config


logger = logging.getLogger(__name__)

conf = get_active_config()

UTC = pytz.timezone("UTC")


class Task:
    """ A yaml defined task object to be passed to Celery """

    mode = "sync"

    def __init__(
        self,
        model_name: str,
        task_name: str,
        cron: dict = None,
        seconds: int = None,
        mode: str = None,
        options: dict = None,
        enabled: bool = True,
        **kwargs,
    ):
        self.model_name = model_name
        self.task_name = task_name
        self.cron = self.parse_cron(cron or {})
        self.seconds = seconds
        self.mode = mode or self.mode
        self.options = options or {}
        self.enabled = enabled

        if not any([self.cron, self.seconds]):
            raise ValueError("Either seconds or cron must be specified")

    def __repr__(self):
        status = "***DISABLED***" if not self.enabled else ""
        sch = self.schedule_as_string
        opts = ", ".join([f"{k}:{v}" for k, v in self.options.items()])
        return f"{status} {self.qualified_name} {sch} {opts}"

    @property
    def schedule_as_string(self):
        s = self.schedule
        sch = (
            f"{s._orig_minute} {s._orig_hour} {s._orig_day_of_week} {s._orig_day_of_month} {s._orig_month_of_year}"
            if self.seconds is None
            else f"{self.schedule} seconds"
        )
        return sch

    @property
    def hf_schedule(self) -> str:
        sch = self.schedule_as_string
        if "seconds" in sch and self.seconds:
            result = f"Every {self.seconds // 60} minutes"
        else:
            result = get_description(sch)

        result = result.replace("00:00 AM", "midnight")
        return result

    def remaining(self, updated_at: datetime) -> timedelta:
        utcnow = UTC.localize(datetime.utcnow())
        if updated_at.tzinfo is not None:
            updated_at = UTC.normalize(updated_at)
        else:
            updated_at = UTC.localize(updated_at)
            updated_at = UTC.normalize(updated_at)

        if isinstance(self.schedule, int):
            delta = (updated_at + timedelta(seconds=self.seconds or 0)) - utcnow
        else:
            delta = self.cron.remaining_estimate(updated_at)

        return delta

    def hf_remaining(self, updated_at: datetime) -> str:
        return humanize.naturaldelta(self.remaining(updated_at))

    @property
    def qualified_name(self):
        return f"{self.model_name}/{self.task_name}"

    @property
    def schedule(self):
        """ The scheduling expression to be used for task creation. Prefers seconds over cron expressions. """
        return self.seconds or self.cron

    @staticmethod
    def parse_cron(cron: dict) -> crontab:
        """ Return a crontab object if the passed dict has any non-null values """
        notnull = {k: v for k, v in cron.items() if v is not None}
        if len(notnull) > 0:
            return crontab(**notnull)
        else:
            return None

    @classmethod
    def from_config(cls, conf: object) -> List[Task]:
        """ Retrieves collection task definitions from the active configuration and parses
        them into Task objects """
        for_scheduling: List[Task] = []
        endpoints = collector.endpoint.load_from_config(conf, load_disabled=False)
        for model_name, _ in endpoints.items():  # type: ignore
            tasks = conf.endpoints.get(model_name).get("tasks", {})  # type: ignore
            for task_name, task_def in tasks.items():
                try:
                    new = Task(model_name, task_name, **task_def)
                    for_scheduling.append(new)
                except ValueError as ve:
                    logger.error(
                        f"Failed to create scheduled task ({model_name}/{task_name}) -- {ve}"
                    )

        return for_scheduling
