from CamObject import CamObject
import geom
from HeeksConfig import HeeksConfig
import cad
from Object import PyProperty
from Object import PyPropertyLength

type = 0

class Tag(CamObject):
    def __init__(self):
        CamObject.__init__(self)
        self.pos = geom.Point(0,0)
        self.ReadDefaultValues()
        
    def GetType(self):
        return type
    
    def TypeName(self):
        return "Tag"
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "tag"
        
    def MakeACopy(self):
        copy = Tag()
        copy.CopyFrom(self)
        return copy
        
    def CopyFrom(self, object):
        CamObject.CopyFrom(self, object)
        self.pos = object.pos
        self.width = object.width
        self.angle = object.angle
        self.height = object.height

    def WriteXml(self):
        cad.SetXmlValue('x', self.pos.x)
        cad.SetXmlValue('y', self.pos.y)
        cad.SetXmlValue('width', self.width)
        cad.SetXmlValue('angle', self.angle)
        cad.SetXmlValue('height', self.height)
        CamObject.WriteXml(self)
        
    def ReadXml(self):
        self.pos.x = cad.GetXmlFloat('x', self.pos.x)
        self.pos.y = cad.GetXmlFloat('y', self.pos.y)
        self.width = cad.GetXmlFloat('width', self.width)
        self.angle = cad.GetXmlFloat('angle', self.angle)
        self.height = cad.GetXmlFloat('height', self.height)
        CamObject.ReadXml(self)
        
    def ReadDefaultValues(self):
        config = HeeksConfig()
        self.width = config.ReadFloat("Width", 10.0)
        self.angle = config.ReadFloat("Angle", 45.0)
        self.height = config.ReadFloat("Height", 4.0)
        
    def WriteDefaultValues(self):
        config = HeeksConfig()
        config.WriteFloat("Width", self.width)
        config.WriteFloat("Angle", self.angle)
        config.WriteFloat("Height", self.height)
    
    def GetProperties(self):
        properties = []

        properties.append(PyProperty("Position", 'pos', self))
        properties.append(PyPropertyLength("Width", 'width', self))
        properties.append(PyProperty("Angle", 'angle', self))
        properties.append(PyPropertyLength("Height", 'height', self))
        
        properties += CamObject.GetProperties(self)

        return properties
        
    def OnRenderTriangles(self):
        cad.DrawColor(cad.Color(0,0,0))
        cad.DrawSymbol(1, self.pos.x, self.pos.y, 0.0)
        cad.DrawColor(cad.Color(0,0,255))
        cad.DrawSymbol(0, self.pos.x, self.pos.y, 0.0)
    
