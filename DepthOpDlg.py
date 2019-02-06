from SpeedOpDlg import SpeedOpDlg
from HeeksObjDlg import HeeksObjDlg
from NiceTextCtrl import LengthCtrl

class DepthOpDlg(SpeedOpDlg):
    def __init__(self, object, drill_pictures, title):
        self.drill_pictures = drill_pictures
        SpeedOpDlg.__init__(self, object, False, title)

    def AddLeftControls(self):
        self.lgthClearanceHeight = LengthCtrl(self)
        self.MakeLabelAndControl('Clearance Height', self.lgthClearanceHeight).AddToSizer(self.sizerLeft)
        self.lgthRapidDownToHeight = LengthCtrl(self)
        self.MakeLabelAndControl('Rapid Safety Space', self.lgthRapidDownToHeight).AddToSizer(self.sizerLeft)
        self.lgthStartDepth = LengthCtrl(self)
        self.MakeLabelAndControl('Start Depth', self.lgthStartDepth).AddToSizer(self.sizerLeft)
        self.lgthFinalDepth = LengthCtrl(self)
        self.MakeLabelAndControl('Final Depth', self.lgthFinalDepth).AddToSizer(self.sizerLeft)
        self.lgthStepDown = LengthCtrl(self)
        self.MakeLabelAndControl('Step Down', self.lgthStepDown).AddToSizer(self.sizerLeft)
        self.lgthZFinishDepth = LengthCtrl(self)
        self.MakeLabelAndControl('Z Finish Depth', self.lgthZFinishDepth).AddToSizer(self.sizerLeft)
        self.lgthZThruDepth = LengthCtrl(self)
        self.MakeLabelAndControl('Z Through Depth', self.lgthZThruDepth).AddToSizer(self.sizerLeft)

        SpeedOpDlg.AddLeftControls(self)
    
    def AddRightControls(self):            
        SpeedOpDlg.AddRightControls(self)
        
    def SetDefaultFocus(self):
        self.lgthClearanceHeight.SetFocus()
            
    def GetDataRaw(self):
        self.object.clearance_height = self.lgthClearanceHeight.GetValue()
        self.object.rapid_safety_space = self.lgthRapidDownToHeight.GetValue()
        self.object.start_depth = self.lgthStartDepth.GetValue()
        self.object.final_depth = self.lgthFinalDepth.GetValue()
        self.object.step_down = self.lgthStepDown.GetValue()
        self.object.z_finish_depth = self.lgthZFinishDepth.GetValue()
        self.object.z_thru_depth = self.lgthZThruDepth.GetValue()
        
        SpeedOpDlg.GetDataRaw(self)
        
    def SetFromDataRaw(self):
        self.lgthClearanceHeight.SetValue(self.object.clearance_height)
        self.lgthRapidDownToHeight.SetValue(self.object.rapid_safety_space)
        self.lgthStartDepth.SetValue(self.object.start_depth)
        self.lgthFinalDepth.SetValue(self.object.final_depth)
        self.lgthStepDown.SetValue(self.object.step_down)
        self.lgthZFinishDepth.SetValue(self.object.z_finish_depth)
        self.lgthZThruDepth.SetValue(self.object.z_thru_depth)
        
        SpeedOpDlg.SetFromDataRaw(self)
        
    def SetPictureByWindow(self, w):
        if w == self.lgthClearanceHeight: DepthOpDlg.SetPictureByName(self, "drill clearance height" if self.drill_pictures else "clearance height")
        elif w == self.lgthRapidDownToHeight: DepthOpDlg.SetPictureByName(self, "drill rapid down height" if self.drill_pictures else "rapid down height")
        elif w == self.lgthStartDepth: DepthOpDlg.SetPictureByName(self, "drill start depth" if self.drill_pictures else "start depth")
        elif w == self.lgthFinalDepth: DepthOpDlg.SetPictureByName(self, "drill final depth" if self.drill_pictures else "final depth")
        elif w == self.lgthStepDown: DepthOpDlg.SetPictureByName(self, "drill step down" if self.drill_pictures else "step down")
        elif w == self.lgthZFinishDepth: DepthOpDlg.SetPictureByName(self, "drill z finish depth" if self.drill_pictures else "z finish depth")
        elif w == self.lgthZThruDepth: DepthOpDlg.SetPictureByName(self, "drill z thru depth" if self.drill_pictures else "z thru depth")

        else: SpeedOpDlg.SetPictureByWindow(self, w)
        
    def SetPictureByName(self, name):
        self.SetPictureByNameAndFolder(name, 'depthop')
        