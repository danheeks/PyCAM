from SketchOpDlg import SketchOpDlg
from HeeksObjDlg import HeeksObjDlg
from NiceTextCtrl import LengthCtrl
import wx
import cad
from HDialog import HControl
from HDialog import ComboBoxBinded
import Profile

class ProfileDlg(SketchOpDlg):
    def __init__(self, parent, object, title = 'Profile Operation', top_level = True):
        SketchOpDlg.__init__(self, parent, object, title, False)
        save_leftControls = self.leftControls
        self.leftControls = []
        
        # add all the controls to the left side
        tool_on_side_choices = ['Left', 'Right', 'On']
        self.cmbToolOnSide = ComboBoxBinded(self, choices = tool_on_side_choices)
        self.leftControls.append(self.MakeLabelAndControl("Tool On Side", self.cmbToolOnSide))
        
        self.SetSketchOrderAndCombo(object.sketch)
        
        cut_mode_choices = ["Conventional", "Climb"]
        self.cmbCutMode = ComboBoxBinded(self, choices = cut_mode_choices)
        self.leftControls.append(self.MakeLabelAndControl("Cut Mode", self.cmbCutMode))
        #self.Bind(wx.EVT_COMBOBOX, self.OnComboOrCheck, self.cmbCutMode)
        self.lgthRollRadius = LengthCtrl(self)
        self.leftControls.append(self.MakeLabelAndControl("Roll Radius", self.lgthRollRadius))
        self.lgthOffsetExtra = LengthCtrl(self)
        self.leftControls.append(self.MakeLabelAndControl("Offset Extra", self.lgthOffsetExtra))
        self.chkDoFinishingPass = wx.CheckBox(self, wx.ID_ANY, 'Do Finishing Pass')
        self.leftControls.append(HControl(wx.ALL, self.chkDoFinishingPass))
        self.chkOnlyFinishingPass = wx.CheckBox(self, wx.ID_ANY, 'Only Finishing Pass')
        self.leftControls.append(HControl(wx.ALL, self.chkOnlyFinishingPass))
        
        self.lgthFinishingFeedrate = LengthCtrl(self)
        self.staticFinishingFeedrate = wx.StaticText(self, wx.ID_ANY, "Finishing Feed Rate")
        self.leftControls.append(self.MakeControlUsingStaticText(self.staticFinishingFeedrate, self.lgthFinishingFeedrate))
        self.cmbFinishingCutMode = ComboBoxBinded(self, choices = cut_mode_choices)
        self.staticFinishingCutMode = wx.StaticText(self, wx.ID_ANY, "Finishing Cut Mode")
        self.leftControls.append(self.MakeControlUsingStaticText(self.staticFinishingCutMode, self.cmbFinishingCutMode))
        self.lgthFinishStepDown = LengthCtrl(self)
        self.staticFinishStepDown = wx.StaticText(self, wx.ID_ANY, "Finish Step Down")
        self.leftControls.append(self.MakeControlUsingStaticText(self.staticFinishStepDown, self.lgthFinishStepDown))
        
        self.leftControls += save_leftControls
        
        if top_level:
            self.cmbSketch.SetFocus()
            HeeksObjDlg.AddControlsAndCreate(self, object)
            
    def GetDataRaw(self, object):
        if self.cmbToolOnSide.GetSelection() == 0:
            object.tool_on_side = Profile.PROFILE_LEFT_OR_OUTSIDE
        elif self.cmbToolOnSide.GetSelection() == 1:
            object.tool_on_side = Profile.PROFILE_RIGHT_OR_INSIDE
        elif self.cmbToolOnSide.GetSelection() == 2:
            object.tool_on_side = Profile.PROFILE_ON
            
        object.cut_mode = Profile.PROFILE_CLIMB if self.cmbCutMode.GetValue().lower() == 'climb' else Profile.PROFILE_CONVENTIONAL
        object.auto_roll_radius = self.lgthRollRadius.GetValue()
        object.offset_extra = self.lgthOffsetExtra.GetValue()
        object.do_finishing_pass = self.chkDoFinishingPass.GetValue()
        object.only_finishing_pass = self.chkOnlyFinishingPass.GetValue()
        object.finishing_h_feed_rate = self.lgthFinishingFeedrate.GetValue()
        object.finishing_cut_mode = Profile.PROFILE_CLIMB if self.cmbFinishingCutMode.GetValue().lower() == 'climb' else Profile.PROFILE_CONVENTIONAL
        object.finishing_step_down = self.lgthFinishStepDown.GetValue()

        SketchOpDlg.GetDataRaw(self, object)
        
    def SetFromDataRaw(self, object):
        choice = Profile.PROFILE_ON
        if object.tool_on_side == Profile.PROFILE_RIGHT_OR_INSIDE:
            choice = 1
        elif object.tool_on_side == Profile.PROFILE_LEFT_OR_OUTSIDE:
            choice = 2
        self.cmbToolOnSide.SetSelection(choice)
        
        self.cmbCutMode.SetValue("Climb" if object.cut_mode == Profile.PROFILE_CLIMB else "Conventional")
        self.lgthRollRadius.SetValue(object.auto_roll_radius)
        self.lgthOffsetExtra.SetValue(object.offset_extra)
        self.chkDoFinishingPass.SetValue(object.do_finishing_pass)
        self.chkOnlyFinishingPass.SetValue(object.only_finishing_pass)
        self.lgthFinishingFeedrate.SetValue(object.finishing_h_feed_rate)
        self.cmbFinishingCutMode.SetValue("Climb" if object.finishing_cut_mode == Profile.PROFILE_CLIMB else "Conventional")
        self.lgthFinishStepDown.SetValue(object.finishing_step_down)
        
        self.EnableControls()
        
        SketchOpDlg.SetFromDataRaw(self, object)
        
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
        else:
            SketchOpDlg.SetPictureByWindow(self, w)
        
    def SetSketchOrderAndCombo(self, s):
        self.order = cad.SketchOrderType.SketchOrderTypeUnknown
        
def Do(object):
    dlg = ProfileDlg(wx.GetApp().frame, object)
    
    while(True):
        result = dlg.ShowModal()
        
        if result == wx.ID_OK:
            dlg.GetData(object)
            return True
        elif result == dlg.btnSketchPick.GetId():
            dlg.PickSketch()
        else:
            return False

