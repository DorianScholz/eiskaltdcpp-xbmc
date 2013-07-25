# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import xbmcaddon

__scriptname__ = 'EiskaltDC++-XBMC'
__author__ = 'Dorian Scholz'
__url__ = 'https://github.com/DorianScholz/eiskaltdcpp-xbmc'
__svn_url__ = ''
__credits__ = ''
__version__ = '0.1'
__XBMC_Revision__ = '30377'

__settings__ = xbmcaddon.Addon(id='script.eiskaltdcpp')
__language__ = __settings__.getLocalizedString

BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__settings__.getAddonInfo('path'), 'resources', 'lib'))
sys.path.append(BASE_RESOURCE_PATH)

KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

if __name__ == '__main__':
    from gui import GUI
    gui = GUI('script-eiskaltdcpp-main.xml', __settings__.getAddonInfo('path'), 'Default')
    gui.doModal()
    del gui
