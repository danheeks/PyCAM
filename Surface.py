from CamObject import CamObject

type = 0

class Surface(CamObject):
    def __init__(self):
        CamObject.__init__(self)
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
        CamObject.CopyFrom(self, object)
        self.solids = []
        self.solids += object.solids
        
    def GetBox(self):
        box = geom.Box3D()
        # return the box around all the solids
        for solid in self.solids:
            object = cad.GetObjectFromId(cad.OBJECT_TYPE_STL_SOLID, solid)
            if object:
                object.GetBox(box)
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
