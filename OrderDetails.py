import wx
from OrderDetailsGUI import OrderDetailsGUI


class OrderDetails(OrderDetailsGUI):
    def __init__(self, parent, *args, **kwds):
        OrderDetailsGUI.__init__(self, parent, *args, **kwds)

        self.tcOrderNr.Bind(wx.EVT_TEXT, self.onDetailsChanged)
        self.tcJobNr.Bind(wx.EVT_TEXT, self.onDetailsChanged)
        self.tcReceiptNr.Bind(wx.EVT_TEXT, self.onDetailsChanged)
        self.tcProtocolNr.Bind(wx.EVT_TEXT, self.onDetailsChanged)
        self.btnPrint.Bind(wx.EVT_BUTTON, self.onPrintClicked)

    def onDetailsChanged(self, event):
        detailscreen = self.readInfoScreen()

        completeInfo = []
        for i in detailscreen:
            completeInfo.append(i != "")

        if all(completeInfo):
            self.btnPrint.Enable()
        else:
            self.btnPrint.Disable()

    def onPrintClicked(self, event):
        self.Close()

    def readInfoScreen(self):
        detailscreen = []
        detailscreen.append(self.tcOrderNr.GetValue())
        detailscreen.append(self.tcJobNr.GetValue())
        detailscreen.append(self.tcReceiptNr.GetValue())
        detailscreen.append(self.tcProtocolNr.GetValue())

        return detailscreen

class MyApp(wx.App):
    def OnInit(self):
        self.OrderDetails = OrderDetails(None, wx.ID_ANY, "")
        self.SetTopWindow(self.OrderDetails)
        self.OrderDetails.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
