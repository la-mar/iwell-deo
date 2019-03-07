""" Logger definitions """

import os
import logging
import logging.config

import sentry_sdk

from src.version import __release__

try:
    from src.settings import LOGLEVEL
except:
    print('Could not find LOGLEVEL in settings.')
    LOGLEVEL = logging.INFO


LOGDIR = './log'

if not os.path.exists(LOGDIR):
    os.mkdir(LOGDIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s()] %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'funcnames': {
            'format': '[%(name)s: %(lineno)s - %(funcName)s()] %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console':{
            'level':LOGLEVEL,
            'class':'logging.StreamHandler',
            'formatter': 'funcnames'
        },
        'file_handler': {
            'level':LOGLEVEL,
            'class':'logging.handlers.RotatingFileHandler',
            'formatter': 'funcnames',
            'filename': f'log/{__release__}.log',
            'maxBytes': 10485760, # 10MB
            'backupCount': 20,
        },
        # 'rollbar':{
        #     'level':LEVEL,
        #     'class':'rollbar.logger.RollbarHandler',
        #     'formatter': 'funcnames',
        # }
    },
    # 'loggers': {
    #     'urllib3': {
    #         'level': 'ERROR',
    #         'propagate': False,
    #     },
    #     'myproject.custom': {
    #         'handlers': ['console', 'mail_admins'],
    #         'level': 'INFO',
    #         'filters': ['special']
    #     }
    # },
    'root': {
        'level': LOGLEVEL,
        'handlers': ['console', 'file_handler'],
    }
}




def sentry_config():
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    def setup_sentry(
        dsn: str,
        level: int = 10, # debug
        event_level: int = 40, # error
        release: str = __release__

        ):

        sentry_logging = LoggingIntegration(
            level=level, # Capture info and above as breadcrumbs
            event_level=event_level # Send errors as events
        )
        sentry_sdk.init(
            dsn= dsn,
            release = release,
            integrations=[sentry_logging],
            environment = ENV_NAME
        )

    try:
        from src.settings import SENTRY_KEY, SENTRY_EVENT_LEVEL, SENTRY_LEVEL, ENV_NAME
        setup_sentry(SENTRY_KEY, SENTRY_EVENT_LEVEL, SENTRY_LEVEL)
    except Exception as e:
        print(f'Unable to load Sentry configuration from settings. -- {e}')



def standard_config():
    sentry_config()
    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger()
    logger.info(f'Configured loggers (level: {logger.level}): {[x.name for x in logger.handlers]}')


if __name__ == "__main__":

    standard_config()
    logger = logging.getLogger()
    logger.error('test-message')
