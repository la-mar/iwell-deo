from __future__ import annotations
from typing import Dict, List, Union, Generator, Optional
import logging
from datetime import datetime, timedelta, date

from attrdict import AttrDict
import pandas as pd
import requests
from oauthlib.oauth2 import LegacyApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session
import util

from config import get_active_config
from collector.token_manager import TokenManager
from collector.request import Request
from collector.endpoint import Endpoint

logger = logging.getLogger(__name__)
conf = get_active_config()


class Requestor(object):
    window_timedelta = timedelta(days=30)
    sync_epoch = datetime(year=1970, month=1, day=1)
    functions: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, str]] = None

    def __init__(
        self,
        base_url: str,
        endpoint: Endpoint,
        functions: dict = None,
        headers: dict = None,
        params: dict = None,
    ):
        self.token_manager = TokenManager.from_app_config(conf)
        self.headers = headers or {}
        self.params = params or {}
        self.base_url = base_url
        self.endpoint = endpoint
        self.functions = functions or {}
        self._session = None
        self.requests: list = []
        self.responses: list = []

    def __repr__(self):
        return f"({self.endpoint.name})  {self.url} -> {self.model}"

    def __iter__(self) -> Generator:
        for r in self.requests:
            yield r

    @property
    def url(self):
        return util.urljoin(self.base_url, self.path)

    @property
    def path(self):
        return self.endpoint.path

    @property
    def model(self):
        """ Making requests on behalf of this model """
        return self.endpoint.model

    @property
    def session(self):
        if self._session is None:
            self.session = requests.Session()
        return self._session

    @property
    def s(self):
        """ Alias for session """
        return self.session

    @session.setter  # type: ignore
    def session(self, value):
        self._session = value

    def get_token(self, force_refresh=False):
        return self.token_manager.get_token(force_refresh=force_refresh)

    def get_function(
        self,
        func_name: str,
        value: Union[int, str, float] = None,
        value2: Union[int, str, float] = None,
        values: list = None,
    ) -> str:
        """Create a url fragment using the specified function

        Arguments:
            name {str} -- parameter name
            value {str} -- parameter value
            value2 {str} -- parameter value
            values {list} -- parameter value

        Returns:
            self
        """
        try:
            if not any([value, values]):
                raise ValueError

            if values:
                values = ",".join([str(x) for x in values])  # type: ignore
            result = self.functions[func_name]["template"].format(  # type: ignore
                value=value, value2=value2, values=values
            )
            logger.debug(result)
            return result
        except KeyError:
            raise KeyError(f"Function not found: {func_name}")

        except ValueError:
            raise ValueError("One of value or values must be specified")

        except Exception as e:
            raise Exception(f"Failed to add function: {func_name} -- {e}")

    def add_param(self, field: str, value: Union[int, str, float] = None) -> Requestor:
        #! https://flask-restless.readthedocs.io/en/stable/searchformat.html
        try:
            self.params[field] = str(value)

        except Exception as e:
            raise Exception(
                f"Failed to add parameter: field={field} value={value} -- {e}"
            )

        return self

    def format(self, **kwargs) -> str:
        try:
            return self.url.format(**kwargs)
        except KeyError as ke:
            raise KeyError(f"Unable to format path ({self.path}) without {ke}")

    def enqueue(self, headers: dict = None, params: dict = None, **kwargs) -> None:
        url = self.format(**kwargs)
        headers = headers or {}
        params = params or {}
        headers = {**self.headers, **headers}
        params = {**self.params, **params}

        r = Request("GET", url, headers=headers, params=params)
        self.requests.append(r)
        logger.debug(f"Queued request: {r}")
        return r

    def get_all(self) -> Generator:
        for r in self:
            logger.info(f"Sending request: {r}")
            yield r.get()


class IWellRequestor(Requestor):
    custom_header_key = conf.API_HEADER_KEY
    custom_header_prefix = conf.API_HEADER_PREFIX

    def __init__(
        self,
        base_url: str,
        endpoint: dict,
        mode: str = "sync",
        since: datetime = None,
        start: datetime = None,
        end: datetime = None,
        **kwargs,
    ):
        super().__init__(base_url, endpoint, **kwargs)
        self.mode = mode
        self.configure_mode()
        self.add_auth()
        if since:
            self.add_since(since)
        if start:
            self.add_start(start)
        if end:
            self.add_end(end)
        self.headers.update({self.custom_header_key: self.custom_header_prefix})

    def configure_mode(self):

        if self.mode == "full":
            self.add_start(datetime(year=1970, month=1, day=1))
        elif self.mode == "sync":
            query = self.determine_query_window()
            self.add_since(query.get("since"))
            self.add_start(query.get("start"))

    def add_since(self, since: datetime, **kwargs) -> None:
        """Limits records to those updated after the specified time"""
        if "since" in self.endpoint.options:
            ts = since.timestamp()
            self.add_param("since", ts)

    def add_start(self, start: datetime, **kwargs) -> None:
        """Filters records based on their recording date (e.g when the reading occurred), NOT when the record was changed in the system"""
        if "start" in self.endpoint.options:
            self.add_param("start", start.strftime("%Y-%m-%d"))

    def add_end(self, end: datetime, **kwargs) -> None:
        if "end" in self.endpoint.options:
            self.add_param("end", end.strftime("%Y-%m-%d"))

    def add_auth(self) -> None:
        self.headers.update({"Authorization": self.get_token(force_refresh=True)})

    def enqueue(self, headers: dict = None, params: dict = None, **kwargs) -> None:
        return super().enqueue(headers, params, **kwargs)

    def get_dependency_ids(
        self, since: datetime = None, updated_column_name: str = "updated_at"
    ) -> list:
        # TODO: function needs to be reworked and parameter agnostic
        ids: list = []
        grouped: dict = {}

        # group columns with the same external table name
        for key_field, column in self.endpoint.depends_on.items():
            if grouped.get(column.table.name) is None:
                grouped[column.table.name] = [(key_field, column)]
            else:
                grouped[column.table.name].append((key_field, column))

        # get ids from external tables
        for table_name, mappings in grouped.items():
            # separate aliases and column objects
            aliases = [m[0] for m in mappings]
            columns = [m[1] for m in mappings]

            # query the column values and label the returned columns
            query = self.model.query.with_entities(
                *[c.label(aliases[idx]) for idx, c in enumerate(columns)]
            )
            # if since:
            #     # hack to get query access to the model via the first column in the columns set
            #     query.filter(columns[0].table.c[updated_column_name] >= since)

            df = pd.read_sql(query.statement, query.session.bind)
            records = df.to_dict(orient="records")
            ids += records
        return ids

    @property
    def last_sync(self):
        pass

    def determine_query_window(self) -> dict:
        # TODO: Implement end bound
        since = None
        start = None
        if self.mode in ["delta", "sync"]:
            since = datetime.now() - (
                self.endpoint.since_offset or self.window_timedelta
            )
            start = datetime.now() - (
                self.endpoint.start_offset or self.window_timedelta
            )
        elif self.mode == "full":
            since = self.sync_epoch
            start = self.sync_epoch

        return {"since": since, "start": start, "end": None}

    def enqueue_with_ids(self, headers: dict = None, params: dict = None, **kwargs):
        """adds id vars as headers to the outgoing request so they can be retrieved from the response at collection time """
        id_headers = {
            f"{self.custom_header_prefix}-{k}": str(v) for k, v in kwargs.items()
        }
        headers = headers or {}
        return self.enqueue(headers={**headers, **id_headers}, params=params, **kwargs)

    def sync_model(self) -> Generator:
        logger.info(f"Syncing model: {self}")
        ids: list = []
        since = self.determine_query_window().get("since")

        if len(self.endpoint.depends_on) > 0:
            dep_ids = self.get_dependency_ids(since)

            for kwargs in dep_ids:
                self.enqueue_with_ids(**kwargs)
        else:
            self.enqueue()

        while len(self.requests) > 0:
            yield self.requests.pop()

        logger.info(f"Model sync complete: {self}")


if __name__ == "__main__":
    from iwell import create_app, db

    from collector.endpoint import load_from_config
    from config import get_active_config
    from collector.collector import Collector, IWellCollector

    logging.basicConfig()
    logger.setLevel(10)

    app = create_app()
    app.app_context().push()

    conf = get_active_config()
    endpoints = load_from_config(conf)
    functions = conf.functions
    url = conf.API_BASE_URL

    # dt = datetime(year=1970, month=1, day=1)
    # ts = int(dt.timestamp())

    endpoint = endpoints["tank_readings"]
    endpoint.timedelta = timedelta(hours=24)
    endpoint.start_offset = timedelta(days=1)
    # endpoint.mode
    r = IWellRequestor(url, endpoint, mode="sync")
    c = IWellCollector(endpoint)

    # req = r.enqueue_with_ids(well_id=20338, field_id=3051)  # field_values
    req = r.enqueue_with_ids(tank_id=17928)  # tank_readings
    # req.params.update(
    #     {"start": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")}
    # )
    # req.params["since"] = int(float(req.params["since"]))
    req.params
    resp = req.get()

    df = c.transform(resp.json()["data"])
    df
    df.shape
    df.reading_at.min()

    # df.to_dict(orient="records")
    # c.collect(resp)

    # responses = []
    # for req in r.sync_model():
    #     # req.params.update(
    #     #     {"start": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")}
    #     # )
    #     # req.params["since"] = int(float(req.params["since"]))
    #     responses.append(req.get())

    # # for resp in responses:
    # #     c.collect(resp)

    # df = pd.DataFrame()
    # for resp in responses:
    #     df = df.append(c.transform(resp.json()["data"]))

    # df

    # df.shape
    # ts = responses[0].request.path_url.split("=")[-1]
    # pd.Timestamp(datetime.utcnow()) - endpoint.timedelta < df.iwell_updated_at.min()
    # pd.Timestamp(datetime.utcnow()) - df.iwell_updated_at.min()
