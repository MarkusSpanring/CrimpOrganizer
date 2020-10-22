#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Thu Oct 22 20:11:27 2020
#

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class CrimpOrganizerGUI(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: CrimpOrganizerGUI.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((1419, 599))
        self.SetTitle("CrimpOrganizerGUI")
        
        # Menu Bar
        self.mbOrganizer = wx.MenuBar()
        self.optFile = wx.Menu()
        self.optFile.Append(wx.ID_ANY, "Einstellungen", "")
        self.mbOrganizer.Append(self.optFile, "Datei")
        self.optOrder = wx.Menu()
        self.optOrder.Append(wx.ID_ANY, u"Öffnen", "")
        self.mbOrganizer.Append(self.optOrder, u"Aufträge")
        self.SetMenuBar(self.mbOrganizer)
        # Menu Bar end
        
        self.mainPanel = wx.Panel(self, wx.ID_ANY)
        
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 0, wx.EXPAND, 0)
        
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_2, 0, wx.EXPAND, 0)
        
        static_text_1 = wx.StaticText(self.mainPanel, wx.ID_ANY, "Crimpkontakte")
        static_text_1.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_2.Add(static_text_1, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        
        self.panel_1 = wx.Panel(self.mainPanel, wx.ID_ANY)
        sizer_2.Add(self.panel_1, 1, wx.EXPAND, 0)
        
        self.btnNewContact = wx.Button(self.mainPanel, wx.ID_ANY, "Neu")
        sizer_2.Add(self.btnNewContact, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        
        static_line_3 = wx.StaticLine(self.mainPanel, wx.ID_ANY)
        sizer_3.Add(static_line_3, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 5)
        
        self.tcSearchContact = wx.SearchCtrl(self.mainPanel, wx.ID_ANY, "")
        self.tcSearchContact.SetMinSize((220, 22))
        self.tcSearchContact.ShowCancelButton(True)
        self.tcSearchContact.SetDescriptiveText("Suchen")
        sizer_3.Add(self.tcSearchContact, 0, wx.ALL, 5)
        
        self.lcContacts = wx.ListCtrl(self.mainPanel, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.lcContacts.SetMinSize((400, 290))
        self.lcContacts.AppendColumn("Artikelnr.", format=wx.LIST_FORMAT_LEFT, width=155)
        self.lcContacts.AppendColumn("Hersteller", format=wx.LIST_FORMAT_LEFT, width=150)
        self.lcContacts.AppendColumn("Kontaktserie", format=wx.LIST_FORMAT_LEFT, width=150)
        sizer_3.Add(self.lcContacts, 1, wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        static_line_1 = wx.StaticLine(self.mainPanel, wx.ID_ANY, style=wx.LI_VERTICAL)
        sizer_1.Add(static_line_1, 0, wx.EXPAND, 0)
        
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_5, 1, wx.EXPAND, 0)
        
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5.Add(sizer_7, 0, wx.EXPAND, 0)
        
        static_text_2 = wx.StaticText(self.mainPanel, wx.ID_ANY, "Crimpzangen")
        static_text_2.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_7.Add(static_text_2, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        
        self.panel_2 = wx.Panel(self.mainPanel, wx.ID_ANY)
        sizer_7.Add(self.panel_2, 1, wx.EXPAND, 0)
        
        self.btnManageTools = wx.Button(self.mainPanel, wx.ID_ANY, "Verwalten")
        sizer_7.Add(self.btnManageTools, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        
        static_line_4 = wx.StaticLine(self.mainPanel, wx.ID_ANY)
        sizer_5.Add(static_line_4, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 5)
        
        self.panel_3 = wx.Panel(self.mainPanel, wx.ID_ANY)
        self.panel_3.SetMinSize((455, 22))
        sizer_5.Add(self.panel_3, 0, wx.ALL, 5)
        
        self.lcToolSummary = wx.ListCtrl(self.mainPanel, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.lcToolSummary.SetMinSize((450, 280))
        self.lcToolSummary.AppendColumn(u"Ø", format=wx.LIST_FORMAT_LEFT, width=70)
        self.lcToolSummary.AppendColumn("Crimpzange", format=wx.LIST_FORMAT_LEFT, width=200)
        self.lcToolSummary.AppendColumn("Einsatz", format=wx.LIST_FORMAT_LEFT, width=210)
        sizer_5.Add(self.lcToolSummary, 1, wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        static_line_2 = wx.StaticLine(self.mainPanel, wx.ID_ANY, style=wx.LI_VERTICAL)
        sizer_1.Add(static_line_2, 0, wx.EXPAND, 0)
        
        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_6, 0, wx.EXPAND, 0)
        
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_10, 0, 0, 0)
        
        static_text_3 = wx.StaticText(self.mainPanel, wx.ID_ANY, u"Crimpanweisung für")
        static_text_3.SetMinSize((201, 25))
        static_text_3.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_10.Add(static_text_3, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        
        self.tcSchemeNr = wx.TextCtrl(self.mainPanel, wx.ID_ANY, "")
        self.tcSchemeNr.SetMinSize((100, 25))
        sizer_10.Add(self.tcSchemeNr, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        
        stSchemeRev = wx.StaticText(self.mainPanel, wx.ID_ANY, "Rev.:")
        stSchemeRev.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_10.Add(stSchemeRev, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        
        self.tcSchemeRev = wx.TextCtrl(self.mainPanel, wx.ID_ANY, "")
        self.tcSchemeRev.SetMinSize((50, 25))
        sizer_10.Add(self.tcSchemeRev, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        
        static_line_5 = wx.StaticLine(self.mainPanel, wx.ID_ANY)
        sizer_6.Add(static_line_5, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 5)
        
        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_11, 0, wx.EXPAND, 5)
        
        self.panel_5 = wx.Panel(self.mainPanel, wx.ID_ANY)
        self.panel_5.SetMinSize((60, 26))
        sizer_11.Add(self.panel_5, 1, 0, 0)
        
        self.btnCreateInstructions = wx.Button(self.mainPanel, wx.ID_ANY, "Crimpanweisung erzeugen")
        self.btnCreateInstructions.Enable(False)
        sizer_11.Add(self.btnCreateInstructions, 0, wx.BOTTOM | wx.RIGHT | wx.TOP, 5)
        
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(sizer_4, 1, 0, 0)
        
        self.treeInstructions = wx.TreeCtrl(self.mainPanel, wx.ID_ANY)
        self.treeInstructions.SetMinSize((200, 454))
        sizer_4.Add(self.treeInstructions, 0, wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        self.lcCrimpInstructions = wx.ListCtrl(self.mainPanel, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.lcCrimpInstructions.SetMinSize((320, 454))
        self.lcCrimpInstructions.AppendColumn("Pos.", format=wx.LIST_FORMAT_LEFT, width=50)
        self.lcCrimpInstructions.AppendColumn("Artikelnr.", format=wx.LIST_FORMAT_LEFT, width=120)
        self.lcCrimpInstructions.AppendColumn(u"Ø", format=wx.LIST_FORMAT_LEFT, width=70)
        self.lcCrimpInstructions.AppendColumn(u"Gehäuse", format=wx.LIST_FORMAT_LEFT, width=200)
        sizer_4.Add(self.lcCrimpInstructions, 1, wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        self.mainPanel.SetSizer(sizer_1)
        
        self.Layout()
        self.Centre()
        # end wxGlade

# end of class CrimpOrganizerGUI

class MyApp(wx.App):
    def OnInit(self):
        self.frame = CrimpOrganizerGUI(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
