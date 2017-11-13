# -*- coding: utf-8 -*-

import os
import logging
import logging.config, yaml


logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.realpath(__file__)),"logs","info.log"),
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)

logger = logging.getLogger(__name__)
logger.info("***************************************************************")
logger.info("					New QGIS run 								")
logger.info("***************************************************************")


def classFactory(iface):
    from gtiffload.plugin import GTiffTools
    return GTiffTools(iface)
