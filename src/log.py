""" Logger definitions """

import os
import logging.config
import yaml
from src.version import __tag__

# logger.debug('debug message')
# logger.info('info message')
# logger.warn('warn message')
# logger.error('error message')
# logger.critical('critical message')

def setup_logging(
    default_path='logging.yaml',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())

        config['handlers']['debug_file_handler']['filename'] \
        = config['handlers']['debug_file_handler']['filename'] \
        .format(project_dir_name = __tag__)



        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

if __name__ == "__main__":
    setup_logging()
    LOG = logging.getLogger(__name__)
    LOG.error('test-message')
