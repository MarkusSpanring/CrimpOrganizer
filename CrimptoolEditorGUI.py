#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Wed Sep  2 18:44:12 2020
#

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class CrimptoolEditorGUI(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: CrimptoolEditorGUI.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((959, 660))
        self.SetTitle("CrimptoolEditorGUI")
        
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_2, 0, 0, 0)
        
        self.btnEdit = wx.Button(self.panel_1, wx.ID_ANY, "Bearbeiten")
        self.btnEdit.Enable(False)
        sizer_2.Add(self.btnEdit, 0, wx.ALL, 5)
        
        self.btnDelete = wx.Button(self.panel_1, wx.ID_ANY, u"Löschen")
        self.btnDelete.Enable(False)
        sizer_2.Add(self.btnDelete, 0, wx.ALL, 5)
        
        self.pnlTopSpacer = wx.Panel(self.panel_1, wx.ID_ANY)
        sizer_2.Add(self.pnlTopSpacer, 1, wx.ALL, 5)
        
        static_line_4 = wx.StaticLine(self.panel_1, wx.ID_ANY)
        sizer_1.Add(static_line_4, 0, wx.EXPAND, 0)
        
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)
        
        self.lcCrimpTools = wx.ListCtrl(self.panel_1, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.lcCrimpTools.AppendColumn("Hersteller", format=wx.LIST_FORMAT_LEFT, width=135)
        self.lcCrimpTools.AppendColumn(u"Ausführung", format=wx.LIST_FORMAT_LEFT, width=265)
        self.lcCrimpTools.AppendColumn("Hersteller Nr.", format=wx.LIST_FORMAT_LEFT, width=150)
        sizer_3.Add(self.lcCrimpTools, 1, wx.ALL | wx.EXPAND, 5)
        
        static_line_3 = wx.StaticLine(self.panel_1, wx.ID_ANY, style=wx.LI_VERTICAL)
        static_line_3.SetMinSize((5, 629))
        sizer_3.Add(static_line_3, 0, wx.ALL | wx.EXPAND, 5)
        
        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_4, 0, 0, 0)
        
        stCrimpData = wx.StaticText(self.panel_1, wx.ID_ANY, "Crimpzangendetails")
        stCrimpData.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_4.Add(stCrimpData, 0, wx.ALIGN_CENTER, 0)
        
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_5, 0, 0, 0)
        
        stProd = wx.StaticText(self.panel_1, wx.ID_ANY, "Hersteller:")
        stProd.SetMinSize((90, 16))
        sizer_5.Add(stProd, 0, wx.ALL, 5)
        
        self.tcProd = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcProd.SetMinSize((270, 22))
        self.tcProd.Enable(False)
        sizer_5.Add(self.tcProd, 0, wx.ALL, 5)
        
        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_9, 0, 0, 0)
        
        stType = wx.StaticText(self.panel_1, wx.ID_ANY, "Type:")
        stType.SetMinSize((90, 16))
        sizer_9.Add(stType, 0, wx.ALL, 5)
        
        self.tcType = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcType.SetMinSize((270, 22))
        self.tcType.Enable(False)
        sizer_9.Add(self.tcType, 0, wx.ALL, 5)
        
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_6, 0, 0, 0)
        
        stProdNr = wx.StaticText(self.panel_1, wx.ID_ANY, "Hersteller Nr.:")
        stProdNr.SetMinSize((90, 16))
        sizer_6.Add(stProdNr, 0, wx.ALL, 5)
        
        self.tcProdNr = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcProdNr.SetMinSize((270, 22))
        self.tcProdNr.Enable(False)
        sizer_6.Add(self.tcProdNr, 0, wx.ALL, 5)
        
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_8, 0, 0, 0)
        
        stCrimp = wx.StaticText(self.panel_1, wx.ID_ANY, u"Ausführung:")
        stCrimp.SetMinSize((90, 16))
        sizer_8.Add(stCrimp, 0, wx.ALL, 5)
        
        self.tcCrimp = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcCrimp.SetMinSize((270, 22))
        self.tcCrimp.Enable(False)
        sizer_8.Add(self.tcCrimp, 0, wx.ALL, 5)
        
        static_line_1 = wx.StaticLine(self.panel_1, wx.ID_ANY)
        sizer_4.Add(static_line_1, 0, wx.EXPAND, 0)
        
        stSlots = wx.StaticText(self.panel_1, wx.ID_ANY, u"Einsätze", style=wx.ALIGN_CENTER)
        stSlots.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_4.Add(stSlots, 0, wx.ALIGN_CENTER, 0)
        
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_10, 1, 0, 0)
        
        sizer_11 = wx.BoxSizer(wx.VERTICAL)
        sizer_10.Add(sizer_11, 1, wx.EXPAND, 0)
        
        sizer_13 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11.Add(sizer_13, 0, 0, 0)
        
        self.tcAWGSlot = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcAWGSlot.SetMinSize((80, 22))
        sizer_13.Add(self.tcAWGSlot, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        
        self.tcMetSlot = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcMetSlot.SetMinSize((80, 22))
        sizer_13.Add(self.tcMetSlot, 0, wx.RIGHT | wx.TOP, 5)
        
        self.lcSlots = wx.ListCtrl(self.panel_1, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.lcSlots.SetMinSize((165, 145))
        self.lcSlots.Enable(False)
        self.lcSlots.AppendColumn("AWG", format=wx.LIST_FORMAT_LEFT, width=82)
        self.lcSlots.AppendColumn("Metrisch", format=wx.LIST_FORMAT_LEFT, width=82)
        sizer_11.Add(self.lcSlots, 1, wx.ALL, 5)
        
        sizer_12 = wx.BoxSizer(wx.VERTICAL)
        sizer_10.Add(sizer_12, 1, wx.EXPAND, 0)
        
        self.btnAddSlot = wx.Button(self.panel_1, wx.ID_ANY, u"Einsatz hinzufügen")
        self.btnAddSlot.SetMinSize((150, 21))
        self.btnAddSlot.Enable(False)
        sizer_12.Add(self.btnAddSlot, 0, wx.ALL, 5)
        
        self.btnDeleteSlot = wx.Button(self.panel_1, wx.ID_ANY, u"Einsatz löschen")
        self.btnDeleteSlot.SetMinSize((150, 21))
        self.btnDeleteSlot.Enable(False)
        sizer_12.Add(self.btnDeleteSlot, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)
        
        self.pnlSubSpacer = wx.Panel(self.panel_1, wx.ID_ANY)
        sizer_12.Add(self.pnlSubSpacer, 1, wx.EXPAND, 0)
        
        static_line_2 = wx.StaticLine(self.panel_1, wx.ID_ANY)
        sizer_4.Add(static_line_2, 0, wx.EXPAND, 0)
        
        stCrimpTool = wx.StaticText(self.panel_1, wx.ID_ANY, "Crimpzangen ID", style=wx.ALIGN_CENTER)
        stCrimpTool.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_4.Add(stCrimpTool, 0, wx.ALIGN_CENTER, 0)
        
        grid_sizer_1 = wx.FlexGridSizer(2, 2, 5, 5)
        sizer_4.Add(grid_sizer_1, 1, wx.EXPAND | wx.TOP, 5)
        
        self.tcID = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcID.SetMinSize((170, 22))
        grid_sizer_1.Add(self.tcID, 0, 0, 0)
        
        self.btnAddID = wx.Button(self.panel_1, wx.ID_ANY, u"ID hinzufügen")
        self.btnAddID.SetMinSize((150, 21))
        self.btnAddID.Enable(False)
        grid_sizer_1.Add(self.btnAddID, 0, wx.LEFT, 5)
        
        self.lbToolIDs = wx.ListBox(self.panel_1, wx.ID_ANY, choices=[])
        self.lbToolIDs.SetMinSize((170, 150))
        grid_sizer_1.Add(self.lbToolIDs, 0, 0, 0)
        
        self.btnRemoveID = wx.Button(self.panel_1, wx.ID_ANY, "ID entfernen")
        self.btnRemoveID.SetMinSize((150, 21))
        self.btnRemoveID.Enable(False)
        grid_sizer_1.Add(self.btnRemoveID, 0, wx.LEFT, 5)
        
        self.panel_1.SetSizer(sizer_1)
        
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.btnEditClicked, self.btnEdit)
        self.Bind(wx.EVT_BUTTON, self.btnDeleteClicked, self.btnDelete)
        self.Bind(wx.EVT_BUTTON, self.btnAddSlotClicked, self.btnAddSlot)
        self.Bind(wx.EVT_BUTTON, self.btnDeleteSlotClicked, self.btnDeleteSlot)
        # end wxGlade

    def btnEditClicked(self, event):  # wxGlade: CrimptoolEditorGUI.<event_handler>
        print("Event handler 'btnEditClicked' not implemented!")
        event.Skip()

    def btnDeleteClicked(self, event):  # wxGlade: CrimptoolEditorGUI.<event_handler>
        print("Event handler 'btnDeleteClicked' not implemented!")
        event.Skip()

    def btnAddSlotClicked(self, event):  # wxGlade: CrimptoolEditorGUI.<event_handler>
        print("Event handler 'btnAddSlotClicked' not implemented!")
        event.Skip()

    def btnDeleteSlotClicked(self, event):  # wxGlade: CrimptoolEditorGUI.<event_handler>
        print("Event handler 'btnDeleteSlotClicked' not implemented!")
        event.Skip()

# end of class CrimptoolEditorGUI

class Crimptool(wx.App):
    def OnInit(self):
        self.CrimptoolEditorGUI = CrimptoolEditorGUI(None, wx.ID_ANY, "")
        self.SetTopWindow(self.CrimptoolEditorGUI)
        self.CrimptoolEditorGUI.Show()
        return True

# end of class Crimptool

if __name__ == "__main__":
    app = Crimptool(0)
    app.MainLoop()
