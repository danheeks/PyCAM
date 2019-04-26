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
