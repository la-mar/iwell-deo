
import logging
import os

LOAD_TO_DB = True

LOGLEVEL = logging.INFO

ENV_NAME = os.environ['ENV_NAME']


""" API keys """
SENTRY_KEY = "http://b362e6ecfa16458dbf00854f1f723c00@sentry.driftwoodenergy.com/9"
SENTRY_LEVEL = logging.WARNING
SENTRY_EVENT_LEVEL = logging.WARNING


# DATABASE_URI = 'mssql+pymssql://DWENRG-SQL01\\DRIFTWOOD_DB/iWell'
DATABASE_URI = os.environ['DATABASE_URI']+'iWell'

DEFAULT_EXCLUSIONS = ['updated', 'inserted']



YAML_CONFIG_PATH = './config/config.yaml'
LOG_CONFIG_PATH = './config/logging.yaml'


DEFAULT_TIMESTAMP = 21600 # 1970-01-01
DEFAULT_START = '1970-01-01'












