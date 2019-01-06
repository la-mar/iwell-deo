

import logging
import os
import sys
from datetime import datetime

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

import src.controller
from src.log import setup_logging
from src.sentry import setup_sentry
from src.settings import LOG_CONFIG_PATH, SENTRY_KEY
from src.version import __tag__



def main():

    # Configure logging module
    setup_logging(LOG_CONFIG_PATH)
    logger = logging.getLogger(__tag__)

    setup_sentry(SENTRY_KEY, release =  __tag__)
    logger.info(f'Sentry configured: {__tag__}')


    try:
        src.controller.integrate()

    except Exception as e:
        logger.exception(f'{__tag__} exited abnormally. -- Error: {e}')


    logger.info('Finished')



if __name__ == "__main__":
    main()
