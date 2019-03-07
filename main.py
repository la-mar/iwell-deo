

# TODO: Add configuration for complete pull


import logging

import src.controller
import src.loggers
from src.version import __release__

src.loggers.standard_config()
logger = logging.getLogger(__name__)

def main():


    try:
        src.controller.integrate()

    except Exception as e:
        logger.exception(f'{__release__} exited abnormally. -- Error: {e}')


    logger.info('Finished')



if __name__ == "__main__":
    main()






