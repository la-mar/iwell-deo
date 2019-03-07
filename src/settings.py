
import logging
import os

LOAD_TO_DB = True

LOGLEVEL = logging.INFO

ENV_NAME = os.environ['ENV_NAME']


""" API keys """
SENTRY_KEY = "https://e98008aac80c407ab03ce6a826368190@sentry.io/1365080"
SENTRY_LEVEL = logging.ERROR
SENTRY_EVENT_LEVEL = logging.ERROR


DATABASE_URI = 'mssql+pymssql://DWENRG-SQL01\\DRIFTWOOD_DB/iWell'
DEFAULT_EXCLUSIONS = ['updated', 'inserted']



YAML_CONFIG_PATH = './config/config.yaml'
LOG_CONFIG_PATH = './config/logging.yaml'


DEFAULT_TIMESTAMP = 21600 # 1970-01-01
DEFAULT_START = '1970-01-01'












