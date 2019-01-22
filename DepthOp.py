from SpeedOp import SpeedOp
from consts import *
from CNCConfig import CNCConfig

class DepthOp(SpeedOp):
    def __init__(self):
        SpeedOp.__init__(self)
        
    def ReadDefaultValues(self):
        SpeedOp.ReadDefaultValues(self)
        config = CNCConfig()
        self.abs_mode = config.ReadInt("DepthOpAbsMode", ABS_MODE_ABSOLUTE)
        self.clearance_height = config.ReadFloat("DepthOpClearance", 5.0)
        self.start_depth = config.ReadFloat("DepthOpStartDepth", 0.0)
        self.step_down = config.ReadFloat("DepthOpStepDown", 1.0)
        self.final_depth = config.ReadFloat("DepthOpFinalDepth", -1.0)
        self.rapid_safety_space = config.ReadFloat("DepthOpRapidSpace", 2.0)

    def WriteDefaultValues(self):
        SpeedOp.WriteDefaultValues(self)
        config = CNCConfig()
        config.WriteInt("DepthOpAbsMode", self.abs_mode)
        config.WriteFloat("DepthOpClearance", self.clearance_height)
        config.WriteFloat("DepthOpStartDepth", self.start_depth)
        config.WriteFloat("DepthOpStepDown", self.step_down)
        config.WriteFloat("DepthOpFinalDepth", self.final_depth)
        config.WriteFloat("DepthOpRapidSpace", self.rapid_safety_space)
        
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
