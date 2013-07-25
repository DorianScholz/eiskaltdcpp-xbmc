# -*- coding: utf-8 -*-

import sys
import xbmc
import xbmcgui
from repeater import Repeater
from eiskaltdcpp import EiskaltDCPP

_ = sys.modules['__main__'].__language__
__settings__ = sys.modules['__main__'].__settings__

KEY_MENU_ID = 92

EXIT_SCRIPT = (6, 10, 247, 275, 61467, 216, 257, 61448,)
CANCEL_DIALOG = EXIT_SCRIPT + (216, 257, 61448,)


class GUI(xbmcgui.WindowXMLDialog):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, bforeFallback=0):
        self.transferListItems = {}
        self.transfers = {}
        self.repeater = None
        self.eiskaltdcpp = None

    def onInit(self):
        progressDialog = xbmcgui.DialogProgress()
        progressDialog.create(_(0), _(1))  # 'Transmission', 'Connecting to Transmission'
        params = {
            'host': __settings__.getSetting('rpc_host'),
            'port': __settings__.getSetting('rpc_port')
        }
        try:
            self.eiskaltdcpp = EiskaltDCPP(**params)
        except ValueError as e:
            progressDialog.close()
            self.close()
            message = '%s\n%s' % (_(9002), str(e))  # Invalid config
            if xbmcgui.Dialog().yesno(_(2), message, _(3)):
                __settings__.openSettings()
            return False

        progressDialog.close()

        status = self.eiskaltdcpp.getStatus()
        if status != 'connected':
            self.close()
            message = '%s\n%s' % (_(9002), status)  # Invalid config
            if xbmcgui.Dialog().yesno(_(2), message, _(3)):
                __settings__.openSettings()
            return False

        self.updateTransfers()
        self.repeater = Repeater(1.0, self.updateTransfers)
        self.repeater.start()

    def updateTransfers(self):
        transferListWidget = self.getControl(120)
        transfers = self.eiskaltdcpp.getTransfers()
        for key, transfer in transfers.iteritems():
            statusline = '[%(status)s] %(downloaded)s of %(size)s' % transfer
            if key not in self.transferListItems:
                # Create a new list item
                item = xbmcgui.ListItem(label=transfer['filename'], label2=statusline)
                item.setProperty('transferid', transfer['id'])
                transferListWidget.addItem(item)
                self.transferListItems[key] = item
            else:
                # Update existing list item
                item = self.transferListItems[key]
            self.transfers = transfers
            item.setLabel(transfer['filename'])
            item.setLabel2(statusline)
            item.setProperty('Progress', '%.2f' % transfer['progress'])

        removed = [key for key in self.transferListItems.keys() if key not in transfers.keys()]
        if len(removed) > 0:
            # Clear transfers from the list that have been removed
            for key in removed:
                del self.transferListItems[key]
            transferListWidget.reset()
            for key, item in self.transferListItems.iteritems():
                transferListWidget.addItem(item)
        transferListWidget.setEnabled(bool(transfers))

    def onClick(self, controlID):
        transferListWidget = self.getControl(120)
        if (controlID == 111):
            # Search
            kb = xbmc.Keyboard('', _(202))
            kb.doModal()
            if not kb.isConfirmed():
                return
            search_text = kb.getText()
            progressDialog = xbmcgui.DialogProgress()
            progressDialog.create(_(0), _(290))
            results = self.eiskaltdcpp.search(search_text)
            progressDialog.close()
            if not results:
                xbmcgui.Dialog().ok(_(0), _(291))
                return
            result_list = ['[%(count)s] %(filename)s %(size)s' % item for item in results]
            selected = xbmcgui.Dialog().select(_(0), result_list)
            if selected < 0:
                return
            self.eiskaltdcpp.addDownload(results[selected])

        elif (controlID == 112):
            # Remove selected transfer
            item = transferListWidget.getSelectedItem()
            if item and xbmcgui.Dialog().yesno(_(0), 'Remove \'%s\'?' % self.transfers[item.getProperty('transferid')]['filename']):
                self.eiskaltdcpp.removeTransfer(item.getProperty('transferid'))

        if (controlID == 117):
            # Exit button
            self.close()

        if (controlID == 120):
            # A transfer was chosen, TODO: show details
            item = transferListWidget.getSelectedItem()
            #infoGui = TransferInfoGUI('script-eiskaltdcpp-details.xml', __settings__.getAddonInfo('path'), 'Default')
            #infoGui.setTransfer(self.eiskaltdcpp, item.getProperty('transferid'))
            #infoGui.doModal()
            #del infoGui

    def onFocus(self, controlID):
        pass

    def onAction(self, action):
        if (action.getButtonCode() in CANCEL_DIALOG) or (action.getId() == KEY_MENU_ID):
            self.close()

    def close(self):
        if self.repeater:
            self.repeater.stop()
        super(GUI, self).close()
