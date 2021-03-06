from __future__ import annotations
from typing import Dict, List, Union, Any
import logging
import datetime as dt
from pydoc import locate

from attrdict import AttrDict
from flask_sqlalchemy import Model
from sqlalchemy import Column

from api.models import *
from config import get_active_config

logger = logging.getLogger(__name__)

conf = get_active_config()


class Endpoint(object):
    since_offset = {"minutes": conf.API_DEFAULT_SYNC_WINDOW_MINUTES}
    start_offset = {"days": conf.API_DEFAULT_SYNC_START_OFFSET_DAYS}
    mode = "sync"

    def __init__(
        self,
        name: str,
        model: str,
        version: str = None,
        path: str = None,
        mappings: Dict[str, str] = None,
        url_params: List[str] = None,
        exclude: List[str] = None,
        depends_on: Dict[str, str] = None,
        options: List[str] = None,
        normalize: bool = False,
        updated_column: str = "updated_at",
        enabled: bool = True,
        mode: str = None,
        since_offset: Dict = None,
        start_offset: Dict = None,
        **kwargs,
    ):

        self.name = name
        self.version = version
        self.path = path
        self.mappings = AttrDict(mappings or {})
        self.model_name = model
        self._model = None
        self.updated_column = updated_column
        self.url_params = url_params
        self.exclude = exclude or []
        self._dependency_map = depends_on or {}
        self._depends_on: Union[Dict[str, Model], None] = None
        self.normalize = normalize
        self.options = options or []
        self.enabled = enabled
        self.since_offset = dt.timedelta(**(since_offset or self.since_offset))  # type: ignore
        self.mode = mode or self.mode
        self.start_offset = dt.timedelta(**(start_offset or self.start_offset))  # type: ignore

    def __repr__(self):
        return f"{self.version}{self.path}"

    def __iter__(self):
        attrs = [x for x in dir(self) if not x.startswith("_")]
        for a in attrs:
            yield a, getattr(self, a)

    @property
    def model(self) -> Model:
        if self._model is None:
            self._model = self.locate_model(self.model_name)
        return self._model

    @property
    def depends_on(self) -> Dict[str, Column]:
        if self._depends_on is None:
            self._depends_on = self.link_upstream_columns()
        return self._depends_on

    def link_upstream_columns(self) -> Dict[str, Column]:
        linked_columns: Dict[Any, Any] = {}
        for key_field, model_name in self._dependency_map.items():
            model_name, column_name = model_name.rsplit(".", maxsplit=1)
            columns = list(self.locate_model(model_name).__table__.columns)
            column_map = {c.name: c for c in columns}
            if linked_columns.get(key_field) is None:
                linked_columns[key_field] = column_map[column_name]
            else:
                linked_columns[key_field] += column_map[column_name]
        return linked_columns

    def locate_model(self, model_name: str) -> Model:
        model: Model = None
        try:
            # try to import dotted model name. ex: api.models.MyModel
            model = locate(model_name)
            logger.debug(f"Found model: {model_name}")
        except ModuleNotFoundError:
            logger.debug(
                f"Failed to import module '{model_name}' from project directory"
            )
            try:
                # try to import model from global namespace
                model = globals()[model_name]
                logger.debug(f"Model '{model_name}' found in global namespace")
            except ModuleNotFoundError:
                raise ModuleNotFoundError(
                    f"No module named '{model_name}' found in project or global namespace"
                )
        except Exception as e:
            raise Exception(f"Unable to locate module {model_name} -- {e}")

        return model


def load_from_config(
    app_config: object, load_disabled: bool = False
) -> Dict[str, Endpoint]:
    endpoints: dict = {}
    try:
        endpoints = app_config.endpoints  # type: ignore
    except AttributeError:
        logger.debug("config object has no attribute 'endpoints'")

    loaded: Dict[str, Endpoint] = {}
    for ep in endpoints.items():
        try:
            new = Endpoint(name=ep[0], **ep[1])
            if new.enabled:
                loaded[ep[0]] = new
        except Exception as e:
            logger.error(f"Failed to create endpoint ({ep[0]}) -> {e}")

    return loaded


if __name__ == "__main__":

    from config import get_active_config

    config = get_active_config()
    endpoints = config.endpoints
    # [x for x in endpoints.items()]
    # endpoints = load_from_config(config)

    # e = Endpoint("test", **{"model": "test"})
    e = Endpoint(name="test", **endpoints.wells)
    e.depends_on
    e._dependency_map
    e.enabled
    e.timedelta
