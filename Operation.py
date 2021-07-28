from CamObject import CamObject
from consts import *
from HeeksConfig import HeeksConfig
import cad
import wx
from Object import PyProperty
from Object import PyPropertyLength
from Object import PyChoiceProperty
import Tool

class PyToolProperty(PyChoiceProperty):
    def __init__(self, op):
        # a choice property which lets you choose a drop-down of tool names and updates the op's tool_number attribute
        choices = ['None']
        alternative_values = [0]
        obj_list = wx.GetApp().program.tools
        if obj_list != None:
            obj = obj_list.GetFirstChild()
            while obj:
                if obj.GetIDGroupType() == Tool.type:
                    choices.append(obj.GetTitle())
                    alternative_values.append(obj.tool_number)
                obj = obj_list.GetNextChild()
        
        PyChoiceProperty.__init__(self, 'Tool', 'tool_number', choices, op, alternative_values)


class Operation(CamObject):
    def __init__(self):
        CamObject.__init__(self, id_named = True)
        self.active = True
        self.comment = ''
        self.tool_number = 0
        self.pattern = 1
        self.surface = 0
        
    def TypeName(self):
        return "Operation"
        
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        if self.active:
            return self.op_icon()
        else:
            return "noentry"
            
    def CanBeDeleted(self):
        return True
    
    def UsesTool(self): # some operations don't use the tool number
        return True
    
    def ReadDefaultValues(self):
        config = HeeksConfig()
        self.tool_number = config.ReadInt("Tool", 0)
        self.pattern = config.ReadInt("Pattern", 0)
        self.surface = config.ReadInt("Surface", 0)

    def WriteDefaultValues(self):
        config = HeeksConfig()
        config.WriteInt("Tool", self.tool_number)
        config.WriteInt("Pattern", self.pattern)
        config.WriteInt("Surface", self.surface)
        
    def DoGCodeCalls(self):
        if len(self.comment) > 0:
            comment(self.comment)        

        if self.UsesTool():
            wx.GetApp().SetTool(self.tool_number) # Select the correct  tool.
           
    def CopyFrom(self, object):
        CamObject.CopyFrom(self, object)
        self.active = object.active
        self.comment = object.comment
        self.tool_number = object.tool_number
        self.pattern = object.pattern
        self.surface = object.surface
        
    def WriteXml(self):
        if len(self.comment) > 0: cad.SetXmlValue('comment', self.comment)
        cad.SetXmlValue('active', self.active)
        cad.SetXmlValue('tool_number', self.tool_number)
        cad.SetXmlValue('pattern', self.pattern)
        cad.SetXmlValue('surface', self.surface)
        CamObject.WriteXml(self)
        
    def ReadXml(self):
        self.comment = cad.GetXmlValue('comment', self.comment)
        self.active = cad.GetXmlBool('active', self.active)
        self.tool_number = cad.GetXmlInt('tool_number', self.tool_number)
        self.pattern = cad.GetXmlInt('pattern', self.pattern)
        self.surface = cad.GetXmlInt('surface', self.surface)
        CamObject.ReadXml(self)
            
    def GetProperties(self):
        properties = []

        properties.append(PyProperty("Comment", 'comment', self))
        properties.append(PyProperty("Active", 'active', self))
        properties.append(PyToolProperty(self))
        properties.append(PyProperty("Pattern", 'pattern', self))
        properties.append(PyProperty("Surface", 'surface', self))
        
        properties += CamObject.GetProperties(self)

        return properties
    
    def CheckToolExists(self):
        # returns failure message or None for success
        if self.tool_number == 0:
            return 'No tool defined for operation!'
        tool = Tool.FindTool(self.tool_number)
        if tool == None:
            return 'Tool number ' + str(self.tool_number) + ' does not exist'
