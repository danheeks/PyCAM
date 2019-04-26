from SketchOpDlg import SketchOpDlg
from HeeksObjDlg import HeeksObjDlg
from NiceTextCtrl import LengthCtrl
from NiceTextCtrl import DoubleCtrl
import wx
import cad
from HDialog import HControl
from HDialog import ComboBoxBinded
import Pocket

class PocketDlg(SketchOpDlg):
    def __init__(self, object, title = 'Pocket Operation'):
        SketchOpDlg.__init__(self, object, title)

    def AddLeftControls(self):
        # add all the controls to the left side
        self.lgthStepOver = LengthCtrl(self)
        self.MakeLabelAndControl("Step Over", self.lgthStepOver).AddToSizer(self.sizerLeft)
        self.lgthMaterialAllowance = LengthCtrl(self)
        self.MakeLabelAndControl("Ml Allowance", self.lgthMaterialAllowance).AddToSizer(self.sizerLeft)
        self.cmbStartingPlace = ComboBoxBinded(self, choices = ["Boundary", "Center"])
        self.MakeLabelAndControl("Starting Place", self.cmbStartingPlace).AddToSizer(self.sizerLeft)
        self.cmbCutMode = ComboBoxBinded(self, choices = ["Conventional", "Climb"])
        self.MakeLabelAndControl("Cut Mode", self.cmbCutMode).AddToSizer(self.sizerLeft)
        self.chkKeepToolDown = wx.CheckBox(self, wx.ID_ANY, 'Keep Tool Down')
        HControl(wx.ALL, self.chkKeepToolDown).AddToSizer(self.sizerLeft)
        self.chkUseZigZag = wx.CheckBox(self, wx.ID_ANY, 'Use Zig Zag')
        HControl(wx.ALL, self.chkUseZigZag).AddToSizer(self.sizerLeft)
        self.dblZigAngle = DoubleCtrl(self)
        self.MakeLabelAndControl("Zig Zag Angle", self.dblZigAngle).AddToSizer(self.sizerLeft)
        self.chkZigUnidirectional = wx.CheckBox(self, wx.ID_ANY, 'Zig Unidirectional')
        HControl(wx.ALL, self.chkZigUnidirectional).AddToSizer(self.sizerLeft)
        
        SketchOpDlg.AddLeftControls(self)        
            
    def GetDataRaw(self):
        self.object.step_over = self.lgthStepOver.GetValue()
        self.object.material_allowance = self.lgthMaterialAllowance.GetValue()
        self.object.from_center = self.cmbStartingPlace.GetSelection()
        self.object.cut_mode = self.cmbCutMode.GetSelection()
        self.object.keep_tool_down_if_poss = self.chkKeepToolDown.GetValue()
        self.object.use_zig_zag = self.chkUseZigZag.GetValue()
        self.object.zig_angle = self.dblZigAngle.GetValue()
        self.object.zig_unidirectional = self.chkZigUnidirectional.GetValue()
        #self.object.entry_move = self.lgthFinishStepDown.GetValue()

        SketchOpDlg.GetDataRaw(self)
        
    def SetFromDataRaw(self):
        self.lgthStepOver.SetValue(self.object.step_over)
        self.lgthMaterialAllowance.SetValue(self.object.material_allowance)
        self.cmbStartingPlace.SetSelection(self.object.from_center)
        self.cmbCutMode.SetSelection(self.object.cut_mode)
        self.chkKeepToolDown.SetValue(self.object.keep_tool_down_if_poss)
        self.chkUseZigZag.SetValue(self.object.use_zig_zag)
        self.dblZigAngle.SetValue(self.object.zig_angle)
        self.chkZigUnidirectional.SetValue(self.object.zig_unidirectional)
        
        self.EnableControls()
        
        SketchOpDlg.SetFromDataRaw(self)
        
    def EnableControls(self):
        use_zig_zag = self.chkUseZigZag.GetValue()
        
        self.dblZigAngle.Enable(use_zig_zag)
        self.chkZigUnidirectional.Enable(use_zig_zag)

    def SetPictureByName(self, name):
        self.SetPictureByNameAndFolder( name, 'pocket')
        
    def SetPictureBitmap(self, bitmap, name):
        self.picture.SetPictureBitmap(bitmap, HeeksCNC.heekscnc_path + "/bitmaps/pocket/" + name + ".png", wx.BITMAP_TYPE_PNG)

    def SetPictureByWindow(self, w):
        if w == self.lgthStepOver: PocketDlg.SetPictureByName(self, 'step over')
        elif w == self.lgthMaterialAllowance: PocketDlg.SetPictureByName(self, 'step over')
        elif w == self.cmbStartingPlace:
            if self.cmbStartingPlace.GetSelection() == 1:
                PocketDlg.SetPictureByName(self, 'starting center')
            else:
                PocketDlg.SetPictureByName(self, 'starting boundary')
        elif w == self.cmbCutMode:
            if self.cmbCutMode.GetSelection() == 1:
                PocketDlg.SetPictureByName(self, 'climb milling')
            else:
                PocketDlg.SetPictureByName(self, 'conventional milling')
        elif w == self.chkKeepToolDown:
            if self.chkKeepToolDown.GetValue(): PocketDlg.SetPictureByName(self, 'tool down')
            else: PocketDlg.SetPictureByName(self, 'not tool down')
        elif w == self.chkUseZigZag or w == self.chkZigUnidirectional:
            if self.chkUseZigZag.GetValue():
                if self.chkZigUnidirectional.GetValue(): PocketDlg.SetPictureByName(self, 'zig unidirectional')
                else: PocketDlg.SetPictureByName(self, 'use zig zag')
            else: PocketDlg.SetPictureByName(self, 'general')
        elif w == self.dblZigAngle: PocketDlg.SetPictureByName(self, 'zig angle')
#        else:
#            SketchOpDlg.SetPictureByWindow(self, w)
        
def Do(object):
    dlg = PocketDlg(object)
    
    while(True):
        result = dlg.ShowModal()
        
        if result == wx.ID_OK:
            dlg.GetData()
            return True
        elif result == dlg.btnSketchPick.GetId():
            dlg.PickSketch()
        else:
            return False

            
            
            
            
            
            
            
