#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Thu Oct 22 17:34:01 2020
#

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class OrderDetailsGUI(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: OrderDetailsGUI.__init__
        kwds["style"] = kwds.get("style", 0) | wx.CAPTION | wx.CLIP_CHILDREN | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((326, 151))
        self.SetTitle("OrderDetailsGUI")
        
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        
        grid_sizer_1 = wx.FlexGridSizer(3, 2, 5, 5)
        sizer_1.Add(grid_sizer_1, 0, wx.ALL, 0)
        
        st1 = wx.StaticText(self.panel_1, wx.ID_ANY, "Bestellnummer:")
        st1.SetMinSize((99, 16))
        grid_sizer_1.Add(st1, 0, wx.LEFT | wx.TOP, 5)
        
        self.tcOrderNr = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcOrderNr.SetMinSize((200, 22))
        grid_sizer_1.Add(self.tcOrderNr, 0, wx.TOP, 5)
        
        st2 = wx.StaticText(self.panel_1, wx.ID_ANY, "Auftragsnummer:")
        grid_sizer_1.Add(st2, 0, wx.LEFT, 5)
        
        self.tcJobNr = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcJobNr.SetMinSize((200, 22))
        grid_sizer_1.Add(self.tcJobNr, 0, 0, 0)
        
        st3 = wx.StaticText(self.panel_1, wx.ID_ANY, "Protokollnummer:")
        grid_sizer_1.Add(st3, 0, wx.LEFT, 5)
        
        self.tcProtocolNr = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.tcProtocolNr.SetMinSize((200, 22))
        grid_sizer_1.Add(self.tcProtocolNr, 0, 0, 0)
        
        static_line_1 = wx.StaticLine(self.panel_1, wx.ID_ANY)
        sizer_1.Add(static_line_1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        
        self.btnSave = wx.Button(self.panel_1, wx.ID_ANY, "Als Vorlage Speichern")
        sizer_2.Add(self.btnSave, 0, wx.LEFT | wx.TOP, 5)
        
        self.panel_2 = wx.Panel(self.panel_1, wx.ID_ANY)
        sizer_2.Add(self.panel_2, 1, 0, 0)
        
        self.btnPrint = wx.Button(self.panel_1, wx.ID_ANY, "Drucken")
        self.btnPrint.Enable(False)
        sizer_2.Add(self.btnPrint, 0, wx.RIGHT | wx.TOP, 5)
        
        self.panel_1.SetSizer(sizer_1)
        
        self.Layout()
        self.Centre()
        # end wxGlade

# end of class OrderDetailsGUI

class MyApp(wx.App):
    def OnInit(self):
        self.frame = OrderDetailsGUI(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
