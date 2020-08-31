import wx
import json
import os
from CrimpcontactEditorGUI import CrimpcontactEditorGUI


class CrimpcontactEditor(CrimpcontactEditorGUI):
    def __init__(self, parent, *args, **kwds):
        # Don't like this... why has frame a problem with kwds?
        preload = kwds.pop("preload")
        CrimpcontactEditorGUI.__init__(self, parent, *args, **kwds)

        self.data_directory = parent.data_directory
        self.old_contact = ""
        self.xSections = ["0.25", "0.34", "0.50",
                          "0.75", "1.00", "1.50", "2.50",
                          "1.00+1.00", "1.50+1.50", "1.00+1.50"]

        self.fillXSectionBox()
        self.loadCrimpContact(contact=preload)

        self.btnSave.Bind(wx.EVT_BUTTON, self.onSaveClicked)

        self.tcRefNr.Bind(wx.EVT_TEXT, self.onInfoChanged)
        self.tcType.Bind(wx.EVT_TEXT, self.onInfoChanged)
        self.tcProducer.Bind(wx.EVT_TEXT, self.onInfoChanged)
        self.tcProducerNr.Bind(wx.EVT_TEXT, self.onInfoChanged)

        self.cbXSection.Bind(wx.EVT_COMBOBOX, self.onCrosssectionSelected)
        self.cbTool.Bind(wx.EVT_COMBOBOX, self.onToolSelected)
        self.tcSoll.Bind(wx.EVT_TEXT, self.onInfoChanged)
        self.btnAddXSection.Bind(wx.EVT_BUTTON, self.onAddXSectionClicked)
        self.btnDeleteXSection.Bind(wx.EVT_BUTTON, self.onDeleteXSecClicked)
        self.lcCrimptools.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onEntrySelected)
        self.lcCrimptools.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onEntrySelected)

    def onSaveClicked(self, event):
        refNr = self.tcRefNr.GetValue()
        contactType = self.tcType.GetValue()
        producer = self.tcProducer.GetValue()
        producerNr = self.tcProducerNr.GetValue()

        contact = {}
        contact["refNr"] = refNr
        contact["type"] = contactType
        contact["producer"] = producer
        contact["producerNr"] = producerNr
        contact["crosssection"] = {}

        for row in range(self.lcCrimptools.GetItemCount()):
            xs = self.lcCrimptools.GetItem(row, 0).GetText()
            tool = self.lcCrimptools.GetItem(row, 1).GetText()
            slot = self.lcCrimptools.GetItem(row, 2).GetText()
            soll = self.lcCrimptools.GetItem(row, 3).GetText()

            contact["crosssection"][xs] = {}
            contact["crosssection"][xs]["tool"] = tool
            contact["crosssection"][xs]["slot"] = slot
            contact["crosssection"][xs]["soll"] = soll

        self.saveContactInfo(contact)
        self.Close()

    def saveContactInfo(self, contact):
        outfile = os.path.join(self.data_directory, "crimpcontacts.json")

        if not os.path.exists(outfile):
            crimpcontacts = {}
            crimpcontacts[contact["refNr"]] = contact
            with open(outfile, "w") as FSO:
                json.dump(crimpcontacts, FSO)

        else:
            with open(outfile, "r") as FSO:
                crimpcontacts = json.load(FSO)
                if self.old_contact and self.old_contact != contact["refNr"]:
                    crimpcontacts.pop(self.old_contact)

                crimpcontacts[contact["refNr"]] = contact
            with open(outfile, "w") as FSO:
                json.dump(crimpcontacts, FSO)

    def onCrosssectionSelected(self, event):
        xSection = self.cbXSection.GetStringSelection()
        if xSection:
            self.cbTool.Clear()
            self.cbSlot.Clear()
            self.tcSoll.Clear()
            self.fillToolBox()
            self.tcSoll.Enable()
        else:
            self.cbTool.Disable()
            self.cbTool.Clear()
            self.cbSlot.Disable()
            self.cbSlot.Clear()
            self.tcSoll.Disable()
            self.tcSoll.Clear()
        self.onInfoChanged(event)

    def onToolSelected(self, event):
        tool = event.GetEventObject()
        self.fillSlotBox(tool)
        self.onInfoChanged(event)

    def onAddXSectionClicked(self, event):
        xSection = self.cbXSection.GetStringSelection()
        tool = self.cbTool.GetStringSelection()
        slot = self.cbSlot.GetStringSelection()
        soll = self.tcSoll.GetValue()

        for row in range(self.lcCrimptools.GetItemCount()):
            if xSection == self.lcCrimptools.GetItem(row, 0).GetText():
                return

        self.lcCrimptools.Append([xSection, tool, slot, soll])
        self.fillXSectionBox()
        self.cbTool.Clear()
        self.cbSlot.Clear()
        self.tcSoll.Clear()

    def onEntrySelected(self, event):
        if self.lcCrimptools.GetFirstSelected() > -1:
            self.btnDeleteXSection.Enable()
        else:
            self.btnDeleteXSection.Disable()

    def onDeleteXSecClicked(self, event):
        xsID = self.lcCrimptools.GetFirstSelected()
        self.lcCrimptools.DeleteItem(xsID)
        self.onInfoChanged(event)

    def onInfoChanged(self, event):
        infoscreen = []
        infoscreen.append(self.tcRefNr.GetValue())
        infoscreen.append(self.tcType.GetValue())
        infoscreen.append(self.tcProducer.GetValue())
        infoscreen.append(self.tcProducerNr.GetValue())

        completeInfo = []
        for i in infoscreen:
            completeInfo.append(i != "")

        validCrimp = True
        xSection = self.cbXSection.GetStringSelection()
        for row in range(self.lcCrimptools.GetItemCount()):
            if xSection == self.lcCrimptools.GetItem(row, 0).GetText():
                validCrimp = False

        tool = self.cbTool.GetStringSelection()
        slot = self.cbSlot.GetStringSelection()
        soll = self.tcSoll.GetValue()
        if xSection == "" or tool == "" or slot == "" and soll == "":
            validCrimp = False

        if validCrimp:
            self.btnAddXSection.Enable()
        else:
            self.btnAddXSection.Disable()

        if all(completeInfo) and self.lcCrimptools.GetItemCount() > 0:
            self.btnSave.Enable()
        else:
            self.btnSave.Disable()

    def fillXSectionBox(self):
        self.cbXSection.Clear()
        for xs in self.xSections:
            self.cbXSection.Append(xs)

    def fillToolBox(self, selection=""):
        tools = self.loadCrimpTools()
        toolIds = list(tools.keys())
        for toolid in sorted(toolIds):
            self.cbTool.Append(toolid)
        if selection:
            self.cbTool.SetSelection(toolIds.index(selection))
        self.cbTool.Enable()
        return self.cbTool

    def fillSlotBox(self, tool, selection=""):
        slotbox = self.FindWindowById(tool.GetId() + 100)
        slotbox.Clear()
        tools = self.loadCrimpTools()
        slots = list(tools[tool.GetStringSelection()]["Slots"])
        slots.sort()
        for i, s in enumerate(slots):

            awg = "AWG {0}".format(s[0])
            met = u"{0} mm²".format(s[1])

            if s[0] and s[1]:
                slot = " | ".join([awg, met])
            else:
                slot = awg * (s[0] != "") + met * (s[1] != "")

            if slot == selection:
                slotID = i

            slotbox.Append(slot)

        if selection:
            slotbox.SetSelection(slotID)

        slotbox.Enable()

    def loadCrimpTools(self):
        outfile = os.path.join(self.data_directory, "crimptools.json")
        if os.path.exists(outfile):
            with open(outfile, "r") as FSO:
                return json.load(FSO)

    def loadCrimpContact(self, contact=""):
        outfile = os.path.join(self.data_directory, "crimpcontacts.json")
        if os.path.exists(outfile) and contact:
            with open(outfile, "r") as FSO:
                contacts = json.load(FSO)

            self.tcRefNr.SetValue(contacts[contact]["refNr"])
            self.tcType.SetValue(contacts[contact]["type"])
            self.tcProducer.SetValue(contacts[contact]["producer"])
            self.tcProducerNr.SetValue(contacts[contact]["producerNr"])

            self.lcCrimptools.DeleteAllItems()
            crosssections = contacts[contact]["crosssection"]
            for xs in sorted(crosssections.keys()):
                tool = crosssections[xs]["tool"]
                slot = crosssections[xs]["slot"]
                soll = crosssections[xs]["soll"]
                self.lcCrimptools.Append([xs, tool, slot, soll])

            self.old_contact = contact




class MyApp(wx.App):
    def OnInit(self):
        self.CrimpcontactEditor = CrimpcontactEditor(None, wx.ID_ANY, "")
        self.SetTopWindow(self.CrimpcontactEditor)
        self.CrimpcontactEditor.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
