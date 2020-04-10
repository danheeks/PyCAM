from CamObject import CamObject
import geom

type = 0

class Stock(CamObject):
    def __init__(self):
        CamObject.__init__(self)
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
