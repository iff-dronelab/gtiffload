from __future__ import absolute_import
from builtins import object
# -*- coding: utf-8 -*-
from osgeo import gdal, osr

import exiftool
import os, time, webbrowser, threading, logging, math


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
        self.logger = logging.getLogger(__name__)
        self.logger.info("GDAL version in this QGIS is: " + gdal.__version__)
        self.iface = iface
        self.mapTool = None
        self.doAdd = False
        self.total_image_list = []
        self.new_image_list = []
        self.counter = 0
        self.start_time = time.time()
        readSettings()
        self.camera = pluginSetting("camera")
        self.image_path = pluginSetting("gtifPath")
        self.gtif_path = pluginSetting("gtifoutPath")
        self.trans_path = pluginSetting("translatedPath")
        self.refreshInterval = pluginSetting("refreshInterval")
        self.out_format = pluginSetting("out_format")

        self.logger.info("Input Images Path: " + self.image_path)
        self.logger.info("Trans Images Path: " + self.trans_path)
        self.logger.info("Warped Images Path: " + self.gtif_path)
        self.logger.info("Refresh Interval: " + str(self.refreshInterval) )
        self.logger.info("Camera is: " + str(self.camera) )

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
        self.logger.info('Removing the images.')

        addedLayers = self.iface.legendInterface().layers()
        self.logger.info('Number of Raster Layers to remove are: ' + str(len(addedLayers)))
        for layer in addedLayers:
            if "QgsRasterLayer" in str(layer) :
                QgsMapLayerRegistry.instance().removeMapLayers([layer.id()])
        self.total_image_list = []
        self.new_image_list = []
        self.counter = 0

    def getNewImages(self):
        self.logger.info("Getting New Images.")

        self.image_path = pluginSetting("gtifPath")
        self.gtif_path = pluginSetting("gtifoutPath")
        self.trans_path = pluginSetting("translatedPath")
        self.camera = pluginSetting("camera")
        self.out_format=pluginSetting("out_format")

        self.logger.info("Input Images Path: " + self.image_path)
        self.logger.info("Trans Images Path: " + self.trans_path)
        self.logger.info("Warped Images Path: " + self.gtif_path)
        self.logger.info("Camera is: " + str(self.camera) )
        self.logger.info("Out format is: " + str(self.out_format) )



        if not os.path.exists(self.gtif_path):
            self.logger.info("Output Path does not exist. Trying to create it.")
            os.makedirs(self.gtif_path)
            self.logger.info("Output Path created.")
        if not os.path.exists(self.trans_path):
            self.logger.info("Translated Image Path does not exist. Trying to create it.")
            os.makedirs(self.trans_path)
            self.logger.info("Translated Image Path created.")
        tmp_list = []
        
        img_extensions = [".tif",".tiff","TIFF","TIF", ".jpg", ".jpeg", ".JPG", ".JPEG"]
        for filename in os.listdir(self.image_path):
            if filename.endswith(tuple(img_extensions)):
                item = os.path.join(self.image_path, filename)
                self.logger.info("Adding image to list."+item)
                tmp_list.append( item )
        self.new_image_list = list(set(tmp_list) - set(self.total_image_list))
        self.total_image_list = tmp_list
        self.logger.info("Getting Unique Images List. It contains "+ str(len(self.new_image_list)) +" new images")
        for src in self.new_image_list:
            self.logger.info("Processing image: "+src)
            self.counter = self.counter+1

            t_ext='.tif'
            t_format = 'GTiff'
            creationOptions = ['COMPRESS=JPEG']
    
            
            dst=os.path.join(self.trans_path, 'trans_'+str(self.counter)+t_ext)
            warp_dst=os.path.join(self.gtif_path, 'rot_'+str(self.counter)+t_ext)
            t1=time.time()
            gcpList = self.getExifData(src)
            t2=time.time()
            ds=gdal.Open(src)
            t3=time.time()

            if self.camera=="DJI P4P":
                ds=gdal.Translate(dst, ds, outputSRS = 'EPSG:4326', GCPs = gcpList,creationOptions = creationOptions, width = 684, height = 456, format = t_format)
            elif self.camera=="DJI P4" or self.camera=="DJI MAVIC" or self.camera=="DJI SPARK":
                ds=gdal.Translate(dst, ds, outputSRS = 'EPSG:4326', GCPs = gcpList,creationOptions = creationOptions, width = 640, height = 480, format = t_format)
            else:
                ds=gdal.Translate(dst, ds, outputSRS = 'EPSG:4326', GCPs = gcpList,creationOptions = creationOptions, format = t_format)
            t4=time.time()

            ds1=gdal.Warp(warp_dst,ds, creationOptions = ['COMPRESS=JPEG'], format = 'GTiff', resampleAlg = gdal.GRIORA_NearestNeighbour, tps=True, dstNodata = 0)
            ds1 = None
            if self.out_format=='mbtiles':
                warp_dst2 = os.path.join(self.gtif_path, 'rot_'+str(self.counter)+'.mbtiles')
                cm='gdal_translate -of MBTiles '+warp_dst + ' ' + warp_dst2
                self.logger.info(cm)
                gdal.Translate(warp_dst2, warp_dst, format = 'MBTiles')
                gdal.Warp(warp_dst2,warp_dst2,format = 'MBTiles', dstNodata = "0 0 0 0")            

            t5=time.time()
            if self.out_format=='mbtiles':
                self.iface.addRasterLayer(warp_dst2)
            else:
                self.iface.addRasterLayer(warp_dst)
            t6=time.time()
            self.logger.info("Time Profile:   ReadExif  Open  Translate  Warp LoadQgis" )
            self.logger.info("             "+ str(t2-t1) + "   "+ str(t3-t2) +"   "+ str(t4-t3) +"   "+ str(t5-t4) +"   "+ str(t6-t5) )

    def setTool(self):
        self._showMessage('Loading the images Continuosly.')
        self.logger.info("Loading the images Continuosly.")
        self.refreshInterval = pluginSetting("refreshInterval")
        self.doAdd = True
        while self.doAdd:
            if time.time()-self.start_time >= self.refreshInterval:
                self.getNewImages()
                self.start_time = time.time()
            QCoreApplication.processEvents()

    def manualSetTool(self):
        self.doAdd = False
        self._showMessage('Loading the images Manually.')
        self.logger.info("Loading the images Manually.")
        self.getNewImages()

    def stopAddingNewImages(self):
        self.doAdd = False
        self._showMessage('Stop Loading the images.')
        self.logger.info("Stop Loading the images.")

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

    def getExifData(self,image_path):
        if self.camera=="FLIR A65":
            ## Camera Const variables for FLIR
            PIXEL_DIM_X=640
            PIXEL_DIM_Y=512
            FOV_X=45.4
            FOV_Y=34.9
        elif self.camera=="DJI P4":
            ## Camera Const variables for FLIR
            PIXEL_DIM_X=640
            PIXEL_DIM_Y=480
            FOV_X=81.7
            FOV_Y=66
        elif self.camera=="DJI P4P":
            ## Camera Const variables for FLIR
            PIXEL_DIM_X=684
            PIXEL_DIM_Y=456
            FOV_X=73.7
            FOV_Y=53.1
        elif self.camera=="DJI MAVIC":
            ## Camera Const variables for FLIR
            PIXEL_DIM_X=640
            PIXEL_DIM_Y=480
            FOV_X=67.3
            FOV_Y=53.1
        elif self.camera=="DJI SPARK":
            ## Camera Const variables for FLIR
            PIXEL_DIM_X=640
            PIXEL_DIM_Y=480
            FOV_X=69.4
            FOV_Y=54.9

    	## Read the required EXIF Tags from the files
    	with exiftool.ExifTool() as et:
    	    LONG_CENTER = et.get_tag("GPSLongitude", image_path)
    	    LAT_CENTER  = et.get_tag("GPSLatitude", image_path)
            if self.camera=="FLIR A65":
                ALTITUDE    = et.get_tag("GPSAltitude", image_path) # They have put relative alt in gps alt
                HEADING = et.get_tag("GPSImgDirection", image_path)
            elif self.camera=="DJI P4P" or self.camera=="DJI P4" or self.camera=="DJI MAVIC" or self.camera=="DJI SPARK":
                ALTITUDE    = et.get_tag("RelativeAltitude", image_path) # They have put relative alt in gps alt
                HEADING = et.get_tag("FlightYawDegree",image_path)

    	    meterPerLongDegree = math.cos(LAT_CENTER * (-math.pi/180) ) * 111321
    	    meterPerLatDegree  = 111600
    	    GROUND_WIDTH_OF_IMAGE  = 2 * float(ALTITUDE) * math.tan(FOV_X*(math.pi/180)/2)
    	    GROUND_HEIGHT_OF_IMAGE = 2 * float(ALTITUDE) * math.tan(FOV_Y*(math.pi/180)/2)
    	    x0 = LONG_CENTER
    	    y0 = LAT_CENTER
    	    ANGLE = float(HEADING) * (-math.pi/180)
    	    DX = GROUND_WIDTH_OF_IMAGE / 2
    	    DY = GROUND_HEIGHT_OF_IMAGE / 2

    	    x1d = (-DX * math.cos(ANGLE) - DY * math.sin(ANGLE)   ) / meterPerLongDegree  + x0
    	    y1d = (-DX * math.sin(ANGLE) + DY * math.cos(ANGLE)   ) / meterPerLatDegree   + y0
    	    x2d = (DX  * math.cos(ANGLE) - DY * math.sin(ANGLE)   ) / meterPerLongDegree  + x0
    	    y2d = (DX  * math.sin(ANGLE) + DY * math.cos(ANGLE)   ) / meterPerLatDegree   + y0
    	    x3d = (-DX * math.cos(ANGLE) + DY * math.sin(ANGLE)   ) / meterPerLongDegree  + x0
    	    y3d = (-DX * math.sin(ANGLE) - DY * math.cos(ANGLE)   ) / meterPerLatDegree   + y0
    	    x4d = (DX  * math.cos(ANGLE) + DY * math.sin(ANGLE)   ) / meterPerLongDegree  + x0
    	    y4d = (DX  * math.sin(ANGLE) - DY * math.cos(ANGLE)   ) / meterPerLatDegree   + y0
            #self._showMessage("GCP1"+str(x1d)+","+str(y1d))
    	    gcpList = [gdal.GCP(x1d,y1d,0,0), gdal.GCP(x2d,y2d,0,PIXEL_DIM_X,0), gdal.GCP(x3d,y3d,0,0,PIXEL_DIM_Y), gdal.GCP(x4d,y4d,0,PIXEL_DIM_X,PIXEL_DIM_Y)]
    	return gcpList
