from Tool import Tool
from consts import *
import cad
from CamObject import CamObject
import wx

type = 0

class Tools(CamObject):
    def __init__(self):
        CamObject.__init__(self)
        
    def TypeName(self):
        return "Tools"
    
    def GetType(self):
        return type
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "tools"
    
    def CanBeDeleted(self):
        return False
        
    def OneOfAKind(self):
        return True
    
    def UsesID(self):
        return False
    
    def AddToPopupMenu(self, menu):
        menu.AddItem("save as default tools", self.OnSaveDefault)
        
    def OnSaveDefault(self):
        self.save_default()
        
    def save_default(self):
        import pickle
        f = open(wx.GetApp().cam_dir + "/default_tools.txt", "wb")
        for tool in self.children:
            pickle.dump(tool, f)
        f.close()        

    def load_default(self):
        self.Clear()
        
        try:
            cad.OpenXmlFile(wx.GetApp().cam_dir + "/default.tooltable", self)
        except:
            # no default file found, add 2 tools
            cad.AddUndoably(Tool(diameter = 3.0, type = TOOL_TYPE_SLOTCUTTER, tool_number = 1), self, None)
            cad.AddUndoably(Tool(diameter = 6.0, type = TOOL_TYPE_SLOTCUTTER, tool_number = 2), self, None)
            return
        
    def MakeACopy(self):
        object = Tools()
        object.CopyFrom(self)
        return object
    
    def CallsObjListReadXml(self):
        return True
        
    def FindAllTools(self):
        tools = []
        tools.append( (0, "No tool") )
        for child in self.children:
            tools.append( (child.tool_number, child.name()) )
        return tools
    
    def FindFirstTool(self, type):
        for child in self.GetChildren():
            if child.type == type:
                return child
        return None                
        
    def FindTool(self, tool_number):
        for child in self.children:
            if child.tool_number == tool_number:
                return child
        return None
        