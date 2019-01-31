from CamObject import CamObject
from consts import *
from CNCConfig import CNCConfig
import cad

class Operation(CamObject):
    def __init__(self, tool_number = -1, operation_type = cad.OBJECT_TYPE_UNKNOWN):
        CamObject.__init__(self)
        self.active = True
        self.comment = ''
        self.title = self.TypeName()
        self.tool_number = tool_number
        self.operation_type = operation_type
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
        config = CNCConfig()
        
        self.tool_number = config.ReadInt("OpTool", 0)
        
        if self.tool_number != 0:
            default_tool = wx.GetApp().program.tools.FindTool(self.tool_number)
            if default_tool == None:
                self.tool_number = 0
            else:
                self.tool_number = default_tool.tool_number
        
        if self.tool_number == 0:
            first_tool = wx.GetApp().program.tools.FindFirstTool(TOOL_TYPE_SLOTCUTTER)
            if first_tool:
                self.tool_number = first_tool.tool_number
            else:
                first_tool = wx.GetApp().program.tools.FindFirstTool(TOOL_TYPE_ENDMILL)
                if first_tool:
                    self.tool_number = first_tool.tool_number
                else:
                    first_tool = wx.GetApp().program.tools.FindFirstTool(TOOL_TYPE_BALLENDMILL)
                    if first_tool:
                        self.tool_number = first_tool.tool_number

    def WriteDefaultValues(self):
        config = CNCConfig()
        if self.tool_number != 0:
            config.WriteInt("OpTool", self.tool_number)
        
    def AppendTextToProgram(self):
        if len(self.comment) > 0:
            wx.GetApp().program.python_program += "comment(" + self.comment + ")\n"        

        if self.UsesTool():
            wx.GetApp().machine_state.AppendToolChangeText(self.tool_number) # Select the correct  tool.
           
    def CopyFrom(self, object):
        self.active = object.active
        self.comment = object.comment
        self.title = object.title
        self.tool_number = object.tool_number
        self.operation_type = object.operation_type
        self.pattern = object.pattern
        self.surface = object.surface
