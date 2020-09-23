import wx
import json
import os
from SettingsDialogGUI import SettingsDialogGUI


class SettingsDialog(SettingsDialogGUI):
    def __init__(self, parent, *args, **kwds):
        # Don't like this... why has frame a problem with kwds?

        SettingsDialogGUI.__init__(self, parent, *args, **kwds)

        self.data_directory = parent.data_directory
        self.xsec_soll_values = [["0.14", 20, 20],
                                 ["0.25", 35, 40],
                                 ["0.34", 50, 65],
                                 ["0.50", 60, 70],
                                 ["0.75", 80, 90],
                                 ["1.00", 100, 150],
                                 ["1.50", 130, 210],
                                 ["2.50", 200, 320],
                                 ["4.00", 290, 500],
                                 ["6.00", 350, 700],
                                 ["10.0", 500, 950],
                                 ["2x1.00", 200, 300],
                                 ["2x1.50", 260, 420],
                                 ["1.00+1.50", 200, 320]]

        self.loadXsections()
        self.fillXsections()
        self.tcXSection.Bind(wx.EVT_TEXT, self.onXsecChanged)
        self.lcXSections.Bind(wx.EVT_LIST_ITEM_SELECTED,
                              self.onEntrySelected)
        self.lcXSections.Bind(wx.EVT_LIST_ITEM_DESELECTED,
                              self.onEntrySelected)
        self.btnSave.Bind(wx.EVT_BUTTON, self.onSaveClicked)
        self.btnDelete.Bind(wx.EVT_BUTTON, self.onDeleteClicked)
        self.btnApply.Bind(wx.EVT_BUTTON, self.onApplyClicked)

    def onXsecChanged(self, event):
        self.tcSollOpen.SetValue("")
        self.tcSollClosed.SetValue("")
        self.btnSave.SetLabel("Speichern")

        xsec = self.tcXSection.GetValue()
        if self.xsec_exists(xsec) > -1:
            xsec, open_soll, closed_soll = self.get_xsec(xsec)
            self.tcSollOpen.SetValue(str(open_soll))
            self.tcSollClosed.SetValue(str(closed_soll))
            self.btnSave.SetLabel("Ändern")

        if self.tcXSection.GetValue() == "":
            self.btnSave.Disable()
        else:
            self.btnSave.Enable()

    def onEntrySelected(self, event):
        entry_idx = self.lcXSections.GetFirstSelected()
        if entry_idx > -1:
            self.btnDelete.Enable()
            xsec = self.lcXSections.GetItem(entry_idx, 0).GetText()
            open_soll = self.lcXSections.GetItem(entry_idx, 1).GetText()
            closed_soll = self.lcXSections.GetItem(entry_idx, 2).GetText()
            self.tcXSection.SetValue(xsec)
            self.tcSollOpen.SetValue(open_soll)
            self.tcSollClosed.SetValue(closed_soll)
        else:
            self.btnDelete.Disable()

    def onSaveClicked(self, event):
        xsec = self.tcXSection.GetValue()
        open_soll = self.tcSollOpen.GetValue()
        closed_soll = self.tcSollClosed.GetValue()
        open_soll = int(open_soll) if open_soll else 0
        closed_soll = int(closed_soll) if closed_soll else 0

        index = self.xsec_exists(xsec)
        if index > -1:
            self.xsec_soll_values.pop(index)
        self.xsec_soll_values.append([xsec, open_soll, closed_soll])
        self.xsec_soll_values.sort(key=lambda x: x[1])
        self.fillXsections()
        self.btnApply.Enable()

    def onDeleteClicked(self, event):

        entry_idx = self.lcXSections.GetFirstSelected()
        if entry_idx > -1:
            self.xsec_soll_values.pop(entry_idx)
        self.fillXsections()
        self.btnApply.Enable()

    def onApplyClicked(self, event):
        self.saveXsections()
        self.Close()

    def saveXsections(self):
        settings_path = os.path.join(self.data_directory, "settings.json")
        with open(settings_path, "r") as FSO:
            settings = json.load(FSO)

        settings["xsec_soll_values"] = self.xsec_soll_values
        with open(settings_path, "w") as FSO:
            json.dump(settings, FSO, indent=4)

    def loadXsections(self):
        settings_path = os.path.join(self.data_directory, "settings.json")
        if not os.path.exists(settings_path):
            with open(settings_path, "w") as FSO:
                json.dump({"xsec_soll_values": self.xsec_soll_values},
                          FSO, indent=4)

        with open(settings_path, "r") as FSO:
            self.xsec_soll_values = json.load(FSO)["xsec_soll_values"]
            self.xsec_soll_values.sort(key=lambda x: x[1])

    def fillXsections(self):
        self.btnDelete.Disable()
        self.btnSave.Disable()
        self.lcXSections.DeleteAllItems()
        self.tcXSection.SetValue("")
        self.tcSollOpen.SetValue("")
        self.tcSollClosed.SetValue("")
        for xsec, open_soll, closed_soll in self.xsec_soll_values:
            self.lcXSections.Append([xsec, open_soll, closed_soll])

    def xsec_exists(self, query):
        for i, (xsec, osoll, csoll) in enumerate(self.xsec_soll_values):
            if query == xsec:
                return i
        return -1

    def get_xsec(self, query):
        for xsec, open_soll, closed_soll in self.xsec_soll_values:
            if query == xsec:
                return (xsec, open_soll, closed_soll)
        return ("", "", "")


class MyApp(wx.App):
    def OnInit(self):
        self.SettingsDialog = SettingsDialog(None, wx.ID_ANY, "")
        self.SetTopWindow(self.SettingsDialog)
        self.SettingsDialog.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
