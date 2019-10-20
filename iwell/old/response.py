# from __future__ import annotations
# import logging


# import requests
# import pandas as pd


# from src.collector import Collector
# from src.util import DefaultCounter
# from src.settings import __RESPONSE_LOG_MSG_TEMPLATE__

# logger = logging.getLogger(__name__)


# class Response(object):

#     PAGE_KEY = "X-PAGE-SIZE"
#     collector = None
#     _reasons = {
#         "Forbidden": ": Forbidden -- Refreshing token and trying again.",  # warning
#         "Unauthorized": ": Unauthorized -- Refreshing token and trying again.",  # warning
#         "Service Unavailable": ": Service Unavailable -- Trying again in a few seconds.",
#         "Too Many Attempts": ": Too Many Attempts -- Exceeded maximum attempts.",
#         "Failed": ": Failed -- Request failed for an unknown reason.",
#     }

#     def __init__(self, response: requests.Response):
#         # FIXME: Add super()
#         self.response = response
#         self.request = response.request
#         self.reason = self.response.reason
#         self.method = self.request.method
#         self.elapsed_seconds = self.response.elapsed.seconds
#         self.elapsed_microseconds = self.response.elapsed.microseconds
#         self.ok = self.response.ok
#         self.path_url = self.request.path_url
#         self.endpoint = self.request.endpoint
#         self.headers = self.response.headers
#         self.endpoint_name = self.endpoint.name
#         self.endpoint_url = self.endpoint.path_url
#         self.version = self.endpoint.version
#         self.tablename = self.endpoint.tablename
#         self.exclusions = self.endpoint.exclusions
#         self.aliases = self.endpoint.aliases
#         self.entities = self.endpoint.entities
#         self.primary_keys = self.endpoint.primary_keys
#         self.elapsed = self.response.elapsed

#         self.metrics = {}
#         self._df = None

#         try:
#             self.json = self.response.json()
#         except:
#             self.json = {}

#     def __repr__(self):
#         return f"<Response: {self.version}/{self.endpoint_name} - {self.nrows} rows>"

#     @property
#     def is_v1(self):
#         return self.version == "v1"

#     @property
#     def is_v2(self):
#         return self.version == "v2"

#     @property
#     def nrows(self):
#         return len(self.df)

#     @property
#     def is_paged(self):
#         return self.PAGE_KEY in self.headers.keys()

#     @property
#     def nrequested(self):
#         if self.is_v1:
#             return int(self.headers[self.PAGE_KEY])
#         else:
#             return -1

#     @property
#     def columns(self):
#         return self.df.columns.to_list()

#     @property
#     def links(self):
#         if self.is_v2:
#             return self.response.links
#         else:
#             return None

#     @property
#     def next_url(self):
#         if self.links:
#             return self.links["next"]["url"]
#         else:
#             return None

#     @property
#     def df(self):
#         if self._df is None:
#             self._df = self._to_df()
#         return self._df

#     @df.setter
#     def df(self, frame):
#         self._df = frame

#     @property
#     def returned_equals_requested(self) -> bool:
#         return self.nrows == self.nrequested

#     @property
#     def returned_rows(self) -> bool:
#         return self.nrows > 0

#     def has_next(self):
#         if self.is_v1:
#             return all(
#                 [
#                     self.is_v1,
#                     self.is_paged,
#                     self.returned_equals_requested,
#                     self.returned_rows,
#                 ]
#             )

#         else:  # is v2
#             has_next = self.next_url is not None and self.nrows > 0
#             return all([self.is_v2, has_next])

#     def next(self):
#         from src.request import Request

#         return Request.from_response(self)

#     def _reason_message(self, reason: str) -> str:
#         if reason in self._reasons:
#             return self._reasons[reason]
#         else:
#             return ""

#     def _message_prefix(self):
#         return __RESPONSE_LOG_MSG_TEMPLATE__.format(
#             method=self.method, url=self.path_url, reason=self.reason
#         )

#     def message(self):

#         reason = self.reason
#         level = "info"
#         message = self._message_prefix()

#         if reason is None:
#             reason = "Failed"
#             level = "exception"

#         if self.ok:
#             level = "info"
#             message += f"{self.nrows} rows ({self.elapsed_seconds}.{self.elapsed_microseconds})"

#         elif self.request.has_attempts:
#             level = "warning"

#         else:
#             reason = "Too Many Attempts"
#             level = "error"

#         message += self._reason_message(reason)

#         if level == "info":
#             logger.info(message)
#         elif level == "warning":
#             logger.warning(message)
#         else:
#             logger.exception(message)

#         return message

#     def _to_df(self):
#         self.df = pd.DataFrame.from_records(self.json)
#         return self.df

#     def _mapping(self):
#         return {k: k for k in self.df.columns.tolist()}

#     def to_collector(self, collect: bool = True, load: bool = True) -> Collector:

#         c = Collector(self)
#         if collect:
#             c.collect()
#         return c

#     def _column_sizes(self) -> dict:
#         """Return a dict of the max length of each field

#             Example:
#                     {
#                         'field_name': 52
#                     }

#         """
#         lengths = DefaultCounter(int)
#         for col in self.df.columns:
#             ct = self.df[col].astype("object").astype("str").str.len().max()
#             ct = ct if pd.notna(ct) else 0
#             lengths.update({col: ct})

#         return lengths

#     def _template_mapping(self) -> dict:
#         """Return a dict of the max length of each field

#             Example:
#                     {
#                         'field_name': 52
#                     }

#         """
#         d = {}
#         for col in self.df.columns:
#             d.update({col: col})

#         return d

#     def tz_localize(ts: pd.Timestamp) -> pd.Timestamp:
#         # Convert last update to UTC
#         if ts.tz is not None:
#             ts = ts.localize("utc")
#         else:
#             ts = ts.tz_convert("US/Central")

#         return ts


# if __name__ == "__main__":

#     from src.request import Request
#     from src.endpoint import Endpoint
#     from src.settings import ENDPOINTS

#     e = Endpoint(**ENDPOINTS["rigs-v2"])
#     request = Request("GET", e)
#     resp = request.send()
#     req = resp.next()
