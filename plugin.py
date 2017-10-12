from __future__ import absolute_import
from builtins import object
# -*- coding: utf-8 -*-

import os, time, webbrowser

from qgis.core import *

from qgis.PyQt.QtCore import (Qt, QFileInfo,QCoreApplication,QEventLoop)
from qgis.PyQt.QtGui import (QIcon, QFileDialog)
from qgis.PyQt.QtWidgets import QAction

from qgis.gui import QgsMessageBar
from qgis.utils import iface

from qgiscommons2.gui import (addAboutMenu, removeAboutMenu, addHelpMenu,removeHelpMenu)
from qgiscommons2.gui.settings import (addSettingsMenu,removeSettingsMenu)
from qgiscommons2.settings import (readSettings,pluginSetting)

class GTiffTools(object):
    def __init__(self, iface):
        self.iface = iface
        self.mapTool = None
        self.doAdd = False
        self.total_image_list = []
        self.new_image_list = []
        self.counter = 0
        self.start_time = time.time()
        readSettings()
        self.image_path = pluginSetting("gtifPath")
        self.refreshInterval = int(pluginSetting("refreshInterval"))

    def initGui(self):
        # Load Images GUI things Manually
        loadImagesManIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "addgtiff.png"))
        self.loadImagesManAction = QAction(loadImagesManIcon, "Load Geotiff Images Manually.", self.iface.mainWindow())
        self.loadImagesManAction.triggered.connect(self.manualSetTool)
        self.iface.addToolBarIcon(self.loadImagesManAction)
        self.iface.addPluginToMenu("geotiffloader", self.loadImagesManAction)

        # Load Images GUI things Continuosly
        loadImagesIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "play.png"))
        self.loadImagesAction = QAction(loadImagesIcon, "Start Loading Geotiff Images Continuosly.", self.iface.mainWindow())
        self.loadImagesAction.triggered.connect(self.setTool)
        self.iface.addToolBarIcon(self.loadImagesAction)
        self.iface.addPluginToMenu("geotiffloader", self.loadImagesAction)

        # Stop Loading Images GUI things
        stopLoadImagesIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "stop.png"))
        self.stopLoadImagesAction = QAction(stopLoadImagesIcon, "Stop Loading Geotiff Images Continuosly.", self.iface.mainWindow())
        self.stopLoadImagesAction.triggered.connect(self.stopAddingNewImages)
        self.iface.addToolBarIcon(self.stopLoadImagesAction)
        self.iface.addPluginToMenu("geotiffloader", self.stopLoadImagesAction)

        # Remove Images GUI Things
        removeImagesIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "removegtiff.png"))
        self.removeImagesAction = QAction(removeImagesIcon, "Remove Geotiff Images.", self.iface.mainWindow())
        self.removeImagesAction.triggered.connect(self.unsetTool)
        self.iface.addToolBarIcon(self.removeImagesAction)
        self.iface.addPluginToMenu("geotiffloader", self.removeImagesAction)

        addSettingsMenu("geotiffloader", self.iface.addPluginToMenu)
        addHelpMenu("geotiffloader", self.iface.addPluginToMenu)
        addAboutMenu("geotiffloader", self.iface.addPluginToMenu)

    def unsetTool(self):
        self.doAdd = False
        self._showMessage('Removing the images.')
        addedLayers = self.iface.legendInterface().layers()
        for layer in addedLayers:
            if "QgsRasterLayer" in str(layer) :
                QgsMapLayerRegistry.instance().removeMapLayers([layer.id()])
        self.total_image_list = []
        self.new_image_list = []
        self.counter = 0

    def getNewImages(self):
        self.image_path = pluginSetting("gtifPath")
        tmp_list = []
        for filename in os.listdir(self.image_path):
            if filename.endswith(".tif"):
                tmp_list.append( os.path.join(self.image_path, filename) )
        self.new_image_list = list(set(tmp_list) - set(self.total_image_list))
        self.total_image_list = tmp_list
        for filename in self.new_image_list:
            self.counter = self.counter+1
            self.iface.addRasterLayer(filename, "image_" + str(self.counter))

    def setTool(self):
        self._showMessage('Loading the images Continuosly.')
        self.refreshInterval = int(pluginSetting("refreshInterval"))
        #time.sleep(1)
        self.doAdd = True
        while self.doAdd:
            if time.time()-self.start_time >= self.refreshInterval:
                self.getNewImages()
                self.start_time = time.time()
            QCoreApplication.processEvents()
    def manualSetTool(self):
        self.doAdd = False
        self._showMessage('Loading the images Manually.')
        self.getNewImages()

    def stopAddingNewImages(self):
        self.doAdd = False

    def unload(self):
        self.doAdd = False
        self.iface.mapCanvas().unsetMapTool(self.mapTool)
        self.iface.removeToolBarIcon(self.loadImagesAction)
        self.iface.removeToolBarIcon(self.loadImagesManAction)
        self.iface.removeToolBarIcon(self.stopLoadImagesAction)
        self.iface.removeToolBarIcon(self.removeImagesAction)


        self.iface.removePluginMenu("geotiffloader", self.loadImagesAction)
        self.iface.removePluginMenu("geotiffloader", self.loadImagesManAction)
        self.iface.removePluginMenu("geotiffloader", self.stopLoadImagesAction)
        self.iface.removePluginMenu("geotiffloader", self.removeImagesAction)

        removeSettingsMenu("geotiffloader")
        removeHelpMenu("geotiffloader")
        removeAboutMenu("geotiffloader")

    def _showMessage(self, message, level=QgsMessageBar.INFO):
        iface.messageBar().pushMessage(message, level, iface.messageTimeout())
