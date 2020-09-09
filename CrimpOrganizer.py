import wx
import os
import json
import copy
from CrimpOrganizerGUI import CrimpOrganizerGUI
from CrimptoolEditor import CrimptoolEditor
from CrimpcontactEditor import CrimpcontactEditor
from AnnotateContacts import AnnotateContacts
from OrderDetails import OrderDetails
from exporter import CrimpInstructionPDF


class CrimpOrganizer(CrimpOrganizerGUI):
    def __init__(self, *args, **kwds):
        CrimpOrganizerGUI.__init__(self, *args, **kwds)
        self.data_directory = os.getcwd()

        self.crimptools = self.loadCrimptools()
        self.crimpcontacts = self.loadCrimpcontacts()
        self.fillCrimpInstructions(init=True)
        self.selected_instruction = []
        self.full_instructions = {}
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

        self.btnRemoveInstruction.Bind(wx.EVT_BUTTON,
                                       self.onRemoveInstructionClicked)
        self.lcCrimpInstructions.Bind(wx.EVT_LIST_ITEM_SELECTED,
                                      self.onInstructionSelected)
        self.lcCrimpInstructions.Bind(wx.EVT_LIST_ITEM_DESELECTED,
                                      self.onInstructionSelected)

        self.btnCreateInstructions.Bind(wx.EVT_BUTTON, self.onCreateClicked)
        self.tcSchemeNr.Bind(wx.EVT_TEXT, self.onSchemeNrChanged)
        self.tcSchemeRev.Bind(wx.EVT_TEXT, self.onSchemeNrChanged)

        self.treeInstructions.Bind(wx.EVT_TREE_SEL_CHANGED,
                                   self.treeItemSelected)

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
        self.CrimptoolEditor.Bind(wx.EVT_CLOSE, self.onToolEditorClose)
        self.CrimptoolEditor.Show()

    def onToolEditorClose(self, event):
        self.crimptools = self.loadCrimptools()
        self.fillContacts()
        self.lcToolSummary.DeleteAllItems()
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
                slot = contact["crosssection"][xs]["slot"]
                tool = contact["crosssection"][xs]["tool"]
                IDs = ", ".join(self.crimptools[tool]["IDs"])
                self.lcToolSummary.Append([xs, IDs, slot])

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
        self.selected_instruction = []
        if self.lcToolSummary.GetFirstSelected() > -1:
            self.btnUseTools.Enable()

            contactID = self.lcContacts.GetFirstSelected()
            contactRef = self.lcContacts.GetItem(contactID, 0).GetText()

            sel = self.lcToolSummary.GetNextSelected(-1)
            while sel > -1:
                xs = self.lcToolSummary.GetItem(sel, 0).GetText()
                instruction_key = "#".join([xs, contactRef])
                if instruction_key not in self.full_instructions:
                    self.selected_instruction.append(instruction_key)

                sel = self.lcToolSummary.GetNextSelected(sel)

            if not self.selected_instruction:
                self.btnUseTools.Disable()
        else:
            self.btnUseTools.Disable()

    def onUseToolsClicked(self, event):
        identifiers = self.selected_instruction
        self.AnnotateContacts = AnnotateContacts(self, identifiers=identifiers)
        self.AnnotateContacts.Bind(wx.EVT_CLOSE, self.onContactsAnnotated)
        self.AnnotateContacts.Show()

    def onContactsAnnotated(self, event):
        if self.AnnotateContacts.annotated_data:
            self.lcContacts.Select(-1, 0)
            self.lcToolSummary.Select(-1, 0)
            self.lcToolSummary.DeleteAllItems()
            self.lcCrimpInstructions.DeleteAllItems()

            for entry in self.selected_instruction:
                annotated_data = self.AnnotateContacts.annotated_data[entry]
                self.full_instructions[entry] = annotated_data

                xs, contactRef = entry.split("#")
                contact = self.crimpcontacts[contactRef]
                self.full_instructions[entry]["series"] = contact["series"]
                self.full_instructions[entry]["producer"] = contact["producer"]

                slot = contact["crosssection"][xs]["slot"]
                soll = contact["crosssection"][xs]["soll"]
                self.full_instructions[entry]["slot"] = splitReadableSlot(slot)
                self.full_instructions[entry]["soll"] = soll

                tool = contact["crosssection"][xs]["tool"]
                IDs = self.crimptools[tool]["IDs"]
                self.full_instructions[entry]["IDs"] = IDs

                producer = self.crimptools[tool]["producer"]
                self.full_instructions[entry]["producer"] = producer

            for instruction in self.full_instructions:
                self.lcCrimpInstructions.Append(instruction.split("#"))

            schemeNr = self.tcSchemeNr.GetValue() != ""
            schemeRev = self.tcSchemeRev.GetValue() != ""
            nameGiven = all([schemeNr, schemeRev])
            if self.lcCrimpInstructions.GetItemCount() > 0 and nameGiven:
                self.btnCreateInstructions.Enable()
            else:
                self.btnCreateInstructions.Disable()

        event.Skip()

    def onInstructionSelected(self, event):
        if self.lcCrimpInstructions.GetFirstSelected() > -1:
            self.btnRemoveInstruction.Enable()
        else:
            self.btnRemoveInstruction.Disable()

    def onRemoveInstructionClicked(self, event):
        instruction_id = self.lcCrimpInstructions.GetFirstSelected()
        xs = self.lcCrimpInstructions.GetItem(instruction_id, 0).GetText()
        contact = self.lcCrimpInstructions.GetItem(instruction_id, 1).GetText()
        entry = "#".join([xs, contact])
        self.lcCrimpInstructions.DeleteAllItems()
        self.full_instructions.pop(entry)

        for instruction in self.full_instructions:
            self.lcCrimpInstructions.Append(instruction.split("#"))

        if self.lcCrimpInstructions.GetItemCount() > 0:
            self.btnCreateInstructions.Enable()
        else:
            self.btnCreateInstructions.Disable()
            self.btnRemoveInstruction.Disable()

    def onSchemeNrChanged(self, event):
        schemeNr = self.tcSchemeNr.GetValue() == ""
        schemeRev = self.tcSchemeRev.GetValue() == ""
        if any([schemeNr, schemeRev]):
            self.btnCreateInstructions.Disable()
        else:
            self.btnCreateInstructions.Enable()

    def onCreateClicked(self, event):
        self.OrderDetails = OrderDetails(self)
        self.OrderDetails.Bind(wx.EVT_CLOSE, self.onOrderDetailsGiven)
        self.OrderDetails.Show()

    def onOrderDetailsGiven(self, event):
        schemeNr = self.tcSchemeNr.GetValue()
        schemeRev = self.tcSchemeRev.GetValue()
        scheme = "-".join([schemeNr, schemeRev])
        details = self.OrderDetails.readInfoScreen()
        details.append(scheme)
        pdfcreator = CrimpInstructionPDF()
        pdfcreator.createPDF(order_information=details,
                             instructions=self.full_instructions)

        self.saveCrimpInstructions(scheme)
        event.Skip()

    def treeItemSelected(self, event):
        obj = event.GetEventObject()
        instructions = obj.GetItemData(obj.GetSelection())
        self.lcContacts.Select(-1, 0)
        self.lcToolSummary.Select(-1, 0)
        self.lcToolSummary.DeleteAllItems()
        self.lcCrimpInstructions.DeleteAllItems()
        if instructions is not None:
            parent = obj.GetItemParent(obj.GetSelection())
            schemeNr = obj.GetItemText(parent)
            schemeRev = obj.GetItemText(obj.GetSelection())
            self.tcSchemeNr.SetValue(schemeNr)
            self.tcSchemeRev.SetValue(schemeRev)
            for instruction in instructions:
                self.lcCrimpInstructions.Append(instruction.split("#"))
            self.full_instructions = copy.deepcopy(instructions)
        else:
            self.full_instructions = {}

    def fillContacts(self, searchpattern=""):
        self.btnEditContact.Disable()
        self.btnDeleteContact.Disable()
        contacts = list(self.crimpcontacts.keys())
        contacts.sort()
        self.lcContacts.DeleteAllItems()
        for contact in contacts:
            producer = self.crimpcontacts[contact]["producer"]
            series = self.crimpcontacts[contact]["series"]

            searchresult = any([searchpattern in contact,
                                searchpattern in producer,
                                searchpattern in series
                                ])
            if searchresult:
                self.lcContacts.Append([contact, producer, series])

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

    def fillCrimpInstructions(self, init=False):
        instructions = self.loadCrimpInstructions()
        self.treeInstructions.DeleteAllItems()
        root = self.treeInstructions.AddRoot("Crimpanweisungen")
        for schemeNr in instructions.keys():
            nr = self.treeInstructions.AppendItem(root, schemeNr)
            for schemeRev in instructions[schemeNr].keys():
                rev = self.treeInstructions.AppendItem(nr, schemeRev)

                data = instructions[schemeNr][schemeRev]
                self.treeInstructions.SetItemData(rev, data)
        self.treeInstructions.Expand(root)

    def loadCrimpInstructions(self):
        outdir = os.path.join(self.data_directory, "data", "instructions")
        if os.path.exists(outdir):
            instructions = {}
            for d in os.listdir(outdir):
                schemeNr, schemeRev = d.replace(".json", "").split("-")
                if schemeNr not in instructions:
                    instructions[schemeNr] = {}
                with open(os.path.join(outdir, d), "r") as FSO:
                    instructions[schemeNr][schemeRev] = json.load(FSO)
        return instructions

    def saveCrimpInstructions(self, scheme):
        outdir = os.path.join(self.data_directory, "data", "instructions")
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        outfile = os.path.join(outdir, "{0}.json".format(scheme))

        response = wx.NO
        if not os.path.exists(outfile):
            msg = '"{0}" ist eine neue Zeichnung.'.format(scheme)
            msg += 'Soll sie gespeichert werden?'
            response = wx.MessageBox(msg, 'Info',
                                     wx.YES_NO | wx.ICON_WARNING | wx.CANCEL)

        if response == wx.YES and self.full_instructions:
            with open(outfile, "w") as FSO:
                json.dump(self.full_instructions, FSO)
        self.fillCrimpInstructions()


def splitReadableSlot(slot):
    slot_list = slot.split(" | ")
    if len(slot_list) == 1:
        if "AWG" in slot_list[0]:
            return [slot_list[0].replace("AWG ", ""), ""]
        if u"mm²" in slot_list[0]:
            return ["", slot_list[0].replace(u" mm²", "")]
    slot_list[0] = slot_list[0].replace("AWG ", "")
    slot_list[1] = slot_list[1].replace(u" mm²", "")
    return slot_list


class MyApp(wx.App):
    def OnInit(self):
        self.CrimpOrganizer = CrimpOrganizer(None, wx.ID_ANY, "")
        self.SetTopWindow(self.CrimpOrganizer)
        self.CrimpOrganizer.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
