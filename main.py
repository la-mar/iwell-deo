
# TODO: Add configuration for complete pull


import logging

import controller
import loggers
from version import __release__

loggers.standard_config()
logger = logging.getLogger(__name__)

def main():

    try:
        controller.integrate()

    except Exception as e:
        logger.exception(f'{__release__} exited abnormally. -- Error: {e}')


    logger.info('Finished')



if __name__ == "__main__":
    main()






