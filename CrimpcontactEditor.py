import wx
import json
import os
from CrimpcontactEditorGUI import CrimpcontactEditorGUI


class CrimpcontactEditor(CrimpcontactEditorGUI):
    def __init__(self, parent, *args, **kwds):
        # Don't like this... why has frame a problem with kwds?
        preload = kwds.pop("preload", "")
        CrimpcontactEditorGUI.__init__(self, parent, *args, **kwds)

        self.data_directory = parent.data_directory
        self.old_contact = ""
        self.loadXsectionSollValues()

        self.width, self.height = self.GetSize()
        self.crimptool_alias = {}

        self.crimptools = self.loadCrimpTools()
        self.loadCrimpContact(contact=preload)
        self.fillXSectionBox()

        self.btnSave.Bind(wx.EVT_BUTTON, self.onSaveClicked)

        self.tcRefNr.Bind(wx.EVT_TEXT, self.onInfoChanged)
        self.tcSeries.Bind(wx.EVT_TEXT, self.onInfoChanged)
        self.rbOpenContact.Bind(wx.EVT_RADIOBUTTON, self.onCrimptypeSelected)
        self.rbClosedContact.Bind(wx.EVT_RADIOBUTTON, self.onCrimptypeSelected)
        self.tcProducer.Bind(wx.EVT_TEXT, self.onInfoChanged)
        self.tcProducerNr.Bind(wx.EVT_TEXT, self.onInfoChanged)

        self.cbXSection.Bind(wx.EVT_COMBOBOX, self.onCrosssectionSelected)
        self.cbTool.Bind(wx.EVT_COMBOBOX, self.onToolSelected)
        self.cbSlot.Bind(wx.EVT_COMBOBOX, self.onSlotSelected)
        self.tcSoll.Bind(wx.EVT_TEXT, self.onInfoChanged)
        self.btnAddXSection.Bind(wx.EVT_BUTTON, self.onAddXSectionClicked)
        self.btnDeleteXSection.Bind(wx.EVT_BUTTON, self.onDeleteXSecClicked)
        self.lcCrimptools.Bind(wx.EVT_LIST_ITEM_SELECTED,
                               self.onEntrySelected)
        self.lcCrimptools.Bind(wx.EVT_LIST_ITEM_DESELECTED,
                               self.onEntrySelected)

    def onSaveClicked(self, event):
        refNr = self.tcRefNr.GetValue()
        contactSeries = self.tcSeries.GetValue()
        if self.rbOpenContact.GetValue():
            crimpType = "open"
        if self.rbClosedContact.GetValue():
            crimpType = "closed"

        producer = self.tcProducer.GetValue()
        producerNr = self.tcProducerNr.GetValue()

        contact = {}
        contact["refNr"] = refNr
        contact["series"] = contactSeries
        contact["crimpType"] = crimpType
        contact["producer"] = producer
        contact["producerNr"] = producerNr
        contact["crosssection"] = {}

        for row in range(self.lcCrimptools.GetItemCount()):
            xs = self.lcCrimptools.GetItem(row, 0).GetText()
            tool = self.lcCrimptools.GetItem(row, 1).GetText()
            slot = self.lcCrimptools.GetItem(row, 2).GetText()
            soll = self.lcCrimptools.GetItem(row, 3).GetText()

            contact["crosssection"][xs] = {}
            contact["crosssection"][xs]["tool"] = self.crimptool_alias[tool]
            contact["crosssection"][xs]["slot"] = slot
            contact["crosssection"][xs]["soll"] = soll

        self.saveContactInfo(contact)
        self.Close()

    def onCrimptypeSelected(self, event):
        self.tcSoll.Clear()
        self.onCrosssectionSelected(event)

    def onCrosssectionSelected(self, event):
        xSection = self.cbXSection.GetStringSelection()
        soll_value = ""
        for xs, osoll, csoll in self.xsec_soll_values:
            if xs == xSection:
                if self.rbOpenContact.GetValue():
                    soll_value = str(osoll)
                if self.rbClosedContact.GetValue():
                    soll_value = str(csoll)

        if xSection:
            self.cbTool.Clear()
            self.cbSlot.Clear()
            self.tcSoll.Clear()
            self.fillToolBox()
            self.tcSoll.Enable()
            self.tcSoll.SetValue(soll_value)

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

    def onSlotSelected(self, event):
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
        self.cbTool.Disable()
        self.cbTool.Clear()
        self.cbSlot.Disable()
        self.cbSlot.Clear()
        self.tcSoll.Disable()
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
        self.fillXSectionBox()
        self.btnDeleteXSection.Disable()

    def onInfoChanged(self, event):
        infoscreen = []
        infoscreen.append(self.tcRefNr.GetValue())
        infoscreen.append(self.tcSeries.GetValue())
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
        if xSection == "" or tool == "" or slot == "" or soll == "":
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
        used_xsecs = []
        for row in range(self.lcCrimptools.GetItemCount()):
            used_xsecs.append(self.lcCrimptools.GetItem(row, 0).GetText())

        for xs, osoll, csoll in self.xsec_soll_values:
            if xs not in used_xsecs:
                self.cbXSection.Append(xs)

    def fillToolBox(self, selection=""):
        for tool in sorted(list(self.crimptools.keys())):
            readable = self.getReadableToolName(tool)
            self.cbTool.Append(readable)
        if selection:
            self.cbTool.SetSelection(self.crimptools.index(selection))
        self.cbTool.Enable()
        return self.cbTool

    def fillSlotBox(self, tool, selection=""):
        slotbox = self.FindWindowById(tool.GetId() + 100)
        slotbox.Clear()
        toolRef = self.crimptool_alias[tool.GetStringSelection()]
        slots = list(self.crimptools[toolRef]["slots"])
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
        outfile = self.getAbsPath("crimptools.json")
        if os.path.exists(outfile):
            with open(outfile, "r") as FSO:
                return json.load(FSO)

    def getReadableToolName(self, toolRef):
        toolInfo = self.crimptools[toolRef]
        producer, series, producerNr = toolRef.split("#")

        if len(toolInfo["IDs"]) > 1:
            IDs = "(z.B. {0})".format(", ".join(toolInfo["IDs"]))
        else:
            IDs = "(z.B. {0})".format(toolInfo["IDs"][0])

        readable = "{0} | {1} {2}".format(producer, series, IDs)
        self.crimptool_alias[readable] = toolRef
        return readable

    def saveContactInfo(self, contact):
        outfile = self.getAbsPath("crimpcontacts.json")

        if not os.path.exists(outfile):
            crimpcontacts = {}
            crimpcontacts[contact["refNr"]] = contact
            with open(outfile, "w") as FSO:
                json.dump(crimpcontacts, FSO, indent=4)

        else:
            with open(outfile, "r") as FSO:
                crimpcontacts = json.load(FSO)
                if self.old_contact and self.old_contact != contact["refNr"]:
                    crimpcontacts.pop(self.old_contact)

                crimpcontacts[contact["refNr"]] = contact
            with open(outfile, "w") as FSO:
                json.dump(crimpcontacts, FSO, indent=4)

    def loadCrimpContact(self, contact=""):
        outfile = self.getAbsPath("crimpcontacts.json")
        if os.path.exists(outfile) and contact:
            with open(outfile, "r") as FSO:
                contacts = json.load(FSO)

            self.tcRefNr.SetValue(contacts[contact].get("refNr", ""))
            self.tcSeries.SetValue(contacts[contact].get("series", ""))
            if contacts[contact].get("crimpType", "open") == "open":
                self.rbOpenContact.SetValue(True)
            else:
                self.rbClosedContact.SetValue(True)

            self.tcProducer.SetValue(contacts[contact].get("producer", ""))
            self.tcProducerNr.SetValue(contacts[contact].get("producerNr", ""))

            self.lcCrimptools.DeleteAllItems()
            crosssections = contacts[contact].get("crosssection", {})
            for xs in sorted(crosssections.keys()):
                tool = crosssections[xs]["tool"]
                slot = crosssections[xs]["slot"]
                soll = crosssections[xs]["soll"]
                self.lcCrimptools.Append([xs, self.getReadableToolName(tool),
                                          slot, soll])

            self.old_contact = contact

    def loadXsectionSollValues(self):
        settings_path = os.path.join(self.data_directory, "settings.json")
        if not os.path.exists(settings_path):
            msg = 'Keine Einstellungen gefunden. '
            msg += 'Bitte öffne das Einstellungsmenü.'
            dial = wx.MessageDialog(None, msg, 'Info', wx.OK)
            dial.ShowModal()
            self.Close()

        with open(settings_path, "r") as FSO:
            self.xsec_soll_values = json.load(FSO)["xsec_soll_values"]

    def getAbsPath(self, filename):
        folder = filename.replace(".json", "")
        outdir = os.path.join(self.data_directory, "data", folder)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        return os.path.join(outdir, filename)


class MyApp(wx.App):
    def OnInit(self):
        self.CrimpcontactEditor = CrimpcontactEditor(None, wx.ID_ANY, "")
        self.SetTopWindow(self.CrimpcontactEditor)
        self.CrimpcontactEditor.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
