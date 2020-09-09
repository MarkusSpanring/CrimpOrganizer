import wx


class AnnotateContactsPanel(wx.Panel):
    def __init__(self, parent, identifiers=[]):
        """Constructor"""
        identifier_names = []
        for identifier in identifiers:
            identifier_names.append(" mm²: ".join(identifier))

        self.n_fields = len(identifiers)
        wx.Panel.__init__(self, parent)
        self.number_of_identifiers = 0
        self.frame = parent

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(1 + self.n_fields, 3, 0, 0)
        self.mainSizer.Add(grid_sizer_1, 0, wx.CENTER | wx.ALL, 10)

        stHead1 = wx.StaticText(self, wx.ID_ANY, "Kontaktserie")
        stHead2 = wx.StaticText(self, wx.ID_ANY, "Position")
        stHead3 = wx.StaticText(self, wx.ID_ANY, "Gehäuse")
        grid_sizer_1.Add(stHead1, 0, wx.LEFT | wx.BOTTOM, 10)
        grid_sizer_1.Add(stHead2, 0, wx.LEFT | wx.BOTTOM, 10)
        grid_sizer_1.Add(stHead3, 0, wx.LEFT | wx.BOTTOM, 10)
        for i in range(self.n_fields):
            stIdentifier = wx.StaticText(self, i * 1000, identifier_names[i])
            tcPosition = wx.TextCtrl(self, i * 1000 + 1, "")
            tcName = wx.TextCtrl(self, i * 1000 + 2, "")
            tcPosition.Bind(wx.EVT_TEXT, self.onInfoChanged)
            tcName.Bind(wx.EVT_TEXT, self.onInfoChanged)
            grid_sizer_1.Add(stIdentifier, 0, wx.LEFT | wx.BOTTOM, 5)
            grid_sizer_1.Add(tcPosition, 0, wx.LEFT | wx.BOTTOM, 5)
            grid_sizer_1.Add(tcName, 0, wx.LEFT | wx.BOTTOM, 5)

        static_line_1 = wx.StaticLine(self, wx.ID_ANY)
        self.mainSizer.Add(static_line_1, 0, wx.ALL | wx.EXPAND, 5)

        self.btnApply = wx.Button(self, wx.ID_ANY, "Übernehmen")
        self.btnApply.Enable(False)

        self.mainSizer.Add(self.btnApply, 0, wx.BOTTOM | wx.LEFT, 5)

        self.SetSizer(self.mainSizer)

    def onInfoChanged(self, event):
        fields = []
        for i in range(self.n_fields):
            pos = self.FindWindowById(i * 1000 + 1)
            name = self.FindWindowById(i * 1000 + 2)
            fields.append(pos.GetValue() != "")
            fields.append(name.GetValue() != "")
        if all(fields):
            self.btnApply.Enable()
        else:
            self.btnApply.Disable()

        event.Skip()


class AnnotateContacts(wx.Frame):

    def __init__(self, *args, **kwds):
        self.identifiers = []
        for identifier in kwds.pop("identifiers", []):
            self.identifiers.append(identifier.split("#"))

        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.annotated_data = {}
        self.fSizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = AnnotateContactsPanel(self, identifiers=self.identifiers)
        self.panel.btnApply.Bind(wx.EVT_BUTTON, self.onApplyClicked)
        self.fSizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(self.fSizer)
        self.Fit()

    def onApplyClicked(self, event):
        for ID in range(len(self.identifiers)):
            data_key = "#".join(self.identifiers[ID])
            self.annotated_data[data_key] = {}
            pos = self.panel.FindWindowById(ID * 1000 + 1).GetValue()
            name = self.panel.FindWindowById(ID * 1000 + 2).GetValue()
            self.annotated_data[data_key]["pos"] = pos
            self.annotated_data[data_key]["name"] = name

        self.Close()


class MyApp(wx.App):
    def OnInit(self):
        self.AnnotateContacts = AnnotateContacts(None, wx.ID_ANY, "",
                                                 identifier=["1", "2", "3"])
        self.SetTopWindow(self.AnnotateContacts)
        self.AnnotateContacts.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
