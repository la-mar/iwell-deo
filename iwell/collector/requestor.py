from __future__ import annotations
from typing import Dict, List, Union, Generator
import logging
from datetime import datetime, timedelta
import urllib.parse

from attrdict import AttrDict
import pandas as pd
import requests
from oauthlib.oauth2 import LegacyApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session


from config import get_active_config
from collector.token_manager import TokenManager
from collector.request import Request
from collector.endpoint import Endpoint

logger = logging.getLogger(__name__)
config = get_active_config()


class Requestor(object):
    window_timedelta = timedelta(days=1)
    sync_epoch = datetime(year=1970, month=1, day=1)
    functions: Dict[str, str] = {}
    headers: Dict[str, str] = {}
    params: Dict[str, str] = {}

    def __init__(
        self,
        base_url: str,
        endpoint: Endpoint,
        functions: dict = None,
        headers: dict = None,
        params: dict = None,
    ):
        self.token_manager = TokenManager.from_app_config()
        self.headers = headers or self.headers
        self.params = params or self.params
        self.base_url = base_url
        self.endpoint = endpoint
        self.functions = functions or self.functions
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
        return self.urljoin(self.base_url, self.path)

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
                values = "".join(values)  # type: ignore

            return self.functions[func_name]["template"].format(  # type: ignore
                value=value, value2=value2, values=values
            )
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
            raise Exception(f"Failed to add parameter: field={field} value={value}")

        return self

    def format(self, **kwargs) -> str:
        try:
            return self.url.format(**kwargs)
        except KeyError as ke:
            raise KeyError(f"Unable to format path ({self.path}) without {ke}")
        except Exception:
            raise

    @staticmethod
    def urljoin(base: str, path: str) -> str:
        if not base.endswith("/"):
            base = base + "/"
        if path.startswith("/"):
            path = path[1:]
        return urllib.parse.urljoin(base, path)

    def enqueue(self, headers: dict = None, params: dict = None, **kwargs) -> None:
        url = self.format(**kwargs)
        headers = headers or {}
        params = params or {}
        headers = {**self.headers, **headers}
        params = {**self.params, **params}

        r = Request("GET", url, headers=headers, params=params)
        self.requests.append(r)
        logger.debug(f"Queued request: {r}")

    def get_all(self) -> Generator:
        for r in self:
            logger.info(f"Sending request: {r}")
            yield r.get()


class IWellRequestor(Requestor):
    custom_header_key = config.API_HEADER_KEY
    custom_header_prefix = config.API_HEADER_PREFIX
    sync_interval = config.API_SYNC_INTERVAL

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

        if self.mode == "delta":
            # handled by iwell default params (queries last 30 days)
            pass
        elif self.mode == "full":
            self.add_start(datetime(year=1970, month=1, day=1))
        elif self.mode == "sync":
            self.add_start(datetime.now() - timedelta(hours=self.sync_interval))
        else:
            pass

    def add_since(self, since: datetime, **kwargs) -> None:
        ts = int(since.timestamp())
        self.add_param("since", ts)

    def add_start(self, start: datetime, **kwargs) -> None:
        self.add_param("start", start.strftime("%Y-%m-%d"))

    def add_end(self, end: datetime, **kwargs) -> None:
        self.add_param("end", end.strftime("%Y-%m-%d"))

    def add_auth(self) -> None:
        self.headers.update({"Authorization": self.get_token(force_refresh=True)})

    def enqueue(self, headers: dict = None, params: dict = None, **kwargs) -> None:
        super().enqueue(headers, params, **kwargs)

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
            if since:
                # hack to get query access to the model via the first column in the columns set
                query.filter(columns[0].table.c[updated_column_name] >= since)

            df = pd.read_sql(query.statement, query.session.bind)
            records = df.to_dict(orient="records")
            ids += records
        return ids

    @property
    def last_sync(self):
        pass

    def determine_query_window(self) -> dict:
        # TODO: Implement start and end bounds
        since = None
        if self.mode == "delta":
            since = self.last_sync
        elif self.mode == "window":
            since = datetime.now() - (self.window_timedelta or self.window_timedelta)
        elif self.mode == "all":
            since = self.sync_epoch

        return {"since": since, "start": None, "end": None}

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

    config = get_active_config()
    endpoints = load_from_config(config)
    functions = config.functions
    url = config.API_BASE_URL

    dt = datetime(year=1970, month=1, day=1)
    ts = int(dt.timestamp())

    endpoint = endpoints["meters"]
    r = IWellRequestor(url, endpoint, since=dt)
    c = IWellCollector(endpoint)

    # req = next(r.sync_model())
    # response = response.get()
    responses = []
    for req in r.sync_model():
        responses.append(req.get())

    response = responses[0]
    self = c
    # responses[0].json()
    [x.status_code for x in responses]
    [len(x.text) for x in responses]
    [len(x.json()["data"]) for x in responses]
    [x.ok for x in responses]

    for resp in responses:
        c.collect(resp)

    # for req in r.sync_model():
    #     c.collect(req.get())

    # data = resp.json()["data"]
    # keys = {
    #     k.replace("iwell_", ""): v
    #     for k, v in resp.request.headers.items()
    #     if k.startswith("iwell")
    # }
    # df = c.tf.transform(data)
    # for key, value in keys.items():
    #     df[key] = int(value)
    # if not df.empty:
    #     c.model.bulk_merge(df)

    # # group by table
    # import itertools

    # keyfunc = lambda col: col["table_name"]
    # deps_sorted = sorted(for_query, key=keyfunc)
    # deps_grouped = list(itertools.groupby(deps_sorted, keyfunc))

    # cols_grouped = []
    # for _, grouper in deps_grouped:
    #     cols = []
    #     for k, v in list(grouper):
    #         print(f"k: {k}, v: {v}")
    #         if k == "column":
    #             cols.append(v)
    #     cols_grouped.append(cols)

    # fks = r.model.foreign_key_columns()
    # fk = fks[0]

    # dir(fk)
    # fk.column

    # r.model.query.with_entities(*[c.column for c in fks]).all()

    # tanks = r.model.query.all()
    # tank = tanks[0]
    # r.model.primary_keys_updated_since(datetime(year=2019, month=10, day=10))

    # ep = endpoints["tank_readings"]
    # model = ep.model

    # dir(model)
    # dir(model.__table__.foreign_keys)

    # fks = list(model.__table__.foreign_keys)
    # fk = fks[1]

    # dir(fk)
    # fk.target_fullname
    # dir(fk.column)
    # fk.column


class iwell_api:
    def add_since(self, since: datetime = None) -> str:
        """Return time filter for api endpoint. Default settings pull all data.

        Keyword Arguments:
            since {datetime} -- datetime object (default: 1420107010)

        Returns:
            [str] -- since clause
                            ex: "?since=32342561"
        """

        if since:
            ts = since.timestamp()
            self.logger.debug(f"Adding time filter: {ts} ({since})")

        else:
            dt = datetime.utcnow() - self.window_timedelta
            ts = dt.timestamp()
            self.logger.debug(f"Adding time filter: {ts} ({dt})")

        return "?since={}".format(int(ts))

    def add_start(self, start: str):
        """Example 'https://api.example.com/v1/path/to/resource?start=2015-01-01'

        Arguments:
            start {str} -- [description]
        """

        return f"?start={start}"

    def request_entity(self, delta: datetime = None):
        """Generic vehicle for sending GET requests

        Keyword Arguments:
            orient {str} -- specify orientation of resonse records (default: {'split'})
            delta {datetime} -- if None, all data is requested. if datetime is specified, data updated since the specified date will be requested.
        """

        # if delta is not a valid datetime, log error and return
        if delta and not isinstance(delta, datetime):
            # TODO: Add Sentry
            self.logger.exception(
                'Invalid function parameter "delta": not a valid datetime'
            )
            return None

        response = None
        # build uri
        uri = self.url + self.endpoint
        # append date limitation, if supplied
        uri = uri + self.add_since(delta) if delta else uri

        try:

            response = requests.get(uri, headers=self.headers)
            if response.ok:

                if self.njson:
                    self.df = pd.io.json.json_normalize(response.json()["data"])

                else:
                    self.df = pd.read_json(response.text, orient="split")

                self.set_last_success()

                self.logger.debug(f"GET / {uri}  ({self.download_count()} records)")
            else:
                self.logger.warn(
                    f'{response.request.path_url} - {response.json()["error"]["message"]}'
                )
                self.df = None
                self.set_last_failure()

        except Exception as e:
            self.logger.exception(f"GET / {uri} (Entity not retrieved) Error: {e}")
            self.df = None
            self.set_last_failure()

    def request_uri(self, uri: str, ids: dict = None):
        """Generic vehicle for sending GET requests

        Keyword Arguments:
            orient {str} -- specify orientation of resonse records (default: {'split'})
            delta {datetime} -- if None, all data is requested. if datetime is specified, data updated since the specified date will be requested.
        """

        if not ids:
            ids = {}

        response = None

        # print('Requesting: {}'.format(uri))
        try:

            response = requests.get(uri, headers=self.headers)
            if response.ok:

                # Append responses to dataframe
                if self.njson:
                    response_df = pd.io.json.json_normalize(response.json()["data"])

                else:
                    response_df = pd.read_json(response.text, orient="split")

                # Add ids as columns to dataframe
                for id, val in ids.items():
                    if id not in response_df.columns:
                        response_df[id] = val

                # Append response to object dataframe of responses
                if not response_df.empty:
                    self.df = self.df.append(response_df, sort=True)

                count = response_df.count().max()
                count = count if not pd.isna(count) else 0

                self.set_last_success()
                if count > 0:
                    self.logger.info(
                        f'GET {uri.replace(self.url, "")} ({count} records)'
                    )

            else:
                self.logger.exception(
                    f'GET {response.request.path_url.replace(self.url, "")} (Error) {response.json()["error"]["message"]}'
                )

        except Exception as e:
            self.logger.exception(f"Entity not retrieved -- {e}")
            self.set_last_failure()

    def request_uris(self):

        for uri, ids in self.uris.items():
            self.logger.debug(f"Requesting {uri} \n ids:  {ids}")
            self.request_uri(uri, ids)

        self.downloaded_status()
        self.uris = {}

    def parse_response(self):

        self.logger.debug("Parsing response")
        # if self.aliases is not None:
        self.df = self.df.rename(columns=self.aliases)

        # Fix timezones
        self.df[list(self.df.select_dtypes("datetime").columns)] = (
            self.df.select_dtypes("datetime")
            .apply(lambda x: x.dt.tz_localize("utc"))
            .apply(lambda x: x.dt.tz_convert("US/Central"))
        )

        # Fill NAs
        self.df = self.df.fillna(0)

        # if self.exclusions is not None:
        try:
            self.logger.debug(f"Dropping columns: {self.exclusions}")
            self.df = self.df.drop(columns=self.exclusions)
        except Exception as e:
            self.logger.error(e)

    def downloaded_status(self):
        """Return rowcount of downloads
        """

        if self.df is not None:
            n = self.df.count().max()
        else:
            n = 0

        self.logger.info(f"Downloaded {n} records")
        return n

    def keys(self):
        return list(self.df[self.aliases["id"]].values)

    def keyedkeys(self):
        return self.df[[self.aliases["id"]]].to_dict("records")

    def build_uri(
        self,
        well_id=None,
        group_id=None,
        tank_id=None,
        run_ticket_id=None,
        meter_id=None,
        field_id=None,
        reading_id=None,
        note_id=None,
        delta=None,
        start=None,
    ):

        """Wrapper to build a uri from a set of identifiers

        Arguments:
            well_id {str} (optional) --
            group_id {str} (optional) --
            tank_id {str} (optional) --
            run_ticket_id {str} (optional) --
            meter_id {str} (optional) --

        Returns:
            {str} -- url endpoint
        """

        ids = {
            "well_id": well_id,
            "group_id": group_id,
            "tank_id": tank_id,
            "run_ticket_id": run_ticket_id,
            "meter_id": meter_id,
            "field_id": field_id,
            "reading_id": reading_id,
            "note_id": note_id,
        }

        self.logger.debug(f"Building uri from keys: {ids}")
        uri = self.url + self.endpoint.format(**ids)
        if delta:
            uri = uri + self.add_since(since=delta)  # if delta else uri

        if start:
            uri = uri + self.add_start(start=start)
        self.uris[uri] = {id: val for id, val in ids.items() if val is not None}
        self.logger.debug(f"Built  {uri}")
        return uri

    def build_uris(self, ids: list, delta=None, start=None):
        """Wrapper to build multiple uris from a list of ids

        Arguments:
            ids {list} -- list of identifiers

        Returns:
            {list} -- list of populated uri endpoints
        """
        [self.build_uri(**x, delta=delta, start=start) for x in ids]

