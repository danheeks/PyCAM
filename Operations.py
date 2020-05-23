from CamObject import CamObject
from Profile import Profile
from Pocket import Pocket

type = 0

class Operations(CamObject):
    def __init__(self):
        CamObject.__init__(self)
        
    def TypeName(self):
        return "Operations"
    
    def GetType(self):
        return type
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "operations"
    
    def UsesID(self):
        return False
    
    def CanBeDeleted(self):
        return False
    
    def AutoExpand(self):
        return True
        
    def OneOfAKind(self):
        return True
        
    def MakeACopy(self):
        object = Operations()
        object.CopyFrom(self)
        return object
