from DepthOp import DepthOp
import cad
from Object import PyProperty

class SketchOp(DepthOp):
    def __init__(self, sketch, tool_number = -1, operation_type = cad.OBJECT_TYPE_UNKNOWN):
        DepthOp.__init__(self, tool_number, operation_type)
        self.sketch = sketch
        
    def CopyFrom(self, object):
        DepthOp.CopyFrom(self, object)
        self.sketch = object.sketch
        
    def ReadXml(self):
        self.sketch = cad.GetXmlInt('sketch')        
        DepthOp.ReadXml(self)

    def GetProperties(self):
        properties = []

        properties.append(PyProperty("Sketch", 'sketch', self))
        
        properties += DepthOp.GetProperties(self)

        return properties
    
