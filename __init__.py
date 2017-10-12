# -*- coding: utf-8 -*-

import os

#file_path, file_name = os.path.split(os.path.realpath(__file__))
#path, module_name = os.path.split(file_path)

def classFactory(iface):
    from gtiffload.plugin import GTiffTools
    return GTiffTools(iface)
