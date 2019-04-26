from SketchOpDlg import SketchOpDlg
from HeeksObjDlg import HeeksObjDlg
from NiceTextCtrl import LengthCtrl
import wx
import cad
from HDialog import HControl
from HDialog import ComboBoxBinded
import Profile

class ProfileDlg(SketchOpDlg):
    def __init__(self, object, title = 'Profile Operation'):
        SketchOpDlg.__init__(self, object, title)

    def AddLeftControls(self):
        # add all the controls to the left side
        tool_on_side_choices = ['Left', 'Right', 'On']
        self.cmbToolOnSide = ComboBoxBinded(self, choices = tool_on_side_choices)
        self.MakeLabelAndControl("Tool On Side", self.cmbToolOnSide).AddToSizer(self.sizerLeft)
        
        #self.SetSketchOrderAndCombo(self.sketch)
        
        cut_mode_choices = ["Conventional", "Climb"]
        self.cmbCutMode = ComboBoxBinded(self, choices = cut_mode_choices)
        self.MakeLabelAndControl("Cut Mode", self.cmbCutMode).AddToSizer(self.sizerLeft)
        #self.Bind(wx.EVT_COMBOBOX, self.OnComboOrCheck, self.cmbCutMode)
        self.lgthRollRadius = LengthCtrl(self)
        self.MakeLabelAndControl("Roll Radius", self.lgthRollRadius).AddToSizer(self.sizerLeft)
        self.lgthOffsetExtra = LengthCtrl(self)
        self.MakeLabelAndControl("Offset Extra", self.lgthOffsetExtra).AddToSizer(self.sizerLeft)
        self.chkDoFinishingPass = wx.CheckBox(self, wx.ID_ANY, 'Do Finishing Pass')
        HControl(wx.ALL, self.chkDoFinishingPass).AddToSizer(self.sizerLeft)
        self.chkOnlyFinishingPass = wx.CheckBox(self, wx.ID_ANY, 'Only Finishing Pass')
        HControl(wx.ALL, self.chkOnlyFinishingPass).AddToSizer(self.sizerLeft)
        
        self.lgthFinishingFeedrate = LengthCtrl(self)
        self.staticFinishingFeedrate = wx.StaticText(self, wx.ID_ANY, "Finishing Feed Rate")
        self.MakeControlUsingStaticText(self.staticFinishingFeedrate, self.lgthFinishingFeedrate).AddToSizer(self.sizerLeft)
        self.cmbFinishingCutMode = ComboBoxBinded(self, choices = cut_mode_choices)
        self.staticFinishingCutMode = wx.StaticText(self, wx.ID_ANY, "Finishing Cut Mode")
        self.MakeControlUsingStaticText(self.staticFinishingCutMode, self.cmbFinishingCutMode).AddToSizer(self.sizerLeft)
        self.lgthFinishStepDown = LengthCtrl(self)
        self.staticFinishStepDown = wx.StaticText(self, wx.ID_ANY, "Finish Step Down")
        self.MakeControlUsingStaticText(self.staticFinishStepDown, self.lgthFinishStepDown).AddToSizer(self.sizerLeft)
        
        SketchOpDlg.AddLeftControls(self)
        
    def OnSketchCombo(self, event):
        choice = self.cmbToolOnSide.GetSelection()
        self.SetSketchOrderAndCombo(self.cmbSketch.GetSelectedId())
        self.cmbToolOnSide.SetSelection(choice)
        
    def SetDefaultFocus(self):
        #self.cmbSketch.SetFocus()
        pass
            
    def GetDataRaw(self):
        if self.cmbToolOnSide.GetSelection() == 0:
            self.object.tool_on_side = Profile.PROFILE_LEFT_OR_OUTSIDE
        elif self.cmbToolOnSide.GetSelection() == 1:
            self.object.tool_on_side = Profile.PROFILE_RIGHT_OR_INSIDE
        elif self.cmbToolOnSide.GetSelection() == 2:
            self.object.tool_on_side = Profile.PROFILE_ON
            
        self.object.cut_mode = Profile.PROFILE_CLIMB if self.cmbCutMode.GetValue().lower() == 'climb' else Profile.PROFILE_CONVENTIONAL
        self.object.auto_roll_radius = self.lgthRollRadius.GetValue()
        self.object.offset_extra = self.lgthOffsetExtra.GetValue()
        self.object.do_finishing_pass = self.chkDoFinishingPass.GetValue()
        self.object.only_finishing_pass = self.chkOnlyFinishingPass.GetValue()
        self.object.finishing_h_feed_rate = self.lgthFinishingFeedrate.GetValue()
        self.object.finishing_cut_mode = Profile.PROFILE_CLIMB if self.cmbFinishingCutMode.GetValue().lower() == 'climb' else Profile.PROFILE_CONVENTIONAL
        self.object.finishing_step_down = self.lgthFinishStepDown.GetValue()

        SketchOpDlg.GetDataRaw(self)
        
    def SetFromDataRaw(self):
        choice = 2
        if self.object.tool_on_side == Profile.PROFILE_RIGHT_OR_INSIDE:
            choice = 1
        elif self.object.tool_on_side == Profile.PROFILE_LEFT_OR_OUTSIDE:
            choice = 0
        self.cmbToolOnSide.SetSelection(choice)
        
        self.cmbCutMode.SetValue("Climb" if self.object.cut_mode == Profile.PROFILE_CLIMB else "Conventional")
        self.lgthRollRadius.SetValue(self.object.auto_roll_radius)
        self.lgthOffsetExtra.SetValue(self.object.offset_extra)
        self.chkDoFinishingPass.SetValue(self.object.do_finishing_pass)
        self.chkOnlyFinishingPass.SetValue(self.object.only_finishing_pass)
        self.lgthFinishingFeedrate.SetValue(self.object.finishing_h_feed_rate)
        self.cmbFinishingCutMode.SetValue("Climb" if self.object.finishing_cut_mode == Profile.PROFILE_CLIMB else "Conventional")
        self.lgthFinishStepDown.SetValue(self.object.finishing_step_down)
        
        self.EnableControls()
        
        SketchOpDlg.SetFromDataRaw(self)
        
        self.SetSketchOrderAndCombo(self.cmbSketch.GetSelectedId())
        
    def EnableControls(self):
        finish = self.chkDoFinishingPass.GetValue()
        
        self.chkOnlyFinishingPass.Enable(finish)
        self.lgthFinishingFeedrate.Enable(finish)
        self.cmbFinishingCutMode.Enable(finish)
        self.lgthFinishStepDown.Enable(finish)
        self.staticFinishingFeedrate.Enable(finish)
        self.staticFinishingCutMode.Enable(finish)
        self.staticFinishStepDown.Enable(finish)
        
    def SetPictureByName(self, name):
        self.SetPictureByNameAndFolder( name, 'profile')
        
    def SetPictureByWindow(self, w):
        if w == self.cmbToolOnSide:
            sel = self.cmbToolOnSide.GetSelection()
            if sel == 2:
                ProfileDlg.SetPictureByName(self, 'side on')
            else:
                if self.order == cad.SketchOrderType.SketchOrderTypeOpen:
                    ProfileDlg.SetPictureByName(self, 'side right' if sel == 1 else 'side left')
                elif self.order == cad.SketchOrderType.SketchOrderTypeCloseCW or self.order == cad.SketchOrderType.SketchOrderTypeCloseCCW:
                    ProfileDlg.SetPictureByName(self, 'side inside' if sel == 1 else 'side outside')
                else:
                    ProfileDlg.SetPictureByName(self, 'side inside or right' if sel == 1 else 'side outside or left')
        elif w == self.cmbCutMode:
            if self.cmbCutMode.GetValue() == 'Climb':
                self.SetPictureByNameAndFolder('climb milling', 'pocket')
            else:
                self.SetPictureByNameAndFolder('conventional milling', 'pocket')
        elif w == self.lgthRollRadius: ProfileDlg.SetPictureByName(self, 'roll radius')
        elif w == self.lgthOffsetExtra: ProfileDlg.SetPictureByName(self, 'offset extra')
        elif w == self.chkDoFinishingPass or w == self.chkOnlyFinishingPass:
            if self.chkDoFinishingPass.GetValue():
                if self.chkOnlyFinishingPass.GetValue():
                    ProfileDlg.SetPictureByName(self, 'only finishing')
                else:
                    ProfileDlg.SetPictureByName(self, 'no finishing pass')
        elif w == self.cmbFinishingCutMode:
            if self.cmbFinishingCutMode.GetValue() == 'Climb':
                self.SetPictureByNameAndFolder('climb milling', 'pocket')
            else:
                self.SetPictureByNameAndFolder('conventional milling', 'pocket')
        elif w == self.lgthFinishStepDown:
            self.SetPictureByNameAndFolder('step down', 'depthop')
#        else:
#            SketchOpDlg.SetPictureByWindow(self, w)
        
    def SetSketchOrderAndCombo(self, s):
        self.order = cad.SketchOrderType.SketchOrderTypeUnknown
        
        sketch = cad.GetObjectFromId(cad.OBJECT_TYPE_SKETCH, s)
        if sketch and sketch.GetType() == cad.OBJECT_TYPE_SKETCH:
            self.order = sketch.GetSketchOrder()
            
        if self.order == cad.SketchOrderType.SketchOrderTypeOpen:
            self.cmbToolOnSide.SetString(0, 'Left')
            self.cmbToolOnSide.SetString(1, 'Right')
        elif self.order == cad.SketchOrderType.SketchOrderTypeCloseCW or self.order == cad.SketchOrderType.SketchOrderTypeCloseCCW:
            self.cmbToolOnSide.SetString(0, 'Outside')
            self.cmbToolOnSide.SetString(1, 'Inside')
        else:
            self.cmbToolOnSide.SetString(0, 'Outside or Left')
            self.cmbToolOnSide.SetString(1, 'Inside or Right')
            
        
def Do(object):
    dlg = ProfileDlg(object)
    
    while(True):
        result = dlg.ShowModal()
        
        if result == wx.ID_OK:
            dlg.GetData()
            return True
        elif result == dlg.btnSketchPick.GetId():
            dlg.PickSketch()
        else:
            return False

