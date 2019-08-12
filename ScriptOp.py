from Operation import Operation
import cad
from nc.nc import *
from Object import PyProperty

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
        Operation.CopyFrom(self, object)
        self.str = object.str
            
    def GetProperties(self):
        properties = []
        properties.append(PyProperty('Script', 'str', self))
        properties[-1].type = cad.PROPERTY_TYPE_LONG_STRING
        properties += Operation.GetProperties(self)
        return properties
    
    def DoGCodeCalls(self):
        exec(self.str, globals())

class PyMultiLineProperty(PyProperty):
    def __init__(self, title, value_name, object, num_lines, recalculate = None):
        PyProperty.__init__(self, title, value_name, object, recalculate)
        self.number_of_lines = number_of_lines
        
    def GetNumberOfLines(self):
        return self.number_of_lines
        
        
        
        