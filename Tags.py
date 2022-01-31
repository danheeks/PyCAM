from CamObject import CamObject

type = 0

class Tags(CamObject):
    def __init__(self):
        CamObject.__init__(self)
        
    def GetType(self):
        return type
    
    def TypeName(self):
        return "Tags"
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "tags"
    
    def UsesID(self):
        return False
    
    def CanBeDeleted(self):
        return False
    
    def MakeACopy(self):
        copy = Tags()
        copy.CopyFrom(self)
        return copy
    
    def CallsObjListReadXml(self):
        return True
