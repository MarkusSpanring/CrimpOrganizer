#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Tue Aug 25 18:59:23 2020
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
        self.SetSize((567, 447))
        self.SetTitle("CrimpcontactEditor")
        
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.panel_1.SetMinSize((379, 361))
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_2, 0, 0, 0)
        
        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_12, 1, wx.EXPAND, 0)
        
        stRefNr = wx.StaticText(self.panel_1, wx.ID_ANY, "Artikelnummer:")
        stRefNr.SetMinSize((100, 16))
        sizer_12.Add(stRefNr, 0, wx.ALL, 5)
        
        self.tcRefNr = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcRefNr.SetMinSize((320, 22))
        sizer_12.Add(self.tcRefNr, 0, wx.ALL, 5)
        
        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_11, 1, wx.EXPAND, 0)
        
        stType = wx.StaticText(self.panel_1, wx.ID_ANY, "Type:")
        stType.SetMinSize((100, 16))
        sizer_11.Add(stType, 0, wx.ALL, 5)
        
        self.tcType = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcType.SetMinSize((320, 22))
        sizer_11.Add(self.tcType, 0, wx.ALL, 5)
        
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_10, 1, wx.EXPAND, 0)
        
        stProducer = wx.StaticText(self.panel_1, wx.ID_ANY, "Hersteller:")
        stProducer.SetMinSize((100, 16))
        sizer_10.Add(stProducer, 0, wx.ALL, 5)
        
        self.tcProducer = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcProducer.SetMinSize((320, 22))
        sizer_10.Add(self.tcProducer, 0, wx.ALL, 5)
        
        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_9, 1, wx.EXPAND, 0)
        
        stProducerNr = wx.StaticText(self.panel_1, wx.ID_ANY, "Hersteller Nr.:")
        stProducerNr.SetMinSize((100, 16))
        sizer_9.Add(stProducerNr, 0, wx.ALL, 5)
        
        self.tcProducerNr = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcProducerNr.SetMinSize((320, 22))
        sizer_9.Add(self.tcProducerNr, 0, wx.ALL, 5)
        
        static_line_1 = wx.StaticLine(self.panel_1, wx.ID_ANY)
        sizer_2.Add(static_line_1, 0, wx.ALL | wx.EXPAND, 5)
        
        sizer_13 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_13, 0, wx.BOTTOM, 7)
        
        headCrossection = wx.StaticText(self.panel_1, wx.ID_ANY, "Querschnitt")
        headCrossection.SetMinSize((80, 16))
        sizer_13.Add(headCrossection, 0, wx.ALL, 5)
        
        headTool = wx.StaticText(self.panel_1, wx.ID_ANY, "Crimpzange")
        headTool.SetMinSize((90, 16))
        sizer_13.Add(headTool, 0, wx.ALL, 5)
        
        headSlot = wx.StaticText(self.panel_1, wx.ID_ANY, "Einsatz")
        headSlot.SetMinSize((184, 16))
        sizer_13.Add(headSlot, 0, wx.ALL, 5)
        
        headSoll = wx.StaticText(self.panel_1, wx.ID_ANY, "Soll-Wert")
        sizer_13.Add(headSoll, 0, wx.ALL, 5)
        
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_7, 0, 0, 5)
        
        self.cbXSection = wx.ComboBox(self.panel_1, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.cbXSection.SetMinSize((110, 25))
        sizer_7.Add(self.cbXSection, 0, wx.LEFT, 5)
        
        self.cbTool = wx.ComboBox(self.panel_1, 225, choices=[], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.cbTool.SetMinSize((90, 25))
        self.cbTool.Enable(False)
        sizer_7.Add(self.cbTool, 0, wx.LEFT, 5)
        
        self.cbSlot = wx.ComboBox(self.panel_1, 325, choices=[], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.cbSlot.SetMinSize((190, 25))
        self.cbSlot.Enable(False)
        sizer_7.Add(self.cbSlot, 0, wx.LEFT, 5)
        
        self.tcSoll = wx.TextCtrl(self.panel_1, 425, "")
        self.tcSoll.SetMinSize((50, 22))
        self.tcSoll.Enable(False)
        sizer_7.Add(self.tcSoll, 0, wx.LEFT, 5)
        
        self.btnAddXSection = wx.Button(self.panel_1, wx.ID_ANY, u"Hinzufügen")
        self.btnAddXSection.Enable(False)
        sizer_7.Add(self.btnAddXSection, 0, wx.LEFT | wx.RIGHT, 5)
        
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
        
        self.lcCrimptools = wx.ListCtrl(self.panel_1, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.lcCrimptools.SetMinSize((400, 165))
        self.lcCrimptools.AppendColumn("Querschnitt", format=wx.LIST_FORMAT_LEFT, width=110)
        self.lcCrimptools.AppendColumn("Crimpzange", format=wx.LIST_FORMAT_LEFT, width=110)
        self.lcCrimptools.AppendColumn("Einsatz", format=wx.LIST_FORMAT_LEFT, width=210)
        self.lcCrimptools.AppendColumn("Soll-Wert", format=wx.LIST_FORMAT_LEFT, width=104)
        sizer_3.Add(self.lcCrimptools, 1, wx.ALL | wx.EXPAND, 5)
        
        static_line_3 = wx.StaticLine(self.panel_1, wx.ID_ANY)
        sizer_2.Add(static_line_3, 0, wx.EXPAND, 0)
        
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_5, 1, wx.EXPAND, 0)
        
        self.btnDeleteXSection = wx.Button(self.panel_1, wx.ID_ANY, "Crimpzange entfernen")
        self.btnDeleteXSection.Enable(False)
        sizer_5.Add(self.btnDeleteXSection, 0, wx.ALL, 5)
        
        self.panel_2 = wx.Panel(self.panel_1, wx.ID_ANY)
        sizer_5.Add(self.panel_2, 1, wx.EXPAND, 0)
        
        self.btnSave = wx.Button(self.panel_1, wx.ID_ANY, "Speichern")
        self.btnSave.Enable(False)
        sizer_5.Add(self.btnSave, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        
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
