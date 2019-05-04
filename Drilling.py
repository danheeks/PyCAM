from DepthOp import DepthOp
import geom
import cad
import Tool
from Object import PyChoiceProperty
from Object import PyProperty
from SpeedOp import SpeedOp
import wx
from nc.nc import *
from HeeksConfig import HeeksConfig
import math

type = 0

class Drilling(DepthOp):
    def __init__(self, tool_number = -1, operation_type = cad.OBJECT_TYPE_UNKNOWN):
        DepthOp.__init__(self, tool_number, operation_type)
        self.points = [] #  list of point id integers
        self.ReadDefaultValues()
        
    def WriteXml(self):
        cad.BeginXmlChild('params')
        cad.SetXmlValue('dwell', self.dwell)
        cad.SetXmlValue('retract_mode', self.retract_mode)
        cad.SetXmlValue('spindle_mode', self.spindle_mode)
        cad.SetXmlValue('internal_coolant_on', self.internal_coolant_on)
        cad.SetXmlValue('rapid_to_clearance', self.rapid_to_clearance)
        cad.EndXmlChild()
        for point in self.points:
            cad.BeginXmlChild('Point')
            cad.SetXmlValue('id', point) # integer
            cad.EndXmlChild()
        DepthOp.WriteXml(self)
        
    def ReadXml(self):
        child_element = cad.GetFirstXmlChild()
        while child_element != None:
            if child_element == 'params':
                self.dwell = cad.GetXmlFloat('dwell', self.dwell)
                self.retract_mode = cad.GetXmlInt('retract_mode', self.retract_mode)
                self.spindle_mode = cad.GetXmlInt('spindle_mode', self.spindle_mode)
                self.internal_coolant_on = cad.GetXmlBool('internal_coolant_on', self.internal_coolant_on)
                self.rapid_to_clearance = cad.GetXmlBool('rapid_to_clearance', self.rapid_to_clearance)
            elif child_element == 'Point':
                self.points.append(cad.GetXmlInt('id'))
                
            child_element = cad.GetNextXmlChild()
        DepthOp.ReadXml(self)
        
    def ReadDefaultValues(self):
        DepthOp.ReadDefaultValues(self)
        config = HeeksConfig()
        self.dwell = config.ReadFloat("dwell", 0.0)
        self.retract_mode = config.ReadInt("retract_mode", 0)
        self.spindle_mode = config.ReadInt("spindle_mode", 0)
        self.internal_coolant_on = config.ReadBool("internal_coolant_on", False)
        self.rapid_to_clearance = config.ReadBool("rapid_to_clearance", True)
        
    def WriteDefaultValues(self):
        DepthOp.WriteDefaultValues(self)
        config = HeeksConfig()
        config.WriteFloat("dwell", self.dwell)
        config.WriteInt("retract_mode", self.retract_mode)
        config.WriteInt("spindle_mode", self.spindle_mode)
        config.WriteBool("internal_coolant_on", self.internal_coolant_on)
        config.WriteBool("rapid_to_clearance", self.rapid_to_clearance)
        
    def TypeName(self):
        return "Drilling"

    def GetType(self):
        return type
    
    def op_icon(self):
        return "drilling"
    
    def HasEdit(self):
        return True
        
    def Edit(self):
        import DrillingDlg
        res =  DrillingDlg.Do(self)
        return res
        
    def MakeACopy(self):
        copy = Drilling()
        copy.CopyFrom(self)
        return copy
    
    def CopyFrom(self, object):
        DepthOp.CopyFrom(self, object)
        self.points = []
        for point in object.points: self.points.append(point)
        self.dwell = object.dwell
        self.retract_mode = object.retract_mode
        self.spindle_mode = object.spindle_mode
        self.internal_coolant_on = object.internal_coolant_on
        self.rapid_to_clearance = object.rapid_to_clearance
        
    def CallsObjListReadXml(self):
        return False
            
    def GetProperties(self):
        properties = []

        properties.append(PyProperty("Dwell", 'dwell', self))
        properties.append(PyChoiceProperty("Retract Mode", 'retract_mode', ['Rapid Retract', 'Feed Retract'], self))
        properties.append(PyChoiceProperty("Spindle Mode", 'spindle_mode', ['Keep Running', 'Stop At Bottom'], self))
        properties.append(PyProperty("Internal Coolant On", 'internal_coolant_on', self))
        properties.append(PyProperty("Rapid to Clearance Between Points", 'rapid_to_clearance', self))
        
        properties += DepthOp.GetProperties(self)

        return properties
    
    def DoGCodeCalls(self):
        tool = Tool.FindTool(self.tool_number)
        if tool == None:
            wx.MessageBox('Cannot generate G-Code for profile without a tool assigned')
            return
        
        depth_params = self.GetDepthParams()
        tool_diameter = tool.CuttingRadius(True) * 2.0
        SpeedOp.DoGCodeCalls(self)
        
        for point in self.points:
            object = cad.GetObjectFromId(cad.OBJECT_TYPE_POINT, point)
            pos = object.GetEndPoint()
            drill(x = pos.x/wx.GetApp().program.units, y = pos.y/wx.GetApp().program.units, dwell = self.dwell, depthparams = depth_params, retract_mode = self.retract_mode, spindle_mode = self.spindle_mode, internal_coolant_on = self.internal_coolant_on, rapid_to_clearance = self.rapid_to_clearance)
        
        end_canned_cycle()
