from SpeedOp import SpeedOp
from consts import *
from HeeksConfig import HeeksConfig
import cad
import depth_params
from Object import PyProperty
from Object import PyPropertyLength

class DepthOp(SpeedOp):
    def __init__(self):
        SpeedOp.__init__(self)
        self.user_depths = ''
        self.clearance_height = 5.0
        self.start_depth = 0.0
        self.step_down = 1.0
        self.final_depth = -1.0
        self.rapid_safety_space = 2.0
        self.z_finish_depth = 0.0
        self.z_thru_depth = 0.0
        
    def ReadDefaultValues(self):
        SpeedOp.ReadDefaultValues(self)
        config = HeeksConfig()
        self.clearance_height = config.ReadFloat("ClearanceHeight", 5.0)
        self.start_depth = config.ReadFloat("StartDepth", 0.0)
        self.step_down = config.ReadFloat("StepDown", 1.0)
        self.final_depth = config.ReadFloat("FinalDepth", -1.0)
        self.rapid_safety_space = config.ReadFloat("RapidSpace", 2.0)
        self.z_finish_depth = config.ReadFloat("ZFinish", 0.0)
        self.z_thru_depth = config.ReadFloat("ZThru", 0.0)

    def WriteDefaultValues(self):
        SpeedOp.WriteDefaultValues(self)
        config = HeeksConfig()
        config.WriteFloat("ClearanceHeight", self.clearance_height)
        config.WriteFloat("StartDepth", self.start_depth)
        config.WriteFloat("StepDown", self.step_down)
        config.WriteFloat("FinalDepth", self.final_depth)
        config.WriteFloat("RapidSpace", self.rapid_safety_space)
        config.WriteFloat("ZFinish", self.z_finish_depth)
        config.WriteFloat("ZThru", self.z_thru_depth)
        
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
        
    def WriteXml(self):
        cad.BeginXmlChild('depthop')
        cad.SetXmlValue('clear', self.clearance_height)
        cad.SetXmlValue('down', self.step_down)
        if self.z_finish_depth > 0.0000001: cad.SetXmlValue('zfinish', self.z_finish_depth)
        if self.z_thru_depth > 0.0000001: cad.SetXmlValue('zthru', self.z_thru_depth)
        cad.SetXmlValue('userdepths', self.user_depths)
        cad.SetXmlValue('startdepth', self.start_depth)
        cad.SetXmlValue('depth', self.final_depth)
        cad.SetXmlValue('r', self.rapid_safety_space)
        cad.EndXmlChild()
        SpeedOp.WriteXml(self)
        
    def ReadXml(self):
        child_element = cad.GetFirstXmlChild()
        while child_element != None:
            if child_element == 'depthop':
                self.clearance_height = cad.GetXmlFloat('clear', self.clearance_height)
                self.step_down = cad.GetXmlFloat('down', self.step_down)
                self.z_finish_depth = cad.GetXmlFloat('zfinish', self.z_finish_depth)
                self.z_thru_depth = cad.GetXmlFloat('zthru', self.z_thru_depth)
                self.user_depths = cad.GetXmlValue('userdepths', self.user_depths)
                self.start_depth = cad.GetXmlFloat('startdepth', self.start_depth)
                self.final_depth = cad.GetXmlFloat('depth', self.final_depth)
                self.rapid_safety_space = cad.GetXmlFloat('r', self.rapid_safety_space)
            child_element = cad.GetNextXmlChild()
        SpeedOp.ReadXml(self)
            
    def GetProperties(self):
        properties = []

        properties.append(PyPropertyLength("Clearance Height", 'clearance_height', self))
        properties.append(PyPropertyLength("Start Depth", 'start_depth', self))
        properties.append(PyPropertyLength("Final Depth", 'final_depth', self))
        properties.append(PyPropertyLength("Maximum Step Down", 'step_down', self))
        properties.append(PyPropertyLength("Rapid Safety Space", 'rapid_safety_space', self))
        properties.append(PyPropertyLength("Z Finish Depth", 'z_finish_depth', self))
        properties.append(PyPropertyLength("Z Thru Depth", 'z_thru_depth', self))
        properties.append(PyProperty("User Depths", 'user_depths', self))
        
        properties += SpeedOp.GetProperties(self)

        return properties
            
    def GetDepthParams(self):
        # returns a depth_params object used in the older heekscnc code, and which can be modified for finishing pass
        return depth_params.depth_params(self.clearance_height, self.rapid_safety_space, self.start_depth, self.step_down, self.z_finish_depth, self.z_thru_depth, self.final_depth, self.user_depths)


