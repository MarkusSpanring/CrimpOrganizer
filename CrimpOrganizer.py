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
from SettingsDialog import SettingsDialog


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

        self.tcSearchContact.Bind(wx.EVT_TEXT, self. onSearchChanged)

        self.lcContacts.Bind(wx.EVT_LIST_ITEM_SELECTED,
                             self.onContactSelected)
        self.lcContacts.Bind(wx.EVT_LIST_ITEM_DESELECTED,
                             self.onContactSelected)
        self.lcContacts.Bind(wx.EVT_LIST_ITEM_ACTIVATED,
                             self.onEditContactClicked)
        self.lcContacts.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,
                             self.onContactRClicked)

        self.lcToolSummary.Bind(wx.EVT_LIST_ITEM_SELECTED,
                                self.onToolSelected)
        self.lcToolSummary.Bind(wx.EVT_LIST_ITEM_DESELECTED,
                                self.onToolSelected)
        self.lcToolSummary.Bind(wx.EVT_LIST_ITEM_ACTIVATED,
                                self.onUseToolsClicked)
        self.lcToolSummary.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,
                                self.onToolsRClicked)

        self.lcCrimpInstructions.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,
                                      self.onInstructionRClicked)

        self.btnCreateInstructions.Bind(wx.EVT_BUTTON, self.onCreateClicked)
        self.tcSchemeNr.Bind(wx.EVT_TEXT, self.onSchemeNrChanged)
        self.tcSchemeRev.Bind(wx.EVT_TEXT, self.onSchemeNrChanged)

        self.treeInstructions.Bind(wx.EVT_TREE_SEL_CHANGED,
                                   self.treeItemSelected)
        self.treeInstructions.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK,
                                   self.treeItemRClicked)

        self.optFile.Bind(wx.EVT_MENU, self.onSettingsClicked)
        self.optOrder.Bind(wx.EVT_MENU, self.onOpenOrdersClicked)

        self.btnNewContact.Bind(wx.EVT_BUTTON, self.onNewContactClicked)
        self.btnManageTools.Bind(wx.EVT_BUTTON, self.onManageToolsClicked)



        settings_path = os.path.join(self.data_directory, "settings.json")
        if not os.path.exists(settings_path):
            self.onSettingsClicked(None)

    def onCrimpContactsClicked(self, event):
        print(event.GetId())
        event.Skip()

    def onSettingsClicked(self, event):
        self.SettingsDialog = SettingsDialog(self)
        # self.SettingsDialog.Bind(wx.EVT_CLOSE, self.onContactsAnnotated)
        self.SettingsDialog.Show()

    def onOpenOrdersClicked(self, event):
        print("order")
        event.Skip()

    def onContactRClicked(self, event):
        contactID = self.lcContacts.GetFirstSelected()
        if contactID == -1:
            return
        menus = [(wx.NewIdRef(count=1), "Bearbeiten",
                  self.onEditContactClicked),
                 (wx.NewIdRef(count=1), u"Löschen",
                  self.onDeleteContactClicked)]

        popup_menu = wx.Menu()
        for menu in menus:
            if menu is None:
                popup_menu.AppendSeparator()
                continue
            popup_menu.Append(menu[0], menu[1])
            self.Bind(wx.EVT_MENU, menu[2], id=menu[0])

        self.PopupMenu(popup_menu, self.ScreenToClient(wx.GetMousePosition()))
        popup_menu.Destroy()
        return

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
            self.lcToolSummary.DeleteAllItems()
            contact = self.crimpcontacts[contactRef]
            for xs in sorted(contact["crosssection"].keys()):
                slot = contact["crosssection"][xs]["slot"]
                tool = contact["crosssection"][xs]["tool"]
                IDs = ", ".join(self.crimptools[tool]["IDs"])
                self.lcToolSummary.Append([xs, IDs, slot])

        else:
            self.lcToolSummary.DeleteAllItems()

    def onToolSelected(self, event):
        self.selected_instruction = []
        if self.lcToolSummary.GetFirstSelected() > -1:

            contactID = self.lcContacts.GetFirstSelected()
            contactRef = self.lcContacts.GetItem(contactID, 0).GetText()

            sel = self.lcToolSummary.GetNextSelected(-1)
            while sel > -1:
                xs = self.lcToolSummary.GetItem(sel, 0).GetText()
                instruction_key = "#".join([xs, contactRef])
                if instruction_key not in self.full_instructions:
                    self.selected_instruction.append(instruction_key)

                sel = self.lcToolSummary.GetNextSelected(sel)

    def onToolsRClicked(self, event):
        selTools = self.lcToolSummary.GetFirstSelected()
        if selTools == -1:
            return
        menus = [(wx.NewIdRef(count=1), u"Hinzufügen",
                  self.onUseToolsClicked)]

        popup_menu = wx.Menu()
        for menu in menus:
            if menu is None:
                popup_menu.AppendSeparator()
                continue
            popup_menu.Append(menu[0], menu[1])
            self.Bind(wx.EVT_MENU, menu[2], id=menu[0])

        self.PopupMenu(popup_menu, self.ScreenToClient(wx.GetMousePosition()))
        popup_menu.Destroy()
        return

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

            for instruction in self.full_instructions:
                xs, contact = instruction.split("#")
                pos = self.full_instructions[instruction]["pos"]
                name = self.full_instructions[instruction]["name"]
                info = [pos, contact, xs, name]
                self.lcCrimpInstructions.Append(info)

            schemeNr = self.tcSchemeNr.GetValue() != ""
            schemeRev = self.tcSchemeRev.GetValue() != ""
            nameGiven = all([schemeNr, schemeRev])
            if self.lcCrimpInstructions.GetItemCount() > 0 and nameGiven:
                self.btnCreateInstructions.Enable()
            else:
                self.btnCreateInstructions.Disable()

        event.Skip()

    def onInstructionRClicked(self, event):
        selContact = self.lcCrimpInstructions.GetFirstSelected()
        if selContact == -1:
            return
        menus = [(wx.NewIdRef(count=1), u"Kontakt entfernen",
                  self.onRemoveInstructionClicked)]

        popup_menu = wx.Menu()
        for menu in menus:
            if menu is None:
                popup_menu.AppendSeparator()
                continue
            popup_menu.Append(menu[0], menu[1])
            self.Bind(wx.EVT_MENU, menu[2], id=menu[0])

        self.PopupMenu(popup_menu, self.ScreenToClient(wx.GetMousePosition()))
        popup_menu.Destroy()
        return

    def onRemoveInstructionClicked(self, event):
        instruction_id = self.lcCrimpInstructions.GetFirstSelected()
        contact = self.lcCrimpInstructions.GetItem(instruction_id, 1).GetText()
        xs = self.lcCrimpInstructions.GetItem(instruction_id, 2).GetText()
        entry = "#".join([xs, contact])
        self.lcCrimpInstructions.DeleteAllItems()
        self.full_instructions.pop(entry)

        for instruction in self.full_instructions:
            xs, contact = instruction.split("#")
            pos = self.full_instructions[instruction]["pos"]
            name = self.full_instructions[instruction]["name"]
            info = [pos, contact, xs, name]
            self.lcCrimpInstructions.Append(info)

        if self.lcCrimpInstructions.GetItemCount() > 0:
            self.btnCreateInstructions.Enable()
        else:
            self.btnCreateInstructions.Disable()

    def onReannotateClicked(self, event):
        self.selected_instruction = []
        for instruction in self.full_instructions.keys():
            self.selected_instruction.append(instruction)

        identifiers = self.full_instructions.keys()
        self.AnnotateContacts = AnnotateContacts(self, identifiers=identifiers)
        self.AnnotateContacts.Bind(wx.EVT_CLOSE, self.onContactsAnnotated)
        self.AnnotateContacts.Show()

    def onDeleteSchemeClicked(self, event):
        schemeNr = self.tcSchemeNr.GetValue()
        schemeRev = self.tcSchemeRev.GetValue()

        scheme = "-".join([schemeNr, schemeRev]) + ".json"
        folder = os.path.join(self.data_directory, "data", "instructions")
        filename = os.path.join(folder, scheme)

        if os.path.exists(filename):
            msg = 'Really?! Soll die Anweisung für'
            msg += ' "{0}-{1}" '.format(schemeNr, schemeRev)
            msg += 'unwiderruflich gelöscht werden?'
            response = wx.MessageBox(msg, 'Info', wx.YES_NO | wx.ICON_WARNING)
            if response == wx.YES:
                os.remove(filename)
                self.tcSchemeNr.SetValue("")
                self.tcSchemeRev.SetValue("")
                self.lcCrimpInstructions.DeleteAllItems()
                self.fillCrimpInstructions()
                self.full_instructions = {}

    def onSchemeNrChanged(self, event):
        schemeNr = self.tcSchemeNr.GetValue() == ""
        schemeRev = self.tcSchemeRev.GetValue() == ""
        self.fillCrimpInstructions(searchpattern=self.tcSchemeNr.GetValue())
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
        self.saveCrimpInstructions(scheme, self.OrderDetails.override)
        if self.OrderDetails.details_given:
            protocolNr = details[2]
            outdir = os.path.join(self.data_directory, "data",
                                  "orders", protocolNr)
            if not os.path.exists(outdir):
                os.makedirs(outdir)

            details.append(scheme)
            pdfcreator = CrimpInstructionPDF(outdir=outdir,
                                             outfile="{0}.pdf".format(scheme))
            pdfcreator.createPDF(order_details=details,
                                 instructions=self.buildInstructions())

            pdfcreator.showPDF()

        event.Skip()

    def buildInstructions(self):
        instructions = copy.deepcopy(self.full_instructions)
        for entry in self.full_instructions:
            xs, contactRef = entry.split("#")
            contact = self.crimpcontacts[contactRef]
            instructions[entry]["series"] = contact["series"]
            instructions[entry]["producer"] = contact["producer"]

            slot = contact["crosssection"][xs]["slot"]
            soll = contact["crosssection"][xs]["soll"]
            instructions[entry]["slot"] = splitReadableSlot(slot)
            instructions[entry]["soll"] = soll

            tool = contact["crosssection"][xs]["tool"]
            IDs = self.crimptools[tool]["IDs"]
            instructions[entry]["IDs"] = IDs

            producer = self.crimptools[tool]["producer"]
            instructions[entry]["producer"] = producer
        return instructions

    def treeItemRClicked(self, event):
        schemeNr = self.tcSchemeNr.GetValue()
        schemeRev = self.tcSchemeRev.GetValue()
        scheme = "-".join([schemeNr, schemeRev]) + ".json"
        folder = os.path.join(self.data_directory, "data", "instructions")
        filename = os.path.join(folder, scheme)
        if not os.path.exists(filename):
            return

        menus = [(wx.NewIdRef(count=1), u"Zeichnung löschen",
                  self.onDeleteSchemeClicked),
                 (wx.NewIdRef(count=1), u"Pos./Gehäuse neu zuweisen",
                  self.onReannotateClicked)]

        popup_menu = wx.Menu()
        for menu in menus:
            popup_menu.Append(menu[0], menu[1])
            self.Bind(wx.EVT_MENU, menu[2], id=menu[0])

        self.PopupMenu(popup_menu, self.ScreenToClient(wx.GetMousePosition()))
        popup_menu.Destroy()
        return

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
                xs, contact = instruction.split("#")
                pos = instructions[instruction]["pos"]
                name = instructions[instruction]["name"]
                info = [pos, contact, xs, name]
                self.lcCrimpInstructions.Append(info)

            self.full_instructions = copy.deepcopy(instructions)
        else:
            self.full_instructions = {}
            self.tcSchemeNr.SetValue("")
            self.tcSchemeRev.SetValue("")

    def fillContacts(self, searchpattern=""):
        contacts = list(self.crimpcontacts.keys())
        contacts.sort()
        self.lcContacts.DeleteAllItems()
        for contact in contacts:
            producer = self.crimpcontacts[contact]["producer"]
            series = self.crimpcontacts[contact]["series"]

            searchresult = any([searchpattern.lower() in contact.lower(),
                                searchpattern.lower() in producer.lower(),
                                searchpattern.lower() in series.lower()
                                ])
            if searchresult:
                self.lcContacts.Append([contact, producer, series])

    # This has to go in a separate class
    # It is redundant
    def loadCrimptools(self):
        outfile = self.getFullPath("crimptools.json")
        if os.path.exists(outfile):
            with open(outfile, "r") as FSO:
                return json.load(FSO)

    def loadCrimpcontacts(self):
        outfile = self.getFullPath("crimpcontacts.json")
        if os.path.exists(outfile):
            with open(outfile, "r") as FSO:
                return json.load(FSO)
        return {}

    def saveCrimpcontacts(self):
        outfile = self.getFullPath("crimpcontacts.json")
        if os.path.exists(outfile):
            with open(outfile, "w") as FSO:
                json.dump(self.crimpcontacts, FSO)

    def getFullPath(self, file):
        folder = file.replace(".json", "")
        outdir = os.path.join(self.data_directory, "data", folder)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        return os.path.join(outdir, file)

    def fillCrimpInstructions(self, init=False, searchpattern=""):
        instructions = self.loadCrimpInstructions()
        self.treeInstructions.DeleteAllItems()
        root = self.treeInstructions.AddRoot("Crimpanweisungen")
        found_match = False
        for schemeNr in sorted(list(instructions.keys())):
            if searchpattern and (searchpattern not in schemeNr):
                continue
            elif searchpattern and (searchpattern in schemeNr):
                found_match = True
            nr = self.treeInstructions.AppendItem(root, schemeNr)
            for schemeRev in sorted(list(instructions[schemeNr].keys())):
                rev = self.treeInstructions.AppendItem(nr, schemeRev)
                data = instructions[schemeNr][schemeRev]
                self.treeInstructions.SetItemData(rev, data)
        if found_match:
            self.treeInstructions.ExpandAll()
        else:
            self.treeInstructions.Expand(root)

    def loadCrimpInstructions(self):
        outdir = os.path.join(self.data_directory, "data", "instructions")
        instructions = {}
        if os.path.exists(outdir):
            for d in os.listdir(outdir):
                schemeNr, schemeRev = d.replace(".json", "").split("-")
                if schemeNr not in instructions:
                    instructions[schemeNr] = {}
                with open(os.path.join(outdir, d), "r") as FSO:
                    instructions[schemeNr][schemeRev] = json.load(FSO)
        return instructions

    def saveCrimpInstructions(self, scheme, override=False):
        outdir = os.path.join(self.data_directory, "data", "instructions")
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        outfile = os.path.join(outdir, "{0}.json".format(scheme))
        response = wx.NO
        if not os.path.exists(outfile):
            msg = '"{0}" ist eine neue Zeichnung. '.format(scheme)
            msg += 'Soll sie gespeichert werden?'
            btns = wx.YES_NO | wx.ICON_INFORMATION | wx.CANCEL
            dial = wx.MessageDialog(None, msg, 'Info', btns)
            response = dial.ShowModal()
        if (response == wx.ID_YES or override) and self.full_instructions:
            with open(outfile, "w") as FSO:
                json.dump(self.full_instructions, FSO, indent=4)
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
