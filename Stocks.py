from CamObject import CamObject

type = 0

class Stocks(CamObject):
    def __init__(self):
        CamObject.__init__(self)
        
    def GetType(self):
        return type
    
    def TypeName(self):
        return "Stocks"
    
    def icon(self):
        # the name of the PNG file in the HeeksCNC icons folder
        return "stocks"
    
    def CanBeDeleted(self):
        return False
        
    def OneOfAKind(self):
        return True
        
    def MakeACopy(self):
        object = Stocks()
        object.CopyFrom(self)
        return object
