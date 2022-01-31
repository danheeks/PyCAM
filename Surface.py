from CamObject import CamObject
import cad
import geom
import Surfaces
import wx
from HeeksConfig import HeeksConfig

type = 0

class Surface(CamObject):
    def __init__(self):
        CamObject.__init__(self, id_named = True)
        self.solids = []
        self.tolerance = 0.0
        self.material_allowance = 0.0
        self.same_for_each_pattern_position = True
        
    def GetType(self):
        return type
    
    def TypeName(self):
        return "Surface"
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "surface"
    
    def HasEdit(self):
        return True
    
    def Edit(self):
        import SurfaceDlg
        return SurfaceDlg.Do(self)
        
    def MakeACopy(self):
        copy = Surface()
        copy.CopyFrom(self)
        return copy
    
    def CopyFrom(self, object):
        self.tolerance = object.tolerance
        self.material_allowance = object.material_allowance
        self.same_for_each_pattern_position = object.same_for_each_pattern_position
        self.solids = []
        self.solids += object.solids
        CamObject.CopyFrom(self, object)
        
    def CanAddTo(self, owner):
        return owner.GetType() == Surfaces.type
    
    def PreferredPasteTarget(self):
        return wx.GetApp().program.surfaces
        
    def GetBox(self):
        box = geom.Box3D()
        # return the box around all the solids
        for solid in self.solids:
            object = cad.GetObjectFromId(cad.OBJECT_TYPE_STL_SOLID, solid)
            if object:
                box.InsertBox(object.GetBox())
        return box            
        
    def WriteXml(self):
        cad.SetXmlValue('tolerance', self.tolerance)
        cad.SetXmlValue('material_allowance', self.material_allowance)
        cad.SetXmlValue('same_for_posns', self.same_for_each_pattern_position)
        
        for solid in self.solids:
            cad.BeginXmlChild('solid')
            cad.SetXmlValue('id', solid)
            cad.EndXmlChild()
        
        CamObject.WriteXml(self)
        
    def ReadXml(self):
        self.tolerance = cad.GetXmlFloat('tolerance', self.tolerance)
        self.material_allowance = cad.GetXmlFloat('material_allowance', self.material_allowance)
        self.same_for_each_pattern_position = cad.GetXmlBool('same_for_posns', self.same_for_each_pattern_position)
        
        child_element = cad.GetFirstXmlChild()
        while child_element != None:
            if child_element == 'solid':
                solid = cad.GetXmlInt('id')
                self.solids.append(solid)
            child_element = cad.GetNextXmlChild()
        CamObject.ReadXml(self)
        
    def ReadDefaultValues(self):
        config = HeeksConfig()
        self.tolerance = config.ReadFloat("SurfTol", 0.01)
        self.material_allowance = config.ReadFloat("MatAllow", 0)
        self.same_for_each_pattern_position = config.ReadBool("SameForEach", True)

    def WriteDefaultValues(self):
        config = HeeksConfig()
        config.WriteFloat("SurfTol", self.tolerance)
        config.WriteFloat("MatAllow", self.material_allowance)
        config.WriteBool("SameForEach", self.same_for_each_pattern_position)
