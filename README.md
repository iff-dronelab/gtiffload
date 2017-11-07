# gtiffload Plugin


## WINDOWS USERS:
### Install Python(If not already installed) from
https://www.python.org/downloads/release/python-2714/

### Install Qgis using OS4GEO tool
64 bit http://qgis.org/downloads/QGIS-OSGeo4W-2.18.14-1-Setup-x86_64.exe
32 bit http://qgis.org/downloads/QGIS-OSGeo4W-2.18.14-1-Setup-x86.exe

### Install qgiscommons2 from the repository below using OS4GEO command line tool ONLY
https://github.com/boundlessgeo/lib-qgis-commons.git

Start OS4GEO SHELL
$ cd to_lib-qgis-commons_directory
$ python setup.py install

### Copy Exiftool/exiftool.exe from the gtiffload plugin directory to "C:\" directory

### Install the Exiftool python package provided in the plugin directory  

Start OS4GEO SHELL
$ cd to_gtiffload_plugin_directory
$ cd Exiftool
$ python setup.py install
