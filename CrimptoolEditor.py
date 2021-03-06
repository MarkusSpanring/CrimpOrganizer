#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Wed Aug 19 19:53:27 2020
#

import wx
import json
import os
from CrimptoolEditorGUI import CrimptoolEditorGUI


class CrimptoolEditor(CrimptoolEditorGUI):
    def __init__(self, parent, *args, **kwds):

        CrimptoolEditorGUI.__init__(self, parent, *args, **kwds)
        self.SetTitle("Crimptool")
        self.defEntry = ["", "--Neue Zange--", ""]
        self.old_ref = ""
        self.crimptools = {}
        self.data_directory = parent.data_directory
        self.loadCrimpInfo()  # Create new file if it does not exist

        self.btnEdit.Bind(wx.EVT_BUTTON, self.onEditClicked)
        self.btnDelete.Bind(wx.EVT_BUTTON, self.onDeleteClicked)
        self.tcSearchTool.Bind(wx.EVT_TEXT, self.onSearchChanged)
        self.btnAddSlot.Bind(wx.EVT_BUTTON, self.onAddSlotClicked)
        self.btnDeleteSlot.Bind(wx.EVT_BUTTON, self.onDeleteSlotClicked)
        self.lcCrimpTools.Bind(wx.EVT_LIST_ITEM_SELECTED,
                               self.onCrimpToolSelected)
        self.lcSlots.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSlotSelected)
        self.lcSlots.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onSlotSelected)

        self.tcProd.Bind(wx.EVT_TEXT, self.onInfoChanged)
        self.tcProdNr.Bind(wx.EVT_TEXT, self.onInfoChanged)
        self.tcSeries.Bind(wx.EVT_TEXT, self.onInfoChanged)
        self.tcAWGSlot.Bind(wx.EVT_TEXT, self.onSlotChanged)
        self.tcMetSlot.Bind(wx.EVT_TEXT, self.onSlotChanged)

        self.tcID.Bind(wx.EVT_TEXT, self.onIdChanged)
        self.btnAddID.Bind(wx.EVT_BUTTON, self.onAddIDClicked)
        self.lbToolIDs.Bind(wx.EVT_LISTBOX, self.onToolIDSelected)
        self.btnRemoveID.Bind(wx.EVT_BUTTON, self.onRemoveIDClicked)

        self.fillCrimpToolBox()

    def onEditClicked(self, event):
        infoscreen = {}
        infoscreen["producer"] = self.tcProd.GetValue()
        infoscreen["producerNr"] = self.tcProdNr.GetValue()
        infoscreen["series"] = self.tcSeries.GetValue()

        ref = "#".join([infoscreen["producer"],
                        infoscreen["series"],
                        infoscreen["producerNr"]])

        if self.btnEdit.GetLabel() == "Bearbeiten":
            self.enableInfoScreen()
            self.old_ref = ref
            self.onInfoChanged(event)

        elif self.btnEdit.GetLabel() == "Speichern":
            rows = self.lcSlots.GetItemCount()
            infoscreen["slots"] = []
            for row in range(rows):
                awg = self.lcSlots.GetItem(itemIdx=row, col=0).GetText()
                met = self.lcSlots.GetItem(itemIdx=row, col=1).GetText()
                infoscreen["slots"].append((awg, met))

            rows = self.lbToolIDs.GetCount()
            infoscreen["IDs"] = []
            for row in range(rows):
                ID = self.lbToolIDs.GetString(row)
                if ID:
                    infoscreen["IDs"].append(ID)

            if self.old_ref and self.old_ref != ref:
                self.crimptools.pop(self.old_ref)
            self.crimptools[ref] = infoscreen

            self.saveCrimpInfo()
            self.disableInfoScreen()
            self.fillCrimpToolBox()
            self.btnEdit.Disable()
            self.old_ref = ""

    def onDeleteClicked(self, event):
        toolId = self.lcCrimpTools.GetFirstSelected()
        producer = self.lcCrimpTools.GetItem(itemIdx=toolId, col=0).GetText()
        crimp = self.lcCrimpTools.GetItem(itemIdx=toolId, col=1).GetText()
        producerNr = self.lcCrimpTools.GetItem(itemIdx=toolId, col=2).GetText()
        toolRef = "#".join([producer, crimp, producerNr])

        if toolRef != self.defEntry:
            self.crimptools.pop(toolRef)
            self.saveCrimpInfo()
            self.clearInfoScreen()
            self.fillCrimpToolBox()
            self.btnEdit.Disable()
            self.btnDelete.Disable()

    def onSearchChanged(self, event):
        searchpattern = self.tcSearchTool.GetValue()
        self.fillCrimpToolBox(searchpattern)

    def onCrimpToolSelected(self, event):
        self.disableInfoScreen()

        toolId = self.lcCrimpTools.GetFirstSelected()
        producer = self.lcCrimpTools.GetItem(itemIdx=toolId, col=0).GetText()
        crimp = self.lcCrimpTools.GetItem(itemIdx=toolId, col=1).GetText()
        producerNr = self.lcCrimpTools.GetItem(itemIdx=toolId, col=2).GetText()
        toolRef = "#".join([producer, crimp, producerNr])
        if toolId == 0:
            self.enableInfoScreen()
            self.clearInfoScreen()
            self.btnEdit.SetLabel("Speichern")
            self.btnDelete.Disable()
            return

        elif toolId != -1:
            self.clearInfoScreen()
            infoscreen = self.crimptools[toolRef]
            self.tcProd.SetValue(infoscreen.get("producer", ""))
            self.tcProdNr.SetValue(infoscreen.get("producerNr", ""))
            self.tcSeries.SetValue(infoscreen.get("series", ""))
            for slot in infoscreen.get("slots", []):
                self.lcSlots.Append(slot)

            for ID in infoscreen.get("IDs", []):
                self.lbToolIDs.Append(ID)
            self.btnEdit.Enable()
            self.btnDelete.Enable()

    def onAddSlotClicked(self, event):
        self.lcSlots.Append([self.tcAWGSlot.GetValue(),
                             self.tcMetSlot.GetValue()])

        self.tcAWGSlot.SetValue("")
        self.tcMetSlot.SetValue("")
        self.onInfoChanged(event)

    def onSlotSelected(self, event):
        slotIdx = self.lcSlots.GetFirstSelected()
        if slotIdx == -1:
            self.btnDeleteSlot.Disable()
        elif slotIdx > -1 and self.lcSlots.IsEnabled():
            self.btnDeleteSlot.Enable()

    def onDeleteSlotClicked(self, event):
        slotIdx = self.lcSlots.GetFirstSelected()
        self.lcSlots.DeleteItem(slotIdx)

        self.onSlotSelected(event)
        self.onInfoChanged(event)

    def onToolIDSelected(self, event):
        if self.lbToolIDs.GetSelection() > -1:
            self.btnRemoveID.Enable()
        else:
            self.btnRemoveID.Disable()

    def onIdChanged(self, event):
        if self.tcID.GetValue() == "":
            self.btnAddID.Disable()
        else:
            self.btnAddID.Enable()

    def onAddIDClicked(self, event):
        newID = self.tcID.GetValue()
        self.lbToolIDs.Append(newID)
        self.tcID.SetValue("")
        self.onInfoChanged(event)

    def onRemoveIDClicked(self, event):
        toolID = self.lbToolIDs.GetSelection()
        self.lbToolIDs.Delete(toolID)
        self.btnRemoveID.Disable()
        self.onInfoChanged(event)

    def onInfoChanged(self, event):
        infoscreen = {}
        infoscreen["producer"] = self.tcProd.GetValue()
        infoscreen["producerNr"] = self.tcProdNr.GetValue()
        infoscreen["series"] = self.tcSeries.GetValue()

        completeInfo = []
        for k in infoscreen.keys():
            completeInfo.append(infoscreen[k] != "")

        completeInfo.append(self.lcSlots.GetItemCount() > 0)
        completeInfo.append(self.lbToolIDs.GetCount() > 0)

        if all(completeInfo):
            self.btnEdit.SetLabel("Speichern")
            self.btnEdit.Enable()
        else:
            self.btnEdit.SetLabel("Bearbeiten")
            self.btnEdit.Disable()

    def onSlotChanged(self, event):
        if self.tcAWGSlot.GetValue() != "" or self.tcMetSlot.GetValue() != "":
            self.btnAddSlot.Enable()
        else:
            self.btnAddSlot.Disable()

    def disableInfoScreen(self):
        self.btnEdit.SetLabel("Bearbeiten")
        self.tcProd.Disable()
        self.tcID.Disable()
        self.lbToolIDs.Disable()
        self.tcProdNr.Disable()
        self.tcSeries.Disable()
        self.tcAWGSlot.Disable()
        self.tcMetSlot.Disable()
        self.lcSlots.Disable()
        self.btnDeleteSlot.Disable()

    def enableInfoScreen(self):
        self.btnEdit.SetLabel("Speichern")
        self.lbToolIDs.Enable()
        self.tcID.Enable()
        self.tcProd.Enable()
        self.tcProdNr.Enable()
        self.tcSeries.Enable()
        self.tcAWGSlot.Enable()
        self.tcMetSlot.Enable()
        self.lcSlots.Enable()

    def clearInfoScreen(self):
        self.tcProd.Clear()
        self.tcProdNr.Clear()
        self.tcSeries.Clear()
        self.tcAWGSlot.Clear()
        self.tcMetSlot.Clear()
        self.lbToolIDs.Clear()
        self.lcSlots.DeleteAllItems()

    def loadCrimpInfo(self):
        outfile = os.path.join(self.getOutdir(), "crimptools.json")
        if not os.path.exists(outfile):
            with open(outfile, "w") as FSO:
                json.dump({}, FSO, indent=4)
            self.crimptools = {}
        else:
            with open(outfile, "r") as FSO:
                self.crimptools = json.load(FSO)

    def saveCrimpInfo(self):
        outfile = os.path.join(self.getOutdir(), "crimptools.json")
        if os.path.exists(outfile):
            with open(outfile, "w") as FSO:
                json.dump(self.crimptools, FSO, indent=4)

    def getOutdir(self):
        outdir = os.path.join(self.data_directory, "data", "crimptools")
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        return outdir

    def fillCrimpToolBox(self, searchpattern=""):
        self.lcCrimpTools.DeleteAllItems()
        self.lcCrimpTools.Append(self.defEntry)

        crimptools = list(self.crimptools.keys())
        for crimptool in sorted(crimptools):
            if searchpattern and searchpattern not in crimptool:
                continue
            self.lcCrimpTools.Append(crimptool.split("#"))


class Crimptool(wx.App):
    def OnInit(self):
        self.Crimptool = CrimptoolEditor(None, wx.ID_ANY, "")
        self.SetTopWindow(self.Crimptool)
        self.Crimptool.Show()
        return True


if __name__ == "__main__":
    app = Crimptool(0)
    app.MainLoop()
