#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Thu Sep  3 16:51:13 2020
#

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class CrimpcontactEditorGUI(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: CrimpcontactEditorGUI.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((979, 615))
        self.SetTitle("CrimpcontaktEditor")
        
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.panel_1.SetMinSize((379, 361))
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        
        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_12, 0, wx.EXPAND, 0)
        
        stRefNr = wx.StaticText(self.panel_1, wx.ID_ANY, "Artikelnummer:")
        stRefNr.SetMinSize((100, 16))
        sizer_12.Add(stRefNr, 0, wx.ALL, 5)
        
        self.tcRefNr = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcRefNr.SetMinSize((320, 22))
        sizer_12.Add(self.tcRefNr, 0, wx.ALL, 5)
        
        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_11, 0, wx.EXPAND, 0)
        
        stSeries = wx.StaticText(self.panel_1, wx.ID_ANY, "Kontaktserie:")
        stSeries.SetMinSize((100, 16))
        sizer_11.Add(stSeries, 0, wx.ALL, 5)
        
        self.tcSeries = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcSeries.SetMinSize((320, 22))
        sizer_11.Add(self.tcSeries, 0, wx.ALL, 5)
        
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_10, 0, wx.EXPAND, 0)
        
        stProducer = wx.StaticText(self.panel_1, wx.ID_ANY, "Hersteller:")
        stProducer.SetMinSize((100, 16))
        sizer_10.Add(stProducer, 0, wx.ALL, 5)
        
        self.tcProducer = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcProducer.SetMinSize((320, 22))
        sizer_10.Add(self.tcProducer, 0, wx.ALL, 5)
        
        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_9, 0, wx.EXPAND, 0)
        
        stProducerNr = wx.StaticText(self.panel_1, wx.ID_ANY, "Hersteller Nr.:")
        stProducerNr.SetMinSize((100, 16))
        sizer_9.Add(stProducerNr, 0, wx.ALL, 5)
        
        self.tcProducerNr = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcProducerNr.SetMinSize((320, 22))
        sizer_9.Add(self.tcProducerNr, 0, wx.ALL, 5)
        
        static_line_1 = wx.StaticLine(self.panel_1, wx.ID_ANY)
        sizer_2.Add(static_line_1, 0, wx.ALL | wx.EXPAND, 5)
        
        grid_sizer_1 = wx.FlexGridSizer(2, 5, 0, 0)
        sizer_2.Add(grid_sizer_1, 0, 0, 0)
        
        headCrossection = wx.StaticText(self.panel_1, wx.ID_ANY, "Querschnitt")
        headCrossection.SetMinSize((80, 16))
        grid_sizer_1.Add(headCrossection, 0, wx.ALL, 5)
        
        headTool = wx.StaticText(self.panel_1, wx.ID_ANY, "Crimpzange")
        headTool.SetMinSize((90, 16))
        grid_sizer_1.Add(headTool, 0, wx.ALL, 5)
        
        headSlot = wx.StaticText(self.panel_1, wx.ID_ANY, "Einsatz")
        headSlot.SetMinSize((184, 16))
        grid_sizer_1.Add(headSlot, 0, wx.ALL, 5)
        
        headSoll = wx.StaticText(self.panel_1, wx.ID_ANY, "Soll-Wert")
        headSoll.SetMinSize((61, 16))
        grid_sizer_1.Add(headSoll, 0, wx.ALL, 5)
        
        self.panel_3 = wx.Panel(self.panel_1, wx.ID_ANY)
        grid_sizer_1.Add(self.panel_3, 1, wx.EXPAND, 0)
        
        self.cbXSection = wx.ComboBox(self.panel_1, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.cbXSection.SetMinSize((110, 25))
        grid_sizer_1.Add(self.cbXSection, 0, wx.LEFT, 5)
        
        self.cbTool = wx.ComboBox(self.panel_1, 225, choices=[], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.cbTool.SetMinSize((450, 25))
        self.cbTool.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        self.cbTool.Enable(False)
        grid_sizer_1.Add(self.cbTool, 0, 0, 0)
        
        self.cbSlot = wx.ComboBox(self.panel_1, 325, choices=[], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.cbSlot.SetMinSize((210, 25))
        self.cbSlot.Enable(False)
        grid_sizer_1.Add(self.cbSlot, 0, 0, 0)
        
        self.tcSoll = wx.TextCtrl(self.panel_1, 425, "")
        self.tcSoll.SetMinSize((100, 22))
        self.tcSoll.Enable(False)
        grid_sizer_1.Add(self.tcSoll, 0, 0, 0)
        
        self.btnAddXSection = wx.Button(self.panel_1, wx.ID_ANY, u"Hinzufügen")
        self.btnAddXSection.Enable(False)
        grid_sizer_1.Add(self.btnAddXSection, 0, wx.LEFT | wx.RIGHT, 5)
        
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_3, 5, wx.EXPAND, 0)
        
        self.lcCrimptools = wx.ListCtrl(self.panel_1, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.lcCrimptools.SetMinSize((400, 165))
        self.lcCrimptools.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        self.lcCrimptools.AppendColumn("Querschnitt", format=wx.LIST_FORMAT_LEFT, width=110)
        self.lcCrimptools.AppendColumn("Crimpzange", format=wx.LIST_FORMAT_LEFT, width=450)
        self.lcCrimptools.AppendColumn("Einsatz", format=wx.LIST_FORMAT_LEFT, width=210)
        self.lcCrimptools.AppendColumn("Soll-Wert", format=wx.LIST_FORMAT_LEFT, width=100)
        sizer_3.Add(self.lcCrimptools, 1, wx.ALL | wx.EXPAND, 5)
        
        static_line_3 = wx.StaticLine(self.panel_1, wx.ID_ANY)
        sizer_2.Add(static_line_3, 0, wx.EXPAND, 0)
        
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_5, 0, wx.EXPAND, 0)
        
        self.btnDeleteXSection = wx.Button(self.panel_1, wx.ID_ANY, "Crimpzange entfernen")
        self.btnDeleteXSection.Enable(False)
        sizer_5.Add(self.btnDeleteXSection, 0, wx.ALL, 5)
        
        self.panel_2 = wx.Panel(self.panel_1, wx.ID_ANY)
        sizer_5.Add(self.panel_2, 1, 0, 0)
        
        self.btnSave = wx.Button(self.panel_1, wx.ID_ANY, "Speichern")
        self.btnSave.Enable(False)
        sizer_5.Add(self.btnSave, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        
        grid_sizer_1.AddGrowableRow(1)
        
        self.panel_1.SetSizer(sizer_1)
        
        self.Layout()
        # end wxGlade

# end of class CrimpcontactEditorGUI

class MyApp(wx.App):
    def OnInit(self):
        self.CrimpcontactEditor = CrimpcontactEditorGUI(None, wx.ID_ANY, "")
        self.SetTopWindow(self.CrimpcontactEditor)
        self.CrimpcontactEditor.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
