# -*- coding: utf-8 -*-

import os
import logging
import logging.config, yaml


#file_path, file_name = os.path.split(os.path.realpath(__file__))
#path, module_name = os.path.split(file_path)
def setup_logging(default_path='/home/ladmin/.qgis2/python/plugins/gtiffload/logs/logging.yaml',default_level=logging.INFO,
    env_key='LOG_CFG'):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
setup_logging()
logger = logging.getLogger(__name__)
logger.info("                                                               ")
logger.info("***************************************************************")
logger.info("                                                               ")
logger.info("					New run 									")
logger.info("                                                               ")
logger.info("***************************************************************")


def classFactory(iface):
    from gtiffload.plugin import GTiffTools
    return GTiffTools(iface)
