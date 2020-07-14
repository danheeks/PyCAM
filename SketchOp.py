from DepthOp import DepthOp
import cad
from Object import PyProperty

class SketchOp(DepthOp):
    def __init__(self, sketch):
        DepthOp.__init__(self)
        self.sketch = sketch
        
    def CopyFrom(self, object):
        DepthOp.CopyFrom(self, object)
        self.sketch = object.sketch
        
    def WriteXml(self):
        cad.SetXmlValue('sketch', self.sketch)
        DepthOp.WriteXml(self)
        
    def ReadXml(self):
        self.sketch = cad.GetXmlInt('sketch')      
        DepthOp.ReadXml(self)

    def GetProperties(self):
        properties = []

        properties.append(PyProperty("Sketch", 'sketch', self))
        
        properties += DepthOp.GetProperties(self)

        return properties
    
    def DoEachSketch(self, callback, data):
        # data is a tuple, whatever you want to pass on
        # callback gets called for each separate sketch
              
        object = cad.GetObjectFromId(cad.OBJECT_TYPE_SKETCH, self.sketch)
        
        if object != None:
            if object.GetType() == cad.OBJECT_TYPE_SKETCH:
                re_ordered_sketch = None
                sketch_order = object.GetSketchOrder()
                if sketch_order == cad.SketchOrderType.SketchOrderTypeBad:
                    re_ordered_sketch = object.MakeACopy()
                    re_ordered_sketch.ReOrderSketch(cad.SketchOrderType.SketchOrderTypeReOrder)
                    object = re_ordered_sketch
                    sketch_order = object.GetSketchOrder()
                if (sketch_order == cad.SketchOrderType.SketchOrderTypeMultipleCurves) or (sketch_order == cad.SketchOrderType.SketchOrderHasCircles):
                    new_separate_sketches = object.Split()
                    for one_curve_sketch in new_separate_sketches:
                        callback(one_curve_sketch, data)
                else:
                    callback(object, data)

    
