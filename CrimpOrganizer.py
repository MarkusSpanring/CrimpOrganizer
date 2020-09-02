import wx
import os
import json
from CrimpOrganizerGUI import CrimpOrganizerGUI
from CrimptoolEditor import CrimptoolEditor
from CrimpcontactEditor import CrimpcontactEditor
from OrderDetails import OrderDetails
from exporter import CrimpInstructionPDF


class CrimpOrganizer(CrimpOrganizerGUI):
    def __init__(self, *args, **kwds):
        CrimpOrganizerGUI.__init__(self, *args, **kwds)
        self.data_directory = os.getcwd()

        self.crimptools = self.loadCrimptools()
        self.crimpcontacts = self.loadCrimpcontacts()
        self.selected_tools = []
        self.use_tools = []
        self.fillContacts()

        self.btnNewContact.Bind(wx.EVT_BUTTON, self.onNewContactClicked)
        self.btnEditContact.Bind(wx.EVT_BUTTON, self.onEditContactClicked)
        self.btnDeleteContact.Bind(wx.EVT_BUTTON, self.onDeleteContactClicked)
        self.tcSearchContact.Bind(wx.EVT_TEXT, self. onSearchChanged)

        self.lcContacts.Bind(wx.EVT_LIST_ITEM_SELECTED,
                             self.onContactSelected)
        self.lcContacts.Bind(wx.EVT_LIST_ITEM_DESELECTED,
                             self.onContactSelected)

        self.btnManageTools.Bind(wx.EVT_BUTTON, self.onManageToolsClicked)
        self.btnUseTools.Bind(wx.EVT_BUTTON, self.onUseToolsClicked)

        self.lcToolSummary.Bind(wx.EVT_LIST_ITEM_SELECTED,
                                self.onToolSelected)
        self.lcToolSummary.Bind(wx.EVT_LIST_ITEM_DESELECTED,
                                self.onToolSelected)

        self.btnRemoveEntry.Bind(wx.EVT_BUTTON, self.onRemoveEntryClicked)
        self.lcUseContacts.Bind(wx.EVT_LIST_ITEM_SELECTED,
                                self.onInstructionSelected)
        self.lcUseContacts.Bind(wx.EVT_LIST_ITEM_DESELECTED,
                                self.onInstructionSelected)

        self.btnCreateInstructions.Bind(wx.EVT_BUTTON, self.onCreateClicked)

    def onNewContactClicked(self, event):
        self.CrimpcontactEditor = CrimpcontactEditor(self, preload="")
        self.CrimpcontactEditor.Bind(wx.EVT_CLOSE, self.onContaktEditorClose)
        self.CrimpcontactEditor.Show()

    def onEditContactClicked(self, event):
        contactID = self.lcContacts.GetFirstSelected()
        contactRef = self.lcContacts.GetItem(contactID, 0).GetText()
        self.CrimpcontactEditor = CrimpcontactEditor(self, preload=contactRef)
        self.CrimpcontactEditor.Bind(wx.EVT_CLOSE, self.onContaktEditorClose)
        self.CrimpcontactEditor.Show()

    def onContaktEditorClose(self, event):
        self.crimpcontacts = self.loadCrimpcontacts()
        self.fillContacts()
        self.lcToolSummary.DeleteAllItems()
        event.Skip()

    def onSearchChanged(self, event):
        self.fillContacts(searchpattern=self.tcSearchContact.GetValue())

    def onManageToolsClicked(self, event):
        self.CrimptoolEditor = CrimptoolEditor(self)
        self.CrimptoolEditor.Bind(wx.EVT_CLOSE, self.onContaktEditorClose)
        self.CrimptoolEditor.Show()

    def onToolEditorClose(self, event):
        event.Skip()

    def onContactSelected(self, event):
        contactID = self.lcContacts.GetFirstSelected()
        if contactID > -1:
            contactRef = self.lcContacts.GetItem(contactID, 0).GetText()
            self.btnEditContact.Enable()
            self.btnDeleteContact.Enable()
            self.lcToolSummary.DeleteAllItems()
            contact = self.crimpcontacts[contactRef]
            for xs in sorted(contact["crosssection"].keys()):
                tool = contact["crosssection"][xs]["tool"]
                slot = contact["crosssection"][xs]["slot"]
                self.lcToolSummary.Append([xs, tool, slot])
        else:
            self.btnEditContact.Disable()
            self.btnDeleteContact.Disable()
            self.btnUseTools.Disable()
            self.lcToolSummary.DeleteAllItems()

    def onDeleteContactClicked(self, event):
        contactID = self.lcContacts.GetFirstSelected()
        contactRef = self.lcContacts.GetItem(contactID, 0).GetText()

        msg = 'Really?! Soll Kontakt "{0}"'.format(contactRef)
        msg += 'unwiderruflich gelöscht werden?'
        response = wx.MessageBox(msg, 'Info', wx.YES_NO | wx.ICON_WARNING)

        if contactID > -1 and response == wx.YES:
            self.crimpcontacts = self.loadCrimpcontacts()
            self.crimpcontacts.pop(contactRef)
            self.saveCrimpcontacts()
            self.fillContacts()

    def onToolSelected(self, event):
        self.selected_tools = []
        if self.lcToolSummary.GetFirstSelected() > -1:
            self.btnUseTools.Enable()

            contactID = self.lcContacts.GetFirstSelected()
            contactRef = self.lcContacts.GetItem(contactID, 0).GetText()

            sel = self.lcToolSummary.GetNextSelected(-1)
            while sel > -1:
                xs = self.lcToolSummary.GetItem(sel, 0).GetText()
                if [xs, contactRef] not in self.use_tools:
                    self.selected_tools.append([xs, contactRef])

                sel = self.lcToolSummary.GetNextSelected(sel)

            if not self.selected_tools:
                self.btnUseTools.Disable()
        else:
            self.btnUseTools.Disable()

    def onUseToolsClicked(self, event):
        self.lcContacts.Select(-1, 0)
        self.lcToolSummary.Select(-1, 0)
        self.lcToolSummary.DeleteAllItems()
        self.lcUseContacts.DeleteAllItems()
        self.use_tools += self.selected_tools

        for tool in self.use_tools:
            self.lcUseContacts.Append(tool)

        if self.lcUseContacts.GetItemCount() > 0:
            self.btnRemoveEntry.Enable()
            self.btnCreateInstructions.Enable()
        else:
            self.btnCreateInstructions.Disable()

    def onInstructionSelected(self, event):
        if self.lcUseContacts.GetFirstSelected() > -1:
            self.btnRemoveEntry.Enable()
        else:
            self.btnRemoveEntry.Disable()

    def onRemoveEntryClicked(self, event):
        entry = self.lcUseContacts.GetFirstSelected()
        self.lcUseContacts.DeleteAllItems()
        self.use_tools.pop(entry)

        for tool in self.use_tools:
            self.lcUseContacts.Append(tool)

        if self.lcUseContacts.GetItemCount() > 0:
            self.btnCreateInstructions.Enable()
        else:
            self.btnCreateInstructions.Disable()
            self.btnRemoveEntry.Disable()

    def onCreateClicked(self, event):
        self.OrderDetails = OrderDetails(self)
        self.OrderDetails.Bind(wx.EVT_CLOSE, self.onOrderDetailsClose)
        self.OrderDetails.Show()

    def onOrderDetailsClose(self, event):
        details = self.OrderDetails.readInfoScreen()
        pdfcreator = CrimpInstructionPDF()
        pdfcreator.createPDF(order=details)
        event.Skip()

    def fillContacts(self, searchpattern=""):
        self.btnEditContact.Disable()
        self.btnDeleteContact.Disable()
        contacts = list(self.crimpcontacts.keys())
        contacts.sort()
        self.lcContacts.DeleteAllItems()
        for contact in contacts:

            producer = self.crimpcontacts[contact]["producer"]
            if searchpattern in contact or searchpattern in producer:
                self.lcContacts.Append([contact, producer])

    def loadCrimptools(self):
        outfile = os.path.join(self.data_directory, "crimptools.json")
        if os.path.exists(outfile):
            with open(outfile, "r") as FSO:
                return json.load(FSO)

    def loadCrimpcontacts(self):
        outfile = os.path.join(self.data_directory, "crimpcontacts.json")
        if os.path.exists(outfile):
            with open(outfile, "r") as FSO:
                return json.load(FSO)
        return {}

    def saveCrimpcontacts(self):
        outfile = os.path.join(self.data_directory, "crimpcontacts.json")
        if os.path.exists(outfile):
            with open(outfile, "w") as FSO:
                json.dump(self.crimpcontacts, FSO)


class MyApp(wx.App):
    def OnInit(self):
        self.CrimpOrganizer = CrimpOrganizer(None, wx.ID_ANY, "")
        self.SetTopWindow(self.CrimpOrganizer)
        self.CrimpOrganizer.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
