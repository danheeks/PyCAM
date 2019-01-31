from OpDlg import OpDlg
from NiceTextCtrl import LengthCtrl
from NiceTextCtrl import DoubleCtrl

class SpeedOpDlg(OpDlg):
    def __init__(self, parent, object, some_controls_on_left, title, top_level):
        OpDlg.__init__(self, parent, object, title, False)
        feeds_and_speeds_control_list = self.rightControls
        if some_controls_on_left: feeds_and_speeds_control_list = self.leftControls
        
        self.lgthHFeed = LengthCtrl(self)
        feeds_and_speeds_control_list.append(self.MakeLabelAndControl('Horizontal Feedrate', self.lgthHFeed))
        self.lgthVFeed = LengthCtrl(self)
        feeds_and_speeds_control_list.append(self.MakeLabelAndControl('Vertical Feedrate', self.lgthVFeed))
        self.dblSpindleSpeed = DoubleCtrl(self)
        feeds_and_speeds_control_list.append(self.MakeLabelAndControl('Spindle Speed', self.dblSpindleSpeed))
        
        if top_level:
            OpDlg.AddControlsAndCreate()
            self.cmbTool.SetFocus()
            
    def GetDataRaw(self, object):
        object.horizontal_feed_rate = self.lgthHFeed.GetValue()
        object.vertical_feed_rate = self.lgthVFeed.GetValue()
        object.spindle_speed = self.dblSpindleSpeed.GetValue()
        
        OpDlg.GetDataRaw(self, object)
        
    def SetFromDataRaw(self, object):
        self.lgthHFeed.SetValue(object.horizontal_feed_rate)
        self.lgthVFeed.SetValue(object.vertical_feed_rate)
        self.dblSpindleSpeed.SetValue(object.spindle_speed)
        
        OpDlg.SetFromDataRaw(self, object)
        