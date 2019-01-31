from DepthOp import DepthOp
import cad

class SketchOp(DepthOp):
    def __init__(self, sketch, tool_number = -1, operation_type = cad.OBJECT_TYPE_UNKNOWN):
        DepthOp.__init__(self, tool_number, operation_type)
        self.sketch = sketch
        
    def CopyFrom(self, object):
        DepthOp.CopyFrom(self, object)
        self.sketch = object.sketch
