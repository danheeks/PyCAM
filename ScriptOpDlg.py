from OpDlg import HeeksObjDlg
from NiceTextCtrl import LengthCtrl
from NiceTextCtrl import DoubleCtrl
import wx
import cad
from HDialog import HControl
from HDialog import ComboBoxBinded
from HDialog import control_border
from OpDlg import OpDlg
import ScriptOp

class ScriptOpDlg(OpDlg):
    def __init__(self, object, title = 'Script Operation'):
        OpDlg.__init__(self, object, title, False, False)

    def AddLeftControls(self):
        # add all the controls to the left side
        sizer_vertical = wx.BoxSizer(wx.VERTICAL)
        static_label = wx.StaticText(self, wx.ID_ANY, 'Script')
        sizer_vertical.Add(static_label, 0, wx.RIGHT | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, control_border)
        self.txtScript = wx.TextCtrl(self, wx.ID_ANY, '', wx.DefaultPosition, wx.Size(300, 200), wx.TE_MULTILINE | wx.TE_DONTWRAP | wx.TE_RICH | wx.TE_RICH2)
        sizer_vertical.Add(self.txtScript , 1, wx.LEFT | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, control_border );
        HControl(wx.EXPAND | wx.ALL, sizer_vertical).AddToSizer(self.sizerLeft)
        OpDlg.AddLeftControls(self)        
            
    def GetDataRaw(self):
        self.object.str = self.txtScript.GetValue()
        OpDlg.GetDataRaw(self)
        
    def SetFromDataRaw(self):
        self.txtScript.SetValue(self.object.str)
        OpDlg.SetFromDataRaw(self)
        
def Do(object):
    dlg = ScriptOpDlg(object)
    result = dlg.ShowModal()
    if result == wx.ID_OK:
        dlg.GetData()
        return True
    return False

            
            
            
            
            
            
            
