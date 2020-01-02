import pytest  # pylint: disable=unused-import

from sentry import load

from requests_mock import ANY

# SENTRY_ENABLED = os.getenv("SENTRY_ENABLED", False)
# SENTRY_DSN = os.getenv("SENTRY_DSN", None)
# SENTRY_LEVEL = os.getenv("SENTRY_LEVEL", logging.ERROR)
# SENTRY_EVENT_LEVEL = os.getenv("SENTRY_EVENT_LEVEL", logging.ERROR)
# SENTRY_ENV_NAME = os.getenv("SENTRY_ENV_NAME", ENV_NAME)
# SENTRY_RELEASE = f"{project}-{version}"


class TestSentryIntegration:
    def test_load_sentry_integation(self, requests_mock):
        """ Pretty much just make sure no exceptions are raised """
        requests_mock.register_uri("GET", ANY, text="response_text")
        load()

    def test_load_sentry_failure(self, conf, requests_mock):
        requests_mock.register_uri("GET", ANY, text="response_text")
        conf.SENTRY_DSN = -1
        with pytest.raises(Exception):
            load(conf)

    def test_load_sentry_ignore_bogus_params(self, conf, requests_mock):
        requests_mock.register_uri("GET", ANY, text="response_text")
        conf.SENTRY_BOGUS_KEY = "bogus_value"
        load(conf)
