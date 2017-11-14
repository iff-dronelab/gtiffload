# -*- coding: utf-8 -*-

import os, datetime
import logging
import logging.config, yaml

log_path = os.path.join(os.path.dirname(__file__),"logs")

if not os.path.exists(log_path):
	os.makedirs(log_path)

logging.basicConfig(filename=os.path.join(log_path,str(datetime.date.today())+".log"),
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
