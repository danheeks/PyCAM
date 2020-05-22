from SketchOp import SketchOp
import geom
import cad
import Tool
from Object import PyChoiceProperty
from Object import PyProperty
from Object import PyPropertyLength
from SpeedOp import SpeedOp
import wx
from nc.nc import *
import kurve_funcs
import area_funcs
from HeeksConfig import HeeksConfig
import math

type = 0

PROFILE_CONVENTIONAL = 0
PROFILE_CLIMB = 1

ENTRY_STYLE_PLUNGE = 0
ENTRY_STYLE_RAMP = 1
ENTRY_STYLE_HELICAL = 2
ENTRY_STYLE_UNDEFINED = 3

class Pocket(SketchOp):
    def __init__(self, sketch = 0, tool_number = -1, operation_type = cad.OBJECT_TYPE_UNKNOWN):
        SketchOp.__init__(self, sketch, tool_number, operation_type)
        self.ReadDefaultValues()
        
    def WriteXml(self):
        cad.BeginXmlChild('params')
        cad.SetXmlValue('step', self.step_over)
        cad.SetXmlValue('cut_mode', self.cut_mode)
        cad.SetXmlValue('from_center', self.from_center)
        cad.SetXmlValue('keep_tool_down', self.keep_tool_down_if_poss)
        cad.SetXmlValue('use_zig_zag', self.use_zig_zag)
        cad.SetXmlValue('zig_angle', self.zig_angle)
        cad.SetXmlValue('zig_unidirectional', self.zig_unidirectional)
        cad.SetXmlValue('entry_move', self.entry_move)
        cad.EndXmlChild()
        SketchOp.WriteXml(self)
        
    def ReadXml(self):
        child_element = cad.GetFirstXmlChild()
        while child_element != None:
            if child_element == 'params':
                self.step_over = cad.GetXmlFloat('step', self.step_over)
                self.cut_mode = cad.GetXmlInt('cut_mode', self.cut_mode)
                self.from_center = cad.GetXmlInt('from_center', self.from_center)
                self.keep_tool_down_if_poss = cad.GetXmlBool('keep_tool_down', self.keep_tool_down_if_poss)
                self.use_zig_zag = cad.GetXmlBool('use_zig_zag', self.use_zig_zag)
                self.zig_angle = cad.GetXmlFloat('zig_angle', self.zig_angle)
                self.zig_unidirectional = cad.GetXmlBool('zig_unidirectional', self.zig_unidirectional)
                self.entry_move = cad.GetXmlInt('entry_move', self.entry_move)
            child_element = cad.GetNextXmlChild()
        SketchOp.ReadXml(self)
        
    def CallsObjListReadXml(self):
        return False
        
    def ReadDefaultValues(self):
        SketchOp.ReadDefaultValues(self)
        config = HeeksConfig()
        self.step_over = config.ReadFloat("Stepover", 1.0)
        self.cut_mode = config.ReadInt("CutMode", PROFILE_CLIMB)
        self.from_center = config.ReadInt("FromCenter", True)
        self.material_allowance = config.ReadFloat("MaterialAllowance", 0.0)
        self.keep_tool_down_if_poss = config.ReadBool("KeepToolDown", True)
        self.use_zig_zag = config.ReadBool("UseZigZag", False)
        self.zig_angle = config.ReadFloat("ZigAngle", 0.0)
        self.zig_unidirectional = config.ReadBool("ZigUnidirectional", False)
        self.entry_move = config.ReadInt("DecentStrategy", ENTRY_STYLE_PLUNGE)
        
    def WriteDefaultValues(self):
        SketchOp.WriteDefaultValues(self)
        config = HeeksConfig()
        config.WriteFloat("Stepover", self.step_over)
        config.WriteInt("CutMode", self.cut_mode)
        config.WriteBool("FromCenter", self.from_center)
        config.WriteFloat("MaterialAllowance", self.material_allowance)
        config.WriteBool("KeepToolDown", self.keep_tool_down_if_poss)
        config.WriteBool("UseZigZag", self.use_zig_zag)
        config.WriteFloat("ZigAngle", self.zig_angle)
        config.WriteBool("ZigUnidirectional", self.zig_unidirectional)
        config.WriteInt("DecentStrategy", self.entry_move)
        
    def TypeName(self):
        return "Pocket"

    def GetType(self):
        return type
    
    def op_icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "pocket"
    
    def HasEdit(self):
        return True
        
    def Edit(self):
        import PocketDlg
        res =  PocketDlg.Do(self)
        return res
        
    def MakeACopy(self):
        copy = Pocket(self.sketch)
        copy.CopyFrom(self)
        return copy
    
    def CopyFrom(self, object):
        SketchOp.CopyFrom(self, object)
        self.step_over = object.step_over
        self.cut_mode = object.cut_mode
        self.material_allowance = object.material_allowance
        self.keep_tool_down_if_poss = object.keep_tool_down_if_poss
        self.use_zig_zag = object.use_zig_zag
        self.zig_angle = object.zig_angle
        self.zig_unidirectional = object.zig_unidirectional
        self.entry_move = object.entry_move
            
    def GetProperties(self):
        properties = []

        properties.append(PyPropertyLength("Step Over", 'step_over', self))
        properties.append(PyPropertyLength("Material Allowance", 'material_allowance', self))
        properties.append(PyChoiceProperty("Cut Mode", 'cut_mode', ['Conventional', 'Climb'], self))
        properties.append(PyChoiceProperty("Starting Place", 'from_center', ['Conventional', 'Climb'], self))
        properties.append(PyChoiceProperty("Entry Move", 'entry_move', ['Plunge', 'Ramp', 'Helical'], self, [0,1,2]))
        properties.append(PyProperty("Keep Tool Down", 'keep_tool_down_if_poss', self))
        properties.append(PyProperty("Use Zig Zag", 'use_zig_zag', self))
        properties.append(PyProperty("Zig Angle", 'zig_angle', self))
        properties.append(PyProperty("Unidirectional", 'zig_unidirectional', self))
        
        properties += SketchOp.GetProperties(self)

        return properties
    
    def DoGCodeCallsForSketch(self, sketch, data):
        cut_mode, depth_params, tool_diameter = data
        
        a = sketch.GetArea()
        
        area_funcs.pocket(a, tool_diameter/2, self.material_allowance/wx.GetApp().program.units, self.step_over/wx.GetApp().program.units, depth_params, self.from_center != 0, self.keep_tool_down_if_poss, self.use_zig_zag, self.zig_angle)
        
        rapid(z = self.clearance_height)
        
    
    def DoGCodeCalls(self):
        tool = Tool.FindTool(self.tool_number)
        if tool == None:
            wx.MessageBox('Cannot generate G-Code for profile without a tool assigned')
            return
        
        depth_params = self.GetDepthParams()
        tool_diameter = tool.CuttingRadius(True) * 2.0
        SpeedOp.DoGCodeCalls(self)
        
        self.DoEachSketch(self.DoGCodeCallsForSketch, (self.cut_mode, depth_params, tool_diameter))


