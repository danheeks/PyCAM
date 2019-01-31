from Operation import Operation
from CNCConfig import CNCConfig
import cad

ABS_MODE_ABSOLUTE = 1
ABS_MODE_INCREMENTAL = 2

class SpeedOp(Operation):
    def __init__(self, tool_number = -1, operation_type = cad.OBJECT_TYPE_UNKNOWN):
        Operation.__init__(self, tool_number, operation_type)
        self.horizontal_feed_rate = 200.0
        self.vertical_feed_rate = 50.0
        self.spindle_speed = 7000.0
        
    def ReadDefaultValues(self):
        Operation.ReadDefaultValues(self)
        config = CNCConfig()
        self.horizontal_feed_rate = config.ReadFloat("SpeedOpHFeedrate", 200.0)
        self.vertical_feed_rate = config.ReadFloat("SpeedOpVFeedrate", 50.0)
        self.spindle_speed = config.ReadFloat("SpeedOpSpindleSpeed", 7000.0)

    def WriteDefaultValues(self):
        Operation.WriteDefaultValues(self)
        config = CNCConfig()
        config.WriteFloat("SpeedOpHFeedrate", self.horizontal_feed_rate)
        config.WriteFloat("SpeedOpVFeedrate", self.vertical_feed_rate)
        config.WriteFloat("SpeedOpSpindleSpeed", self.spindle_speed)
        
    def AppendTextToProgram(self):
        Operation.AppendTextToProgram(self)

        if self.spindle_speed != 0.0:
            wx.GetApp().program.python_program += "spindle(" + str(self.spindle_speed) + ")\n"

        wx.GetApp().program.python_program += "feedrate_hv(" + str(self.horizontal_feed_rate / wx.GetApp().program.units) + ", "
        wx.GetApp().program.python_program += str(self.vertical_feed_rate / wx.GetApp().program.units) + ")\n"
        wx.GetApp().program.python_program += "flush_nc()\n"

    def CopyFrom(self, object):
        Operation.CopyFrom(self, object)
        self.horizontal_feed_rate = object.horizontal_feed_rate
        self.vertical_feed_rate = object.vertical_feed_rate
        self.spindle_speed = object.spindle_speed
