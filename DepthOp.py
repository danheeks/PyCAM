from SpeedOp import SpeedOp
from consts import *
from CNCConfig import CNCConfig
import cad

class DepthOp(SpeedOp):
    def __init__(self, tool_number = -1, operation_type = cad.OBJECT_TYPE_UNKNOWN):
        SpeedOp.__init__(self, tool_number, operation_type)
        self.clearance_height = 5.0
        self.start_depth = 0.0
        self.step_down = 1.0
        self.final_depth = -1.0
        self.rapid_safety_space = 2.0
        self.z_finish_depth = 0.0
        self.z_thru_depth = 0.0
        self.user_depths = ''
        
    def ReadDefaultValues(self):
        SpeedOp.ReadDefaultValues(self)
        config = CNCConfig()
        self.clearance_height = config.ReadFloat("ClearanceHeight", 5.0)
        self.start_depth = config.ReadFloat("StartDepth", 0.0)
        self.step_down = config.ReadFloat("StepDown", 1.0)
        self.final_depth = config.ReadFloat("FinalDepth", -1.0)
        self.rapid_safety_space = config.ReadFloat("RapidSpace", 2.0)

    def WriteDefaultValues(self):
        SpeedOp.WriteDefaultValues(self)
        config = CNCConfig()
        config.WriteFloat("ClearanceHeight", self.clearance_height)
        config.WriteFloat("StartDepth", self.start_depth)
        config.WriteFloat("StepDown", self.step_down)
        config.WriteFloat("FinalDepth", self.final_depth)
        config.WriteFloat("RapidSpace", self.rapid_safety_space)
        
    def AppendTextToProgram(self):
        SpeedOp.AppendTextToProgram(self)

        wx.GetApp().program.python_program += "clearance = float(" + str(self.clearance_height / wx.GetApp().program.units) + ")\n"
        wx.GetApp().program.python_program += "rapid_safety_space = float(" + str(self.rapid_safety_space / wx.GetApp().program.units) + ")\n"
        wx.GetApp().program.python_program += "start_depth = float(" + str(self.start_depth / wx.GetApp().program.units) + ")\n"
        wx.GetApp().program.python_program += "step_down = float(" + str(self.step_down / wx.GetApp().program.units) + ")\n"
        wx.GetApp().program.python_program += "final_depth = float(" + str(self.final_depth / wx.GetApp().program.units) + ")\n"

        tool = wx.GetApp().program.tools.FindTool(self.tool_number)
        if tool != None:
            wx.GetApp().program.python_program += "tool_diameter = float(" + str(tool.diameter) + ")\n"

        if self.abs_mode == ABS_MODE_ABSOLUTE:
            wx.GetApp().program.python_program += "#absolute() mode\n"
        else:
            wx.GetApp().program.python_program += "rapid(z=clearance)\n"
            wx.GetApp().program.python_program += "incremental()\n"
        
    def CopyFrom(self, object):
        SpeedOp.CopyFrom(self, object)
        self.clearance_height = object.clearance_height
        self.start_depth = object.start_depth
        self.step_down = object.step_down
        self.final_depth = object.final_depth
        self.rapid_safety_space = object.rapid_safety_space
        self.z_finish_depth = object.z_finish_depth
        self.z_thru_depth = object.z_thru_depth
        self.user_depths = object.user_depths

