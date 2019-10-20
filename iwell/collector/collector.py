from __future__ import annotations
from typing import Dict, List, Union, Any
import logging

import pandas as pd
from flask_sqlalchemy import Model
import requests


from api.models import *
from collector.endpoint import Endpoint
from collector.request import Request
from collector.transformer import Transformer
from config import get_active_config
from collector.util import retry

logger = logging.getLogger(__name__)

config = get_active_config()


class Collector(object):
    """ Acts as the conduit for transferring newly collected data into a backend data model """

    _tf = None
    _endpoint = None
    _functions = None
    _model = None

    def __init__(
        self,
        endpoint: Endpoint,
        functions: Dict[Union[str, None], Union[str, None]] = None,
    ):
        self.endpoint = endpoint
        self._functions = functions

    @property
    def functions(self):
        if self._functions is None:
            self._functions = config.functions
        return self._functions

    @property
    def model(self):
        if self._model is None:
            self._model = self.endpoint.model
        return self._model

    @property
    def tf(self):
        if self._tf is None:
            self._tf = Transformer(
                aliases=self.endpoint.mappings.get("aliases", {}),
                exclude=self.endpoint.exclude,
                date_columns=self.model.date_columns,
            )
        return self._tf

    def transform(self, data: dict) -> pd.DataFrame:
        return self.tf.transform(data)


class IWellCollector(Collector):
    def strip_ids_from_headers(self, headers: Dict[Any, str]) -> Dict[str, str]:
        # get any identifiers in request headers
        prefix_header = str(headers.get(config.API_HEADER_KEY))
        keys = {
            k.replace(prefix_header, ""): v
            for k, v in headers.items()
            if k.startswith(prefix_header)
        }
        return keys

    def collect(self, response: requests.Response) -> None:
        data = response.json()["data"]
        logger.info(f"{self.endpoint}: downloaded {len(data)} records")
        df = self.transform(data)
        # add ids from headers as columns to dataframe
        ids = self.strip_ids_from_headers(response.request.headers)  # type: ignore
        for key, value in ids.items():
            df[key] = int(value)

        if not df.empty:
            return self.model.bulk_merge(df)
        else:
            logger.info(f"{self.endpoint}: empty dataframe")


class CollectionLogger(object):
    """ Logs the completion status of collection tasks in the database"""

    def __init__(self, model: Model, result: Dict[str, Union[str, int, float, bool]]):
        pass


if __name__ == "__main__":
    from iwell import create_app, db
    from api.models import *
    from collector.requestor import Requestor
    from collector.endpoint import load_from_config
    import requests

    app = create_app()
    app.app_context().push()

    config = get_active_config()
    endpoints = load_from_config(config)
    endpoint = endpoints["fields"]

    c = IWellCollector(endpoint)
    c.model

    requestor = Requestor(config.API_BASE_URL, endpoint, functions={})

    r2 = requests.get(
        requestor.url, headers={"Authorization": requestor.get_token()}, params={}
    )
    data = r2.json()["data"]
    c.collect(r2)

