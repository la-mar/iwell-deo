import logging
import os
import socket

import pandas as pd
import tomlkit
import yaml
from attrdict import AttrDict
from sqlalchemy.engine.url import URL

""" Optional Pandas display settings"""
pd.options.display.max_rows = None
pd.set_option("display.float_format", lambda x: "%.2f" % x)
pd.set_option("large_repr", "truncate")
pd.set_option("precision", 2)

_pg_aliases = ["postgres", "postgresql", "psychopg2", "psychopg2-binary"]
_mssql_aliases = ["mssql", "sql server"]

APP_SETTINGS = os.getenv("APP_SETTINGS", "")


def make_config_path(path: str, filename: str) -> str:
    return os.path.abspath(os.path.join(path, filename))


def load_config(path: str) -> AttrDict:
    with open(path) as f:
        return AttrDict(yaml.safe_load(f))


def get_active_config() -> AttrDict:
    return globals()[APP_SETTINGS.replace("iwell.config.", "")]()


def get_default_port(driver: str):
    port = None
    if driver in _pg_aliases:
        port = 5432
    elif driver in _mssql_aliases:
        port = 1433

    return port


def get_default_driver(dialect: str):
    driver = None
    if dialect in _pg_aliases:
        driver = "postgres"  # "psycopg2"
    elif dialect in _mssql_aliases:
        driver = "pymssql"

    return driver


def get_default_schema(dialect: str):
    driver = None
    if dialect in _pg_aliases:
        driver = "public"
    elif dialect in _mssql_aliases:
        driver = "dbo"

    return driver


def make_url(url_params: dict):
    return URL(**url_params)


def _get_project_meta():
    with open("./pyproject.toml") as pyproject:
        file_contents = pyproject.read()

    return tomlkit.parse(file_contents)["tool"]["poetry"]


pkg_meta = _get_project_meta()
project = pkg_meta.get("name")
version = pkg_meta.get("version")


class BaseConfig:
    """Base configuration"""

    DEFAULT_COLLECTION_INTERVAL = {"hours": 1}
    ENV_NAME = os.getenv("ENV_NAME", socket.gethostname())

    """ Sentry """
    SENTRY_ENABLED = os.getenv("SENTRY_ENABLED", False)
    SENTRY_DSN = os.getenv("SENTRY_DSN", None)
    SENTRY_LEVEL = os.getenv("SENTRY_LEVEL", logging.ERROR)
    SENTRY_EVENT_LEVEL = os.getenv("SENTRY_EVENT_LEVEL", logging.ERROR)
    SENTRY_ENV_NAME = os.getenv("SENTRY_ENV_NAME", ENV_NAME)
    SENTRY_RELEASE = f"{project}-{version}"

    """ Config """
    CONFIG_BASEPATH = "./config"
    COLLECTOR_CONFIG_PATH = make_config_path(CONFIG_BASEPATH, "collector.yaml")
    COLLECTOR_CONFIG = load_config(COLLECTOR_CONFIG_PATH)

    """ Logging """
    LOG_LEVEL = os.getenv("LOG_LEVEL", logging.INFO)

    """ --------------- Sqlalchemy --------------- """

    DATABASE_DIALECT = os.getenv("DATABASE_DIALECT", "postgres")
    DATABASE_DRIVER = os.getenv("DATABASE_DRIVER", get_default_driver(DATABASE_DIALECT))
    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME", "")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT", get_default_port(DATABASE_DRIVER))
    DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", get_default_schema(DATABASE_DRIVER))
    DATABASE_NAME = os.getenv("DATABASE_NAME", "postgres")
    DATABASE_URL_PARAMS = {
        "drivername": DATABASE_DRIVER,
        "username": DATABASE_USERNAME,
        "password": DATABASE_PASSWORD,
        "host": DATABASE_HOST,
        "port": DATABASE_PORT,
        "database": DATABASE_NAME,
    }
    SQLALCHEMY_DATABASE_URI = str(make_url(DATABASE_URL_PARAMS))
    DEFAULT_EXCLUSIONS = ["updated_at", "inserted_at"]

    """ Celery """
    # CELERY_TIMEZONE = "US/Central"
    BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    CELERY_SEND_TASK_SENT_EVENT = True
    CELERY_TASK_LIST = ["collector.tasks"]
    CELERYD_TASK_SOFT_TIME_LIMIT = 3600
    CELERY_TASK_SERIALIZER = "pickle"
    CELERY_ACCEPT_CONTENT = ["json", "pickle"]
    # CELERYD_HIJACK_ROOT_LOGGER = False
    # CELERY_RESULT_DBURI = "db+" + SQLALCHEMY_DATABASE_URI
    # CELERY_RESULT_EXTENDED = True

    """ API """
    API_CLIENT_TYPE = os.getenv("IWELL_CLIENT_TYPE", "legacy")
    API_BASE_URL = os.getenv("IWELL_URL")
    API_CLIENT_ID = os.getenv("IWELL_CLIENT_ID")
    API_CLIENT_SECRET = os.getenv("IWELL_CLIENT_SECRET")
    API_USERNAME = os.getenv("IWELL_USERNAME")
    API_PASSWORD = os.getenv("IWELL_PASSWORD")
    API_TOKEN_PATH = os.getenv("IWELL_TOKEN_PATH")
    API_PAGESIZE = os.getenv("IWELL_PAGESIZE", 1000)
    API_HEADER_KEY = os.getenv("IWELL_HEADER_KEY", "API-HEADER-KEY")
    API_HEADER_PREFIX = os.getenv("IWELL_HEADER_PREFIX", "DEO")

    @property
    def show(self):
        return [x for x in dir(self) if not x.startswith("_")]

    @property
    def api_params(self):
        return {
            key.lower().replace("api_", ""): getattr(self, key)
            for key in dir(self)
            if key.startswith("API_")
        }

    @property
    def sentry_params(self):
        return {
            key.lower().replace("sentry_", ""): getattr(self, key)
            for key in dir(self)
            if key.startswith("SENTRY_")
        }

    @property
    def endpoints(self):
        return self.COLLECTOR_CONFIG.endpoints

    @property
    def functions(self):
        return self.COLLECTOR_CONFIG.functions


class DevelopmentConfig(BaseConfig):
    """Development configuration"""

    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    DEBUG_TB_ENABLED = True
    SECRET_KEY = os.getenv("SECRET_KEY", "test")
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(BaseConfig):
    """Testing configuration"""

    CONFIG_BASEPATH = "./test/data"
    COLLECTOR_CONFIG_PATH = make_config_path(CONFIG_BASEPATH, "collector.yaml")
    COLLECTOR_CONFIG = load_config(COLLECTOR_CONFIG_PATH)
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL")
    TOKEN_EXPIRATION_DAYS = 0
    TOKEN_EXPIRATION_SECONDS = 3

    API_BASE_URL = "https://api.example.com/v3"
    API_CLIENT_ID = "test_client_id"
    API_CLIENT_SECRET = "test_client_secret"
    API_USERNAME = "username"
    API_PASSWORD = "password"
    API_TOKEN_PATH = "/auth"
    API_DEFAULT_PAGESIZE = 100


class StagingConfig(BaseConfig):
    """Staging configuration"""

    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


class ProductionConfig(BaseConfig):
    """Production configuration"""

    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
