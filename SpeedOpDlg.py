from OpDlg import OpDlg
from NiceTextCtrl import LengthCtrl
from NiceTextCtrl import DoubleCtrl

class SpeedOpDlg(OpDlg):
    def __init__(self, object, controls_on_left, title):
        self.controls_on_left = controls_on_left
        OpDlg.__init__(self, object, title)
        
    def AddControls(self, sizer):
        self.lgthHFeed = LengthCtrl(self)
        self.MakeLabelAndControl('Horizontal Feedrate', self.lgthHFeed).AddToSizer(sizer)
        self.lgthVFeed = LengthCtrl(self)
        self.MakeLabelAndControl('Vertical Feedrate', self.lgthVFeed).AddToSizer(sizer)
        self.dblSpindleSpeed = DoubleCtrl(self)
        self.MakeLabelAndControl('Spindle Speed', self.dblSpindleSpeed).AddToSizer(sizer)
        
    def AddLeftControls(self):
        if self.controls_on_left:
            self.AddControls(self.sizerLeft)
        OpDlg.AddLeftControls(self)
    
    def AddRightControls(self): 
        if not self.controls_on_left:
            self.AddControls(self.sizerRight)
        OpDlg.AddRightControls(self)           

    def SetDefaultFocus(self):
        self.cmbTool.SetFocus()
            
    def GetDataRaw(self):
        self.object.horizontal_feed_rate = self.lgthHFeed.GetValue()
        self.object.vertical_feed_rate = self.lgthVFeed.GetValue()
        self.object.spindle_speed = self.dblSpindleSpeed.GetValue()
        
        OpDlg.GetDataRaw(self)
        
    def SetFromDataRaw(self):
        self.lgthHFeed.SetValue(self.object.horizontal_feed_rate)
        self.lgthVFeed.SetValue(self.object.vertical_feed_rate)
        self.dblSpindleSpeed.SetValue(self.object.spindle_speed)
        
        OpDlg.SetFromDataRaw(self)
