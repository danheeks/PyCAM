from Operation import Operation
import cad
from nc.nc import *

type = 0

class ScriptOp(Operation):
    def __init__(self, tool_number = -1, operation_type = cad.OBJECT_TYPE_UNKNOWN):
        Operation.__init__(self, tool_number, operation_type)
        self.str = ''
        self.ReadDefaultValues()
        
    def WriteXml(self):
        cad.SetXmlValue('script', self.str)
        Operation.WriteXml(self)
        
    def ReadXml(self):
        self.str = cad.GetXmlValue('script')
        Operation.ReadXml(self)
        
    def TypeName(self):
        return "ScriptOp"

    def GetType(self):
        return type
    
    def op_icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "scriptop"
    
    def HasEdit(self):
        return True
        
    def Edit(self):
        import ScriptOpDlg
        res =  ScriptOpDlg.Do(self)
        return res
        
    def MakeACopy(self):
        copy = ScriptOp()
        copy.CopyFrom(self)
        return copy
    
    def CopyFrom(self, object):
        pass
#        Operation.CopyFrom(self, object)
#        print('ScirptOp CopyFrom str = ' + self.str + ', object.str = ' + object.str)
#        self.str = object.str
            
    def GetProperties(self):
        properties = []
        properties += Operation.GetProperties(self)
        return properties
    
    def DoGCodeCalls(self):
        exec(self.str, globals())
