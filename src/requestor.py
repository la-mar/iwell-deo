import logging
import os
import requests  # connect to apis
import json  # parse json if you need it
import pandas as pd  # dataframes
from pprint import pprint
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.orm import *
from src.retry import retry


from oauthlib.oauth2 import LegacyApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session
from src.config import Config
from src.settings import YAML_CONFIG_PATH, LOGLEVEL, DEFAULT_TIMESTAMP

pd.options.display.max_rows = None
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('large_repr', 'truncate')
pd.set_option('precision',2)

logger = logging.getLogger(__name__)
logging.getLogger('requests.packages.urllib3').setLevel(logging.WARNING)

_properties = Config(YAML_CONFIG_PATH)

def save_properties():
    _properties.save()

#! FIX YAML

class iwell_api(object):
    url = _properties['url']
    logger = logging.getLogger(f'{__name__}.iwell_api')

    def __init__(self, endpoint_name: str):
        self.headers = {
            'Authorization': self.getBearer()
        }
        self.__name__ = endpoint_name
        self.df = pd.DataFrame()
        self.endpoint_name = endpoint_name
        self.uris = {}
        self.logger = logging.getLogger(f'{__name__}.{__class__.__name__}.{self.__name__}')

        self.endpoint = _properties['endpoints'][endpoint_name]['path']
        self.aliases = _properties['endpoints'][endpoint_name]['aliases']
        self.exclusions = _properties['endpoints'][endpoint_name]['exclude']
        self.njson = _properties['endpoints'][endpoint_name]['normalize']
        self.keys = _properties['endpoints'][endpoint_name]['keys']
        self.logger.info(f'Created endpoint handler: {self.__name__}')

    @classmethod
    def reload_properties(cls):
        """refresh property attributes
        """
        cls.logger.debug(f'Reloading properties from {YAML_CONFIG_PATH}')
        _properties = Config(YAML_CONFIG_PATH)

    @classmethod
    def cache_properties(cls):
        """refresh property attributes
        """
        cls.logger.debug('Writing cache time.')
        _properties['cached_at'] = datetime.now()

    @classmethod
    def _getAccessToken(cls):
        # FIXME: Fetching new token tries to attach to str and fails
        """Fetch a new access token from the provider using OAuth2"""
        # https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#backend-application-flow
        oauth = OAuth2Session(
            client=LegacyApplicationClient(client_id=_properties['client_id']))

        cls.logger.info(f'Fetching new oauth token: {oauth}')

        return oauth.fetch_token(
            token_url= cls.url + _properties['token_path']
            , username=_properties['username']
            , password=_properties['password']
            , client_id=_properties['client_id']
            , client_secret=_properties['client_secret']
        )

    @classmethod
    def _token_saver(cls, response_token):
        """Save response token and token expiration date to configuration file.
        Arguments:
            response_token {dict} -- oauth response object
        Returns:
            str -- response token as string
        """

        _properties["token"] = response_token["access_token"]
        _properties["token_expiration"] = (
            datetime.utcfromtimestamp(response_token['expires_at']))
        cls.logger.info(f'Saved token: {_properties["token"]}')
        return response_token

    @classmethod
    @retry(Exception, tries=10, delay=5, backoff=2, logger=logger)
    def getAccessToken(cls, force = False):
        """ Checks if saved token is still valid"""
        token = _properties["token"]
        expiration = _properties["token_expiration"]

        # if force change flag is False
        if not force:
            # if expiration date exists and is a datetime
            if expiration is not None and isinstance(expiration, datetime):
                # if current time is < time of expiration minus one day
                if datetime.now() < expiration - timedelta(days=1):
                    # print('Current token is valid.')
                    return token

        # Token isn't valid. Return new token
        cls.logger.info('Retrieving new token.')

        try:
            token = cls._token_saver(cls._getAccessToken())['token']

        except KeyError as e:
            cls.logger.debug('Fetching new token failed.')

        return token

    @classmethod
    def getBearer(cls):
        """Returns bearer authorization string for inclusion
            in request header.
        Returns:
            str -- bearer string
        """

        bearer =  "Bearer " + cls.getAccessToken()

        cls.logger.debug(f'Bearer Auth: {bearer}')

        return bearer

    def add_since(self, since: datetime = None) -> str:
        """Return time filter for api endpoint. Default settings pull all data.

        Arguments:
            endpoint {str} -- Provider URI or endpoint

        Keyword Arguments:
            since {datetime} -- datetime object (default: 1420107010)

        Returns:
            [str] -- since clause
                            ex: "?since=32342561"
        """

        t = DEFAULT_TIMESTAMP
        if since:
            self.logger.debug(f'Adding time filter: {since.timestamp()} ({since})')
            t = since.timestamp()
        else:
            self.logger.debug(f'Adding time filter: {t} ({datetime.fromtimestamp(t)})')

        return '?since={}'.format(int(t))


    def add_start(self, start: str):
        """Example 'https://api.iwell.info/v1/wells/17588/production?start=2015-01-01'

        Arguments:
            start {str} -- [description]
        """

        return f'?start={start}'

    def get_last_success(self):
        """Get last successful runtime of this endpoint

        Returns:
            [datetime] -- last successful runtime
        """

        last_success = _properties['endpoints'][self.endpoint_name]['last_success']

        # self.logger.info(f'Last successful run time: {last_success}')

        return last_success


    def set_last_success(self):
        """Set last successful runtime of this endpoint

        Returns:
            None
        """

        success = datetime.now()

        self.logger.debug(f'Setting successful run time: {success}')

        _properties['endpoints'][self.endpoint_name]['last_success'] = success
        self.cache_properties()


    def get_last_failure(self):
        """Get last failed runtime of this endpoint

        Returns:
            [datetime] -- last successful runtime
        """

        # self.logger.info(f'Last successful run time: {last_success}')

        return _properties['endpoints'][self.endpoint_name]['last_failure']


    def set_last_failure(self):
        """Set last failed runtime of this endpoint

        Returns:
            None
        """

        failed = datetime.now()

        self.logger.debug(f'Setting failed run time: {failed}')



        _properties['endpoints'][self.endpoint_name]['last_failure'] = failed
        self.cache_properties()

    def request_entity(self, delta: datetime = None):
        """Generic vehicle for sending GET requests

        Keyword Arguments:
            orient {str} -- specify orientation of resonse records (default: {'split'})
            delta {datetime} -- if None, all data is requested. if datetime is specified, data updated since the specified date will be requested.
        """

        # if delta is not a valid datetime, log error and return
        if delta and not isinstance(delta, datetime):
            # TODO: Add Sentry
            self.logger.exception('Invalid function parameter "delta": not a valid datetime')
            return None

        response = None
        # build uri
        uri = self.url+self.endpoint
        # append date limitation, if supplied
        uri = uri + self.add_since(delta) if delta else uri

        try:

            response = requests.get(uri, headers=self.headers)
            if response.ok:

                if self.njson:
                    self.df = pd.io.json.json_normalize(response.json()['data'])

                else:
                    self.df = pd.read_json(response.text, orient='split')

                self.set_last_success()

                self.logger.debug(f'GET / {uri}  ({self.download_count()} records)')
            else:
                self.logger.warn(f'{response.request.path_url} - {response.json()["error"]["message"]}')
                self.df = None
                self.set_last_failure()

        except Exception as e:
            self.logger.exception(f'GET / {uri} (Entity not retrieved) Error: {e}')
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
                    response_df = pd.io.json.json_normalize(response.json()['data'])

                else:
                    response_df = pd.read_json(response.text, orient='split')

                # Add ids as columns to dataframe
                for id, val in ids.items():
                    if id not in response_df.columns:
                        response_df[id] = val

                # Append response to object dataframe of responses
                if not response_df.empty:
                    self.df = self.df.append(response_df, sort = True)

                count = response_df.count().max()
                count = count if not pd.isna(count) else 0

                self.set_last_success()
                if count > 0:
                    self.logger.info(f'GET {uri.replace(self.url, "")} ({count} records)')

            else:
                self.logger.exception(f'GET {response.request.path_url.replace(self.url, "")} (Error) {response.json()["error"]["message"]}')


        except Exception as e:
            self.logger.exception(f'Entity not retrieved -- {e}')
            self.set_last_failure()

    def request_uris(self):

        for uri, ids in self.uris.items():
            self.logger.debug(f'Requesting {uri} \n ids:  {ids}')
            self.request_uri(uri, ids)

        self.downloaded_status()
        self.uris = {}

    def parse_response(self):

        self.logger.debug('Parsing response')
        # if self.aliases is not None:
        self.df = self.df.rename(columns = self.aliases)

        # Fix timezones
        self.df[list(self.df.select_dtypes('datetime').columns)] = \
            self.df.select_dtypes('datetime').apply(lambda x: x.dt.tz_localize('utc')) \
                                             .apply(lambda x: x.dt.tz_convert('US/Central'))

        # Fill NAs
        self.df = self.df.fillna(0)

        # if self.exclusions is not None:
        try:
            self.logger.debug(f'Dropping columns: {self.exclusions}')
            self.df = self.df.drop(columns = self.exclusions)
        except Exception as e:
            self.logger.error(e)


    def downloaded_status(self):
        """Return rowcount of downloads
        """

        if self.df is not None:
            n = self.df.count().max()
        else:
            n = 0

        self.logger.info(f'Downloaded {n} records')
        return n


    def keys(self):
        return list(self.df[self.aliases['id']].values)


    def keyedkeys(self):
        return self.df[[self.aliases['id']]].to_dict('records')


    def build_uri(self, well_id = None, group_id = None, tank_id = None
                , run_ticket_id = None, meter_id = None, field_id = None
                , reading_id = None, note_id = None, delta = None, start = None):

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
            'well_id' : well_id
            , 'group_id' : group_id
            , 'tank_id' : tank_id
            , 'run_ticket_id' : run_ticket_id
            , 'meter_id' : meter_id
            , 'field_id' : field_id
            , 'reading_id' : reading_id
            , 'note_id' : note_id
            }

        self.logger.debug(f'Building uri from keys: {ids}')
        uri =  self.url+self.endpoint.format(**ids)
        if delta:
            uri = uri + self.add_since(since = delta) # if delta else uri

        if start:
            uri = uri + self.add_start(start = start)
        self.uris[uri] = {id: val for id, val in ids.items() if val is not None}
        self.logger.debug(f'Built  {uri}')
        return uri


    def build_uris(self, ids: list, delta = None, start = None):
        """Wrapper to build multiple uris from a list of ids

        Arguments:
            ids {list} -- list of identifiers

        Returns:
            {list} -- list of populated uri endpoints
        """
        [self.build_uri(**x, delta = delta, start = start) for x in ids]


if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)


def _getAccessToken():
    # FIXME: Fetching new token tries to attach to str and fails
    """Fetch a new access token from the provider using OAuth2"""
    # https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#backend-application-flow
    oauth = OAuth2Session(
        client=LegacyApplicationClient(client_id=_properties['client_id']))

    logger.info(f'Fetching new oauth token: {oauth}')

    return oauth.fetch_token(
        token_url= _properties['url']+ _properties['token_path']
        , username=_properties['username']
        , password=_properties['password']
        , client_id=_properties['client_id']
        , client_secret=_properties['client_secret']
    )



_getAccessToken()