import wx
import cad
import Surface
from SolidsDlg import SolidsDlg
from NiceTextCtrl import LengthCtrl
from HDialog import HControl

class SurfaceDlg(SolidsDlg):
    def __init__(self, object, title = 'Surface'):
        SolidsDlg.__init__(self, object, title)
        
    def SetPictureByName(self, name):
        self.SetPictureByNameAndFolder(name, 'surface')
        
    def SetPictureByNameAndFolder(self, name, folder):
        if self.picture:
            self.picture.SetPicture(wx.GetApp().cam_dir + '/bitmaps/' + folder + '/' + name + '.png')

    def AddLeftControls(self):
        # add the controls in one column
        self.lgthTolerance = LengthCtrl(self)
        self.MakeLabelAndControl("Tolerance", self.lgthTolerance).AddToSizer(self.sizerLeft)
        self.lgthMaterialAllowance = LengthCtrl(self)
        self.MakeLabelAndControl("Material Allowance", self.lgthMaterialAllowance).AddToSizer(self.sizerLeft)
        self.chkSameForEachPosition = wx.CheckBox(self, wx.ID_ANY, 'Same for Each Pattern Position')
        HControl(wx.ALL, self.chkSameForEachPosition).AddToSizer(self.sizerLeft)
        SolidsDlg.AddLeftControls(self)

    def GetDataRaw(self):
        self.object.tolerance = self.lgthTolerance.GetValue()
        self.object.material_allowance = self.lgthMaterialAllowance.GetValue()
        self.object.same_for_each_pattern_position = self.chkSameForEachPosition.IsChecked()
        SolidsDlg.GetDataRaw(self)

    def SetFromDataRaw(self):
        self.lgthTolerance.SetValue(self.object.tolerance)
        self.lgthMaterialAllowance.SetValue(self.object.material_allowance)
        self.chkSameForEachPosition.SetValue(self.object.same_for_each_pattern_position)
        SolidsDlg.SetFromDataRaw(self)
        
def Do(object):
    dlg = SurfaceDlg(object)
    while True:
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            dlg.GetData()
            return True
        elif result == dlg.btnSolidsPick.GetId():
            dlg.PickSolids()
        else:
            return False

            
            
            
            
            
            
            
