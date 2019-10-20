from typing import Dict, Optional
import logging
import os
from datetime import datetime, timedelta
from time import sleep
from copy import copy
from urllib.parse import urlparse

import requests
import logging

from collector.util import retry

logger = logging.getLogger(__name__)

# r = Request("GET", "https://api.example.com/v1/path/1/subpath/2/values")


class Request(requests.Request):
    """ An objects specifying a single request to be made to an endpoint."""

    _session = None
    _max_attempts = 3
    headers: Optional[Dict[str, str]] = {}
    params: Optional[Dict[str, str]] = {}
    attempts = 0
    timeouts = 0

    def __init__(
        self,
        method: str,
        url: str,
        headers: Dict[str, str] = None,
        params: Dict[str, str] = None,
        session: requests.Session = None,
    ):

        super().__init__(method)
        self.method = method
        self.url = url
        self.headers = headers
        self._session = session

    def __repr__(self):
        return f"{self.method} {self.path}"

    @property
    def session(self):
        if self._session is None:
            self.session = requests.Session()
        return self._session

    @property
    def path(self):
        return urlparse(self.url).path

    @session.setter
    def session(self, value):
        self._session = value

    def prepare(self):
        """Extend default prepare behavior to add a reference to an endpoint object.
        Done with the goal of passing the endpoint reference into the response object.

        Returns:
            prepared_request
        """
        prepared_request = super().prepare()
        # optionally modify exact request here
        return prepared_request

    @retry(Exception, tries=10, delay=5, backoff=2, logger=logger)
    def get(self):
        return self.session.get(self.url, headers=self.headers, params=self.params)


if __name__ == "__main__":

    from collector.requestor import Requestor
    from collector.request import Request

    from collector.endpoint import Endpoint
    from config import get_active_config

    config = get_active_config()
    endpoints = config.endpoints
    functions = config.functions
    endpoint = endpoints.wells

    url = config.API_BASE_URL + endpoints.wells.path
    requestor = Requestor("req_name", endpoint, functions)

    headers = {"Authorization": requestor.get_token()}
    params = {}

    r2 = requests.get(url, headers=headers, params=params)
    dir(r2)
    r2.request.headers

    r = Request("GET", url)
    dir(r.session)
    r.session.get(url, headers=headers, params=params)

    class Old:
        @property
        def is_v1(self):
            return self.version == "v1"

        @property
        def is_v2(self):
            return self.version == "v2"

        def format_url(self) -> str:
            self.url = self.add_default_params()
            self.url = self.url.format(page=self.current_page, version=self.version)
            return self.url

        def select_fields(self, fields: list) -> None:
            """Specify list of columns to return from the request. Convenience wrapper for add_param.

            Arguments:
                fields {list} -- list of valid field names
            """
            # TODO: Validate field names before adding
            # TODO: use add_function()
            fields = "in({})".format(",".join(fields))

            self.request_params["fields"] = fields

        def get_function(
            self, func_name: str, value=None, values=None, value1=None, value2=None
        ) -> str:

            if not func_name in FUNCTIONS.keys():
                logger.warning(f"{func_name} not found in function library.")
                return None
            try:

                if values:
                    values = "".join(values)

                return FUNCTIONS[func_name]["func"].format(
                    value=value, value1=value1, value2=value2, values=values
                )
            except:
                logger.error(f"Failed to add function: {func_name}.")

        def add_param(
            self,
            name: str,
            func_name: str = "equal",
            value: str = None,
            values=None,
            value1=None,
            value2=None,
        ):
            """Add a parameter to the request query string

            Arguments:
                name {str} -- parameter name
                value {str} -- parameter value

            Returns:
                None
            """

            try:
                if func_name == "equal" and value is not None:
                    self.params[name] = value
                else:
                    self.params[name] = self.get_function(
                        func_name,
                        value=value,
                        value1=value1,
                        value2=value2,
                        values=values,
                    )

                self.logger.debug(
                    f"Added parameter to {self.endpoint.name}: {name}: {self.params[name]}"
                )

            except KeyError as ke:
                self.logger.error(
                    "{error} -- Parameter is invalid for this endpoint".format(error=ke)
                )

            return self

        def add_updated_since(self, since: str):
            """Wraps for add_param. Add a pagesize option to the request  params

            Keyword Arguments:
                size {int} -- size of page

            Returns:
                None
            """

            if since is None:
                logger.warning("Cannot add time delta of None to request params.")
                return self

            if self.updated_column_name is None:
                logger.info(
                    "Endpoint has no time delta key. Bypassing adding time delta to params."
                )
                return self

            if self.is_v1:
                return self.add_param(
                    self.updated_column_name, func_name="equal", value=since
                )
            else:
                return self.add_param(
                    self.updated_column_name,
                    func_name="greater_than_equal",
                    value=since,
                )

            return self

        def add_pagesize(self, size: int = 100):
            """Wraps for add_param. Add a pagesize option to the request  params

            Keyword Arguments:
                size {int} -- size of page

            Returns:
                None
            """

            return self.add_param("pagesize", func_name="equal", value=size)

        def add_default_params(self):

            if hasattr(self, "url_params"):
                if self.url_params is not None:
                    for default_param in self.url_params:
                        default_value = self.spec[default_param][
                            "Default Value"
                        ].format(page=self.current_page)
                        self.add_param(
                            default_param, func_name="equal", value=default_value
                        )
            return self.url

        def set_url(self, url: str) -> str:
            self.url = url
            # self.add_default_params()
            self.format_url()
            return self.url

        def reset_url(self):
            self.url = self.set_url(self.endpoint.url)
            return self.url

        def next_url(self, next_url: str):
            self.url = os.path.dirname(self.url)
            self.url = self.url + next_url
            self.params = {}
            return self

        def next(self, url: str = None):
            if self.is_v1:
                return self.next_page()
            else:
                return self.next_url(url)

        def prepare(self):
            """Extend default prepare behavior to add a reference to an endpoint object.
            Done with the goal of passing the endpoint reference into the response object.

            Returns:
                prepared_request
            """
            self.format_url()
            prepared_request = super().prepare()
            prepared_request.endpoint = self.endpoint
            prepared_request.params = self.params
            prepared_request.current_page = self.current_page
            prepared_request.pagesize = self.pagesize
            prepared_request.collect = self.collect
            return prepared_request

        def merge_session(self, session: requests.Session):
            if self.session is None:
                self.session = session
            return self.session

        def _auth_exists(self) -> bool:
            return "Authorization" in self.headers.keys() if self.is_v2 else True

        def validate_headers(self):

            if (
                not self._auth_exists()
            ):  # v2 is implied as v1 will default to True in the auth_valid expression.
                self.add_bearer()

            if not self._has_default_headers():
                self.headers.update(Request.headers)

            return self

        def _has_default_headers(self) -> bool:
            return all([x in self.headers.keys() for x in Request.headers.keys()])

        @classmethod
        def retrieve_bearer(cls, force_refresh=False):
            return cls._token_manager.getBearer(force_refresh=force_refresh)

        @classmethod
        def add_bearer(self, force_refresh=False):
            self.headers.update(
                {"Authorization": Request.retrieve_bearer(force_refresh=force_refresh)}
            )
            return self

        @property
        def has_attempts(self):
            return self.attempts + self.timeouts <= self._max_attempts

        @classmethod
        def from_response(cls, response):  # TODO: There is a better way to handle this.
            req = Request(
                response.request.method,
                response.request.endpoint,
                page=response.request.current_page,
                pagesize=response.request.pagesize,
                collect=response.request.collect,
            )
            # req.params = response.request.params
            if req.is_v1:  # next_page
                req.current_page += 1
                req.reset_url()
                req.add_param("page", func_name="equal", value=req.current_page)
            else:
                new_url = os.path.dirname(req.url) + response.next_url
                req.set_url(new_url)
            return req

        def _resend(
            self,
            failed_request: requests.PreparedRequest,
            is_recursive: bool = True,
            collect: bool = False,
            wait: int = 0,
        ) -> requests.Response:

            request = failed_request
            request.attempts += 1
            sleep(wait)
            if request.version == "v2":
                self.add_bearer(force_refresh=True)
            return self.send(request, is_recursive, collect)

        def send(
            self,
            session: requests.Session = None,
            recurse: bool = True,
            collect: bool = False,
        ) -> Response:

            # TODO: make this not recursive so the collection can be done elsewhere. Probably move the control flow to Requestor

            request = self.validate_headers()
            prepared_request = self.prepare()
            method = prepared_request.method
            url = prepared_request.path_url
            wait = 0
            response = None

            try:
                response = self.merge_session(session).send(prepared_request)

                self.logger.info(
                    f"Sending: {prepared_request.url[len(self.base_url):]}"
                )
                if response.ok:
                    response = Response(response)

                elif response.reason == "Service Unavailable":
                    wait = 30

            except TimeoutError as te:
                self.attempts += 1
                wait = 60 * self.attempts
                self.logger.warning(
                    f"{method} - {url}: Request timed out ({self.attempts} of {self._max_attempts}). Waiting {wait} seconds to try again."
                )

            except Exception as e:
                self.attempts += 1
                logger.exception(f"{method} - {url}: Error sending request ()")

            if self.has_attempts and not response.ok:
                return self._resend(
                    request, is_recursive=recurse, collect=collect, wait=wait
                )

            # summary = self.collector_summary
            # msg = f'Finished request chain for {self.endpoint.name} - ups: {summary["updates"]}, ins: {summary["inserts"]}'
            # logger.info(msg)

            # if summary['updates'] + summary['inserts'] > 0:
            #     rollbar.report_message(msg, level = 'info')

            return response

    from src.settings import ENDPOINTS

    e = Endpoint(**ENDPOINTS["permits-v2"])
    r = Request("GET", e)
    r.add_updated_since("2019-02-25")
    r.add_param(r.updated_column_name, value="2019-02-25")

    resp = r.send()
