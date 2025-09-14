from DepthOpDlg import DepthOpDlg
import wx
import cad
from HDialog import HControl
from HDialog import ComboBoxBinded
from NiceTextCtrl import LengthCtrl
import SerialNums

class SerialNumsDlg(DepthOpDlg):
    def __init__(self, object, title = 'Serial Numbers Operation'):
        DepthOpDlg.__init__(self, object, False, title)

    def AddLeftControls(self):
        self.txtStartNumber = wx.TextCtrl(self, wx.ID_ANY)
        self.AddLabelAndControl(self.sizerLeft, 'Start Number', self.txtStartNumber)
        
        self.txtQuantity = wx.TextCtrl(self, wx.ID_ANY, 'Quantity')
        self.AddLabelAndControl(self.sizerLeft, 'Quantity', self.txtQuantity)
        
        self.lgthTextHeight = LengthCtrl(self)
        self.staticTextHeight = wx.StaticText(self, wx.ID_ANY, "Text Height")
        self.MakeControlUsingStaticText(self.staticTextHeight, self.lgthTextHeight).AddToSizer(self.sizerLeft)
        
        DepthOpDlg.AddLeftControls(self)
            
    def GetDataRaw(self):
        self.object.start_number = self.txtStartNumber.GetValue()
        self.object.quantity = int(self.txtQuantity.GetValue())
        self.object.height = self.lgthTextHeight.GetValue()

        DepthOpDlg.GetDataRaw(self)
        
    def SetFromDataRaw(self):
        self.txtStartNumber.SetValue(self.object.start_number)
        self.txtQuantity.SetValue(str(self.object.quantity))
        self.lgthTextHeight.SetValue(self.object.height)
                
        DepthOpDlg.SetFromDataRaw(self)
        
    def SetPictureByName(self, name):
        self.SetPictureByNameAndFolder(name, 'serialnums')
            
        
def Do(object):
    dlg = SerialNumsDlg(object)
    
    while(True):
        result = dlg.ShowModal()
        
        if result == wx.ID_OK:
            dlg.GetData()
            return True
        else:
            return False

