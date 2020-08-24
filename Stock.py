from CamObject import CamObject
import geom
import cad

type = 0

class Stock(CamObject):
    def __init__(self):
        CamObject.__init__(self, id_named = True)
        self.solids = []
        
    def GetType(self):
        return type
    
    def TypeName(self):
        return "Stock"
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "stock"
    
    def HasEdit(self):
        return True
    
    def Edit(self):
        import StockDlg
        return StockDlg.Do(self)
        
    def MakeACopy(self):
        copy = Stock()
        copy.CopyFrom(self)
        return copy
    
    def CopyFrom(self, object):
        CamObject.CopyFrom(self, object)
        self.solids = []
        self.solids += object.solids
        
    def GetBox(self):
        self.box = geom.Box3D()
        # return the box around all the solids
        for solid in self.solids:
            object = cad.GetObjectFromId(cad.OBJECT_TYPE_STL_SOLID, solid)
            if object:
                if object.GetVisible():
                    self.box.InsertBox(object.GetBox())
        return self.box
    
    def GetBoxWithInvisibles(self):            
        self.box = geom.Box3D()
        # return the box around all the solids
        for solid in self.solids:
            object = cad.GetObjectFromId(cad.OBJECT_TYPE_STL_SOLID, solid)
            if object:
                self.box.InsertBox(object.GetBox())
        return self.box
        
    def WriteXml(self):
        for solid in self.solids:
            cad.BeginXmlChild('solid')
            cad.SetXmlValue('id', solid)
            cad.EndXmlChild()
        CamObject.WriteXml(self)
        
    def ReadXml(self):
        child_element = cad.GetFirstXmlChild()
        while child_element != None:
            if child_element == 'solid':
                solid = cad.GetXmlInt('id')
                self.solids.append(solid)
            child_element = cad.GetNextXmlChild()
        CamObject.ReadXml(self)
